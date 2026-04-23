---
title: "Building an LTI DeepLinking Response in Rails"
pubDate: "2024-05-06T14:08:00.000Z"
description: "DeepLinking lets your LTI tool send content back to the LMS—like inserting rich HTML into Canvas’s editor. This guide walks through persisting launch data, building a response form, rendering Rails views into JWTs, and even making the whole flow dynamic with Turbo."
slug: "building-an-lti-deeplinking-response-in-rails"
status: "published"
heroImage: "../../assets/images/vhs-rainbow.jpeg"
tags:
  - "edtech"
  - "application design"
  - "lti"
  - "rails"
  - "#Import 2026-02-12 04:57"
---

LTI DeepLinking is an LTI standard which enables passing content from your LTI Tool back to the LMS. This allows, for example, an RCE editor button placement that will launch your tool and return rich content to be embedded in the editor.

This article walks through the process of building an LTI Tool that will respond to a DeepLinking request in Rails. All of the code involved can be found in the [public repo](https://github.com/christopher-b/lti-deep-link-example).

---

*This is part 3 of a 3-part series on LTI Launches. Check out the other articles:*

- What’s in a Canvas LMS LTI 1.3 JWT?
- Handling LTI Launches in Rails

---

According to 1EdTech, DeepLinking's goal is to:

> [Reduce] the time and complexity of setting up an LTI tool link and streamlining the process of adding content from third parties into a Tool Consumer.1EdTech

This example will return HTML content, but the DeepLinking spec also allows for a [few other formats](https://www.imsglobal.org/spec/lti-dl/v2p0/#content-item-types), like Link, File, and Image.

A high-level overview of the process:

- Handle the launch while saving some details from the launch for later use
- Redirect to our tool, which allows the user to create some content.
- Send a POST request back to the LMS, with a single parameter named JWT. This is our own signed, encoded JWT that includes all the required claims, as well as the content we want the LMS to embed.

## Enhancing the LaunchContext Object

When we looked at [handling the OIDC launch](https://cbennell.com/posts/handling-lti-launches-in-rails/), we used an `LTI::LaunchContext` model to encapsulate access to some of the claims in the JWT. It turns out that we need to save some of those parameters for later, when we redirect back to the LMS. We can enhance our LaunchContext class to allow it to persist across the user's session with our Tool. Let's revise the LaunchContext class slightly.

I initially tried to save the whole object in the session, but the object turned out to be too large to comfortably fit in the session. We can, however, turn the LaunchContext into an ActiveRecord, so it can be saved in the database (we could also stick it in a memory cache, like [Solid Cache](https://github.com/rails/solid_cache), if available).

Note that this example is slightly different than the version in the other article, but it can be instantiated in the same way. The difference is that this version inherits from ActiveRecord, and the `#build` method calls `#create` rather than `#new`, so it is persisted to the database.

I'm serializing the `custom` field because I want some flexibility to add custom fields to the Developer Key, without needing to add additional columns to the table.

```ruby
module LTI
  class LaunchContext 
app/models/lti/launch_context.rb

```ruby
class CreateLaunchContexts 
db/migrate/..._create_launch_contexts.rb

*This example assumes custom variable substitution in the Developer Key:*

```ruby
user_sis_id=$Canvas.user.sisSourceId
course_sis_id=$Canvas.course.sisSourceId

```

As a reminder, we instantiate this object from our `OIDCController`. Additionally, we'll save the ID of the persisted LaunchContext to the session for later use.

app

```ruby
class OIDCController 
/controllers/oidc_controller.rb

## Preparing the Response

Let's assume that we're redirecting to a `ToolsController`, where we will present a form that allows the visitor to build some content, saved as a `Tool` model. When this form is submitted, it will `POST` back to the LMS with all our crafter JWT. From the user's perspective, building the content might be a multi-step process, or allow some way to save work in progress.

Let's break down some of the steps we will be following:

1. Prepare a response form to submit our content to the LMS.
2. Because we'll be attaching some logic to our response form, we extract it to a ViewComponent to better handle these capabilities.
3. Give our response form component the ability to render the output HTML and encode it in a JWT, which is what we send back to the LMS.
4. Set up our controller to instantiate the required objects and pass them to the view.
5. Render our component.

We give ourselves access to the `LaunchContext` that we've saved in the session.

```ruby
class ToolController 
app/controllers/tools_controller.rb

Let's take a look at the template for our Tool update page. The essential thing we need to do is `POST` back to the LMS with our encoded content.

```ruby
 id=deep_link_reponse_form>
  >
  

```

app/views/tools/edit.html.erb

`response_content` represents the JWT that we're sending to the LMS. We'll cover that shortly. How do we determine `return_url`? The LMS provides this in the LTI Launch, in the `deep_linking_settings` claim.

```ruby
[https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings][deep_link_return_url]

```

We're already saving that value in our `LaunchContext`, so we can insert it into the form's `action`.

We're going to be adding a bit of logic to this form, so let's wrap it in a [ViewComponent](https://cbennell.com/). We'll pass the `LaunchContext` in as a parameter, so we have access to the `deep_link_return_url` and a few other values we will need later. We pass it into the view and render it.

```ruby
class DeepLinkResponseFormComponent 
app/component/deep_link_response_form_component.rb

```ruby
class ToolsController 
app/controllers/tools_controller.rb

```ruby
 id=deep_link_reponse_form>
  >

```

app/components/deep_link_response_form_component.html.erb

```ruby

```

app/views/tools/edit.html.erb

### Rendering Response Content

Now let's talk about the `response_content`. Ideally, this should contain a rendered version of our `Tool` resource. Wouldn't it be nice if we could get Rails to render the `Tool` for us, using our existing resource scaffolding and the Tool `show` view representation? Can we capture the output of `ToolsController#show`? Yes! But there are some hoops to jump through.

We can get Rails to give us the output of a controller action by calling `#render` on the controller class. We need two things:

1. The name of the action we want to render.
2. The parameters that the controller would pass to the view, as instance variables (known as assigns)

An **important caveat** (and shortcoming) with this approach is that the controller callbacks will not be called, and the controller action method itself (`ToolsController#show`) will not run. We have to be careful about how we use this technique. I would recommend not using this approach to call actions on *other* controllers. Because we're handing this request from within the `ToolsController,` I think we can get away with it.

We'll create yet another class to encapsulate this behaviour. It's just a simple immutable value object with a single method, so we use `Data.define`.

```ruby
module LTI
  ResponseContext = Data.define(:controller_class, :action, :assigns) do
    def render
      controller_class.render(action, assigns: assigns, layout: false)
    end
  end
end

```

app/models/lti/response_context.rb

Back to `ToolsController`. Let's create a `ResponseContext` and pass it into a `DeepLinkResponseFormComponent`.

```ruby
class ToolController 
app/controllers/tools_controller.rb

Now our `DeepLinkResponseFormComponent` has everything it needs to render itself properly. Let's tell it how to fetch the response HTML.

```ruby
class DeepLinkResponseFormComponent 
app/component/deep_link_response_form_component.rb

And finally, we can prepare the encoded response. The LMS is expecting a JWT, so we rely, once again, on the [json-jwt](https://github.com/nov/json-jwt) gem to do this for us, using some details from the initial LMS launch.

```ruby
class DeepLinkResponseFormComponent 
app/component/deep_link_response_form_component.rb

Oops, we also need to provide a signing key.

```ruby
class SSL
  def self.private_key
    @key ||= OpenSSL::PKey::RSA.new key_value
  end

  def self.key_value
    ENV.fetch(SSL_JWK_PRIVATE_KEY)
  end
end

```

app/models/ssl.rb

## Dynamic Updates

One additional requirement for my use-case was that the response form update itself dynamically. Essentially, the user loads the *edit* page once, performs a number of actions, then submits the form. I needed a way to get the form to update itself with the most up-to-date copy of the HTML content. Turbo Frames to the rescue.

The solution is fairly simple. We wrap the response form in a Turbo Frame, and tell the controller to respond to Turbo Streams. When the Tool form is submitted, it will refresh the page, including the response form and it's encoded JWT.

We also add a button to submit the response form.

```ruby

  
  

  

```

app/views/tools/edit.html.erb

```ruby
class ToolController 
app/controllers/tools_controller.rb

We also add a button to submit the response form. This can get a bit awkward depending on how you do your layout. Rails doesn't like to render a form within a form (fair) so we create a submit button for the response form that explicitly targets that form using the `form` html attribute. We can stick that button anywhere, even within a different form, and it will always submit the response form itself.

```ruby

  
  
  

  

```

app/views/tools/edit.html.erb

## Conclusion

There you have it, a DeepLinking response with some bells and whistles.

I hope this post has been useful to someone building out their own tool providers. Reminder: all of the code samples are collected in [the repo](https://github.com/christopher-b/lti-deep-link-example).

Happy coding!
