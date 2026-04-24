---
title: "Handling LTI Launches in Rails"
pubDate: "2024-05-05T13:26:00.000Z"
description: "Learn how to set up your Rails application as an LTI Tool Provider, to handle LTI 1.3 launches from an LMS, including the OCID workflow, user authentication and what to do with the information you get from the LMS."
slug: "handling-lti-launches-in-rails"
status: "published"
heroImage: "vhs-1.jpeg"
tags:
  - "application design"
  - "edtech"
  - "lti"
  - "rails"
---

This article explains how to set up your Rails application as an _LTI Tool Provider_, to handle LTI 1.3 launches from an LMS, including the OCID workflow, user authentication and what to do with the information you get from the LMS.

---

_This is part 2 of a 3-part series on LTI Launches. Check out the other articles:_

- What’s in a Canvas LMS LTI 1.3 JWT?
- Building an LTI DeepLinking Response in Rails

---

If you're reading this, you probably already know what LTI is. If not, the short answer is that it's a standard for embedding external tools into a LMS. Here's the [Wikipedia article](https://en.wikipedia.org/wiki/Learning_Tools_Interoperability).

For these examples, I'm using [Canvas](https://www.instructure.com/canvas) LMS, so the implementation details will be specific to Canvas. Because LTI is a standard, most of the details should be the same across platforms, but the specifics around configuring the LMS and some of the terminology may differ. I've only tested the approach with Canvas.

The first part of this article will discuss handling an LTI launch and authenticating the user who initiated the launch. A future article will cover how to do a _LtiDeepLinkingResponse_, which allows us to return rich content to be embedded in the LMS.

Let's travel through the exciting world of LTI, OIDC, JWTs, JWKs and more.

## Overview

In this guide, _Tool Provider_ refers to the application that we're building.

LTI 1.3 uses OpenID Connect ([OIDC) third-party flow](https://www.imsglobal.org/spec/security/v1p0/#openid_connect_launch_flow). I won't go into great detail, but at a very high level:

1. The LMS initiates a POST request to the Tool Provider, to the URL that we provide when we configure the tool in the LMS.
2. The Tool Provider redirects the browser back to the LMS, to an "authorization endpoint" provided by the LMS. This request requires a crafted URL parameter derived from the original request.
3. The LMS redirects back to the Tool Provider, to a different URL specified in the LMS tool config. This request contains an "ID token" and a signed JWT containing a LTI payload.
4. Finally, the Tool Provider can validate the response, authenticate the user and direct the browser to the appropriate resource.

Let's dig in.

## Step 1: Login Initiation

Your application will need to respond to a number of requests specific to the OIDC launch process, the first of which is the _Login Initiation_. Let's create a controller to handle the OIDC launch, and our first route. All you RESTful routes purists, avert your eyes.

```ruby
post "/oidc/initiation", to: "oidc#initiation"

```

config/routes.rb

````ruby
class OIDCController
app/controllers/oidc_controller.rb

The URL for this route is what we will supply in our Developer Key "OpenID Connect Initiation URL" field.

## Step 2: Redirect to Authentication Endpoint

We now need to craft the redirect back to the LMS. We use a number of parameters from the original request as well as the redirect URL supplied by the LMS out-of-band. We will also use the [openid_connect gem](https://github.com/nov/openid_connect) to do a bit of the magic for us. Let's create a PORO model to handle the logic of building the URL.

```ruby
class OIDCAuthorizationUri
  def initialize(state:, nonce:, login_hint:, lti_message_hint:, tool_id:, redirect_host:)
    @state = state
    @nonce = nonce
    @login_hint = login_hint
    @lti_message_hint = lti_message_hint
    @tool_id = tool_id
    @redirect_host = redirect_host
  end

  def to_s
    client.authorization_uri(
      state: @state,
      nonce: @nonce,
      login_hint: @login_hint,
      lti_message_hint: @lti_message_hint,
      prompt: "none",
      response_mode: "form_post"
    )
  end

  private

  def client
    @client ||= OpenIDConnect::Client.new(
      identifier: @tool_id,
      redirect_uri: "https://#{@redirect_host}/oidc/callback",
      host: config[:oidc_auth_host],
      authorization_endpoint: config[:oidc_auth_path]
    )
  end

  def config
    # This part is up to you. These values are supplied by the LMS
    # For Canvas in production the values are
    # host: "sso.canvas.instructure.com"
    # path: "/api/lti/authorize_redirect"
    {
      oidc_auth_host: "",
      oidc_auth_path: ""
    }
  end
end

````

app/models/oidc_authorization_url.rb

Let's also add some inflections for all of the initialisms we're working with.

```ruby
ActiveSupport::Inflector.inflections(:en) do |inflect|
  inflect.acronym "LTI"
  inflect.acronym "OIDC"
end

```

config/initializers/inflections.rb

In the OIDC controller, we can create a new `OIDCAuthorizationURL` and redirect to it. We create a few session variables to help validate the response in the next step.

```ruby
def initiation
  set_session_params
  redirect_to auth_uri.to_s, allow_other_host: true
end

private

def set_session_params
  session[:state] = SecureRandom.hex(16)
  session[:nonce] = SecureRandom.hex(16)
end

def auth_uri
  @auth_uri ||= OIDCAuthorizationUri.new(
    state: session[:state],
    nonce: session[:nonce],
    login_hint: params[:login_hint],
    lti_message_hint: params[:lti_message_hint],
    tool_id: params[:client_id],
    issuer: params[:iss],
    redirect_host: request.hostname
  )
end

```

app/controllers/oidc_controller.rb

## Step 3: Authentication Response

The LMS now bounces back to a _different_ URL on our Tool Provider, specified in the "Redirect URIs" section of the Developer Key config.

It sends along a [JWT](https://jwt.io/introduction/) with a lot of useful information. I wrote [an article](https://cbennell.ocaduwebspace.ca/67/whats-in-a-canvas-lms-lti-1-3-jwt/) exploring the contents of the JWT. We will deal with that in the next step.

Let's add the route and controller action to handle the authentication response.

```ruby
post "/oidc/callback", to: "oidc#callback"

```

config/routes.rb

````ruby
class OIDCController
app/controllers/oidc_controller.rb

The response contains a signed JWT in the `id_token` param. This JWT is [chock full of details](https://cbennell.ocaduwebspace.ca/67/whats-in-a-canvas-lms-lti-1-3-jwt/) about the LTI Launch, the launch context (like the course in which the tool was embedded) the user and LMS platform itself.

## Step 4: Validate & Authenticate

We have a few hoops to jump through in this step:

1. Decode the JWT response from the LMS
2. Validate the JWT
3. Pull some useful information from the JWT which we can use to authenticate the user
4. Redirect to our content

Next, we decode the JWT. For that we will need the [public JWKs](https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html#config-in-tool) provided by the LMS. We will also leverage the gem [json-jwt](https://github.com/nov/json-jwt) to do the heavy lifting. Let's build a model to encapsulate that behaviour. This will handle fetching the public JWKs that are used to validate the token, and decoding the value into something useful.

```ruby
class JWTContent
  def initialize(id_token_string)
    @id_token_string = id_token_string
  end

  def id_token
    @id_token ||= JSON::JWT.decode(@id_token_string, jwk_set)
  end

  private

  def jwk_set
    @jwk_set ||= JSON::JWK::Set.new(
      jwk_uris
        .filter_map { |jwk_uri| fetch_jwk(jwk_uri) }
        .reduce(:|)
    )
  end

  def fetch_jwk(uri)
    JSON::JWK::Set::Fetcher.fetch(
      uri,
      kid: nil,
      auto_detect: false
    )
  end

  def config
    {
      jwk_uris: [] # Provide these
    }
  end
end

````

app/models/jwt_content.rb

### Verify the Token

We also need to perform some verification on the token. The full verification requirements are explained in the [LTI Security Framework](https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation). We add a `#verify` method to the JWTContent class.

```ruby
class JWTContent
  def verify(lms_platform_id:, tool_client_id:, nonce:)
    azp_valid = id_token[:azp] ? (id_token[:azp] == tool_client_id) : true
    unless azp_valid &&
        id_token[:sub].present? &&
        id_token[:iss] == lms_platform_id &&
        id_token[:aud] == tool_client_id &&
        id_token[:nonce] == nonce &&
        OauthNonce.validate(nonce, tool_client_id) &&
        Time.at(id_token[:iat]).between?(30.seconds.ago, Time.now) &&
        Time.at(id_token[:exp]) > Time.now

      raise "ID Token Verification Failed!"
    end
  end
end

```

app/model/jwt_content.rb

We store and check nonces to prevent replay attacks; here's a simple model to save them in the database. If your application has a cache store, use it instead.

````ruby
class OauthNonce
app/models/oauth_nonce.rb

```ruby
class CreateOauthNonces
db/migrate/...create_oauth_nonces.rb

### Dealing With the Token Contents

Calling `JWTContent.new(jwt).id_token` will return an hash-like containing fields such as:

```ruby
{
  "https://purl.imsglobal.org/spec/lti/claim/version"=>"1.3.0",
  "azp"=>"163950000000000106",
  "exp"=>1714746467,
  "iat"=>1714742867,
  "nonce"=>"0c369dfd1d51c28dc4dd47d3ba164823",
  "https://purl.imsglobal.org/spec/lti/claim/custom"=>{...}
  ...
}

````

We can wrap this content another model to encapsulate the access details.

```ruby
module LTI
  class LaunchContext
    def self.build(payload)
      new(
          message_type: claim_value("message_type", payload),
          lti_version: claim_value("lti_version", payload),
          deployment_id: claim_value("deployment_id", payload),
          target_link_uri: claim_value("target_link_uri", payload),
          custom: claim_value("custom", payload),
          return_url: claim_value("launch_presentation", payload)["return_url"],
          deep_link_return_url: payload["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["deep_link_return_url"],
          aud: payload["aud"],
          azp: payload["azp"],
          iss: payload["iss"],
          sub: payload["sub"]
         )
    end

    def self.claim_value(claim, payload)
      payload["https://purl.imsglobal.org/spec/lti/claim/#{claim}"]
    end

    def initialize(*params)
      # ... set your instance variables
    end

    def user_sis_id
      custom["user_sis_id"]
    end

    def course_sis_id
      custom["course_sis_id"]
    end
  end
end

```

app/models/lti/launch_context.rb

(This example assumes [custom variables](https://canvas.instructure.com/doc/api/file.tools_variable_substitutions.html) configured on the Developer Key)

Developer Key Custom Fields

```
user_sis_id=$Canvas.user.sisSourceId
course_sis_id=$Canvas.course.sisSourceId

```

There's a lot of info in the JWT. You can extract it all into the LaunchContext object, or only extract the specific fields you need. In this case, I'm extracting details needed for a DeepLinking response. (I'm also turning this model into an ActiveRecord, more on that in a future article)

In our controller, we can use the LaunchContext to get the info we actually want. We create a JWTContent instance to decode the JWT passed from the LMS, and pass _that_ into the LTI::LaunchContext.

````ruby
class OIDCController
app/controllers/oidc_controller.rb

Now all that's left is to authenticate the user and redirect.

```ruby
class OIDCController
app/controllers/oidc_controller.rb

## Conclusion

There you have it, a complete LTI 1.3 Launch. Stay tuned for a future articles, where we delve into more the DeepLinking launch and response.

## References

- Canvas LMS API Docs - Manually Configuring LTI Advantage Tools
- 1EdTech LTI Security Framework
- 1EdTech LTI Core
- openid_connect gem
- json-jwt gem
- Verifying Signed JWTs (JWS) with Ruby
- OneLogin OpenId Connect Ruby Samples
````
