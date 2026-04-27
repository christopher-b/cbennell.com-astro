---
title: "What's in a Canvas LMS LTI 1.3 JWT?"
pubDate: "2024-05-04T04:00:00.000Z"
description: "What’s inside an LTI 1.3 JWT? This post walks through a Canvas launch token claim by claim, so you can decode and understand the data your Rails app receives."
slug: "whats-in-a-canvas-lms-lti-1-3-jwt"
status: "published"
section: "post"
heroImage: "glitch-vert.jpeg"
tags:
  - "edtech"
  - "lti"
---

As a precursor to more in-depth articles about handling LTI 1.3 launches ([here](https://cbennell.com/posts/handling-lti-launches-in-rails/) and [here](https://cbennell.com/posts/building-an-lti-deeplinking-response-in-rails/)) in Ruby on Rails, I wanted to explore the contents of an LTI JWT. Receiving and decoding the JWT is part of step three of the four-step process of handling an LTI launch. My other article will cover those steps in more detail (although most of the work is being done by the [json-jwt](https://github.com/nov/json-jwt) gem).

---

_This is part 1 of a 3-part series on LTI Launches. Check out the other articles:_

- [Handling LTI Launches in Rails](/posts/handling-lti-launches-in-rails/)
- [Building an LTI DeepLinking Response in Rails](/posts/building-an-lti-deeplinking-response-in-rails/)

---

A JSON Web Token is a chunk of JSON that has been **signed** and **encrypted**. **Signed** means that we can trust the token content, and **encrypted** means that no one else can read it. JWTs allow applications to securely pass around data, structured as JSON objects. The [LTI Security Framework](https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation) specifies using OIDC + JWTs as one possible pattern for secure communication.

The examples I'm using here are from Canvas LMS, with a request configured to expect an `LTIDeepLinkingResponse`. Other types of requests will add additional details to the JWT. A Canvas LTI JWT looks somthing like this:

```JSON
{
  "https://purl.imsglobal.org/spec/lti/claim/message_type"=>"LtiDeepLinkingRequest",
  "https://purl.imsglobal.org/spec/lti/claim/version"=>"1.3.0",
  "https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"=> {
    "aud"=>"999990000000000101",
    "azp"=>"999990000000000101",
    "https://purl.imsglobal.org/spec/lti/claim/deployment_id"=>"372:...",
    "exp"=>1656791270,
    "iat"=>1656787670,
    "iss"=>"https://canvas.instructure.com",
    "nonce"=>"...",
    "sub"=>"...",
    ...and so on
  }
}
```

At a high level, the JWT contains a few different types of information:

1. Information about the request itself.
2. Information about the request context.
3. Information about the host platform.
4. Information about the user.
5. Information about the expected response.
6. Custom information the LMS has been configured to send.

The decoded JWT contains a JSON hash of values. A few of the low-level items have three-letter keys. The rest are the LTI _claims_, which include a long URL ending in the claim name. For example:

```JSON
"https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0"

```

When discussing these below, I won't list the whole URI, just the claim name. There are a few exceptions to this pattern, which I will note where relevant.

## Request Information

These are mostly the _registered claims_, meaning that they are part of the JWT spec, and form part of the security framework. These are specified in [IEFT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519#section-4.1). Canvas sends the following:

### aud: Audience

```JSON
"aud": "199990000000000101"

```

This represents the intended recipient of the message. In Canvas, this is a combination of your account ID and the Developer Key ID. This can potentially be an array, in which case the tool should reject the token if `aud` contains un-trusted audiences.

### azp: Authorized Party

```JSON
"azp": "199990000000000101"

```

Defined by OIDC Core. Contains the OAuth 2.0 Client ID of Tool Provide which is... the same as the `aud` claim. This field is used as part of the [official response validation process](https://www.imsglobal.org/spec/security/v1p0/#authentication-response-validation): if `aud` contains multiple values, the Tool Provider should ensure that `azp` is present, and that is contains the Tool Provider's OAuth client ID.

### exp: Expiry Time

```JSON
"exp": "1714746467"

```

A deadline for processing the request. The request is not to be accepted if the current date is after this timestamp. Expressed in epoch time. Canvas gives you a generous one hour before the request expires.

### iat: Issued At

```JSON
"iat": "1714742687"

```

The time the request was created.

### iss: Issuer

```JSON
"iss": "https://canvas.instructure.com"

```

A URL representing the party that initiated the request.

### nonce

```JSON
"nonce": "0c369dfd1d51c28dc4dd47d3ba164823"

```

This string is originally passed from the tool to the LMS in the previous step of the LTI Launch, and returned as-is. Used to prevent replay attacks. A specific nonce should only be used for a single request.

### sub: Subject

```JSON
"sub": "dfaf09e2-a019-4fb4-f027-ea8d1fced23e"

```

A representation of the user making the request. Canvas asks us to use the [Names and Roles API](https://canvas.instructure.com/doc/api/names_and_role.html) to turn this into a useful user identifier, but it's easier to use _Custom Fields_ configured on the Developer Key.

## Request Context

### deployment_id

```JSON
"https://purl.imsglobal.org/spec/lti/claim/deployment_id": "409:ae84...806"

```

This is the an ID for the unique placement of this tool launch. Each instance of this tool placement will have a unique ID.

### message_type

```JSON
"https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiDeepLinkingRequest",

```

This is the platform's declaration of the intended workflow of the launch. This is likely determined by the Developer Key config and the actual site of the LTI Launch. This example is from an RCE Button launch, with the DeepLinking enabled on the Key.

### version

Which version of the LTI protocol we're working with.

```JSON
"https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",

```

### target_link_uri

```JSON
"https://purl.imsglobal.org/spec/lti/claim/target_link_uri": "https://your.tool/path",

```

This value is configured on your Developer Key, in the "Target Link URI" field.

### context

This hash contains details of the course or similar context from which the tool was launched. It includes the couse code (label), name (title) an "ID" field, but I'm not sure how to turn this ID into something useful. Again, we can fall back to custom field defined in the Developer Key to get a useful course ID.

```JSON
"https://purl.imsglobal.org/spec/lti/claim/context": {
  "id": "62499430cba135337460ba1a02e5a3fbfce45ed5",
  "label": "Art History 101",
  "title": "ABCD-1234-101 (Spring/Summer 2024) Art History 101",
  "type": [
    "http://purl.imsglobal.org/vocab/lis/v2/course#CourseOffering"
  ]
},

```

We also have a definition of the "type" of context that launched the tool. Perusing the [LTI docs](https://www.imsglobal.org/spec/lti/v1p3/#context-type-vocabulary), it would appear that the most likely values here are course#CourseTemplate, course#CourseOffering, course#CourseSection or course#Group (however, the docs list these all as deprecated?).

I can't find any information about `validation_context`, and all the examples in my searches have it listed null. Likewise with `errors`, I'm not sure what might show up in here. These values show up in several claims, I'll ignore them from now on.

### launch_presentation

Details about how to content will be displayed, including the dimensions of type of viewport.

```JSON
"https://purl.imsglobal.org/spec/lti/claim/launch_presentation": {
  "document_target": "iframe",
  "return_url": "https://lms.com/courses/1234/external_content/success/external_tool_dialog",
  "height": 800,
  "width": 1000,
},

```

There's also a `return_url`, which according to the spec is where "the message receiver can redirect to after the user has finished activity, or if the receiver cannot start because of some technical difficulty". In the case of a DeepLinking request, we will actually redirect to a different URL, defined in the `deep_linking_settings` claim.

## Platform Information

### tool_platform

```JSON
"https://purl.imsglobal.org/spec/lti/claim/tool_platform": {
  "guid": "rWra7zZVp2j2FRxdjDWR0gI25jKCkiBq5WdbPwOD:canvas-lms",
  "name": "Your University Name",
  "version": "cloud",
  "product_family_code": "canvas"
},

```

This is were we find information about this LMS (or whatever system is launching the request), including the product, version, and instance of the product.

## User Information

### roles

```JSON
"https://purl.imsglobal.org/spec/lti/claim/roles": [
  "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
  "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
  "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
  "http://purl.imsglobal.org/vocab/lis/v2/system/person#User"
],

```

A list of roles the use has in the LMS, as defined in the [LIS vocabulary](https://www.imsglobal.org/spec/lti/v1p3/#lis-vocabulary-for-institution-roles). It would appear that this lists includes all roles that the user has, not just the roles in the launch context.

### lti11_legacy_user_id

```JSON
"https://purl.imsglobal.org/spec/lti/claim/lti11_legacy_user_id": "00ac...3c1f",

```

This value is intended to aid migrations from LTI v1.1 tools. It references the ID from the [Names and Roles](https://canvas.instructure.com/doc/api/names_and_role.html#method.lti/ims/names_and_roles.course_index) service. If you're building a new tool, disregard this field.

Likewise, the `lti1p1` claim includes the `legacy_user_id`, along with the tool's OAuth key and signature which can aid migrations.

## Custom Fields

### custom

In your Developer Key config, you can request [custom fields](https://canvas.instructure.com/doc/api/file.tools_variable_substitutions.html) be included in the response. This is the easiest way to get Canvas to pass along contextual SIS IDs, which allows you to skip the "Names and Roles" API. There are many fields you can include, it's worth taking a look to discover ways to enhance your tool.

```JSON
# Developer Key Config:
user_sis_id=$Canvas.user.sisSourceId
course_sis_id=$Canvas.course.sisSourceId

# Response
"https://purl.imsglobal.org/spec/lti/claim/custom": {
  "user_sis_id": "1000123",
  "course_sis_id": "12345",
}

```

## Expected Response

## deep_linking_settings

```JSON
"https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings": {
  "deep_link_return_url": "https://your.tool./courses/1234/deep_linking_response?data=eyJ0...igU",
  "accept_types": ["link", "file", "html", "ltiResourceLink", "image"],
  "accept_presentation_document_targets": ["embed", "iframe", "window"],
  "accept_media_types": "image/*,text/html,application/vnd.ims.lti.v1.ltilink,*/*",
  "auto_create": false,
  "accept_multiple": true,
}

```

The important thing here is the `deep_link_return_url`. This is where you will send the browser along with your JWT-encoded content (a subject for a different article.

`accept_types` is self-explanatory, but it's worth pointing out that Canvas will seem to accept a range of response types, including a rich HTML response. These types are detailed at the [Deep Linking Specification](https://www.imsglobal.org/spec/lti-dl/v2p0/).

I'm not sure about `accept_presentation_document_targets`. I don't specify a target in my DeepLinking responses.

`auto_create` indicates whether the response is persisted without further input from the user.

`accept_multiple` indicates the the LMS accepts multiple chunks of content in the `content_items` response (again, a topic for a different article).

Note that this claim has a different URI prefix than the others:

`https://purl.imsglobal.org/spec/**lti-dl**/claim`

vs

`https://purl.imsglobal.org/spec/**lti**/claim`

## Phew.

That's it! Other types of launches will have different parameters. I may document these in the future, but this should give a solid foundation for interpreting the LTI Launch and building your LTI tool.
