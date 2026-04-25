---
title: "Using Pundit in Phlex Components"
pubDate: "2025-10-31T15:40:41.000Z"
description: "Pundit's helper module makes it easy to do authorization checks in our Phlex views."
slug: "using-pundit-in-phlex-components"
status: "published"
heroImage: "glitch-rainbow.jpeg"
tags:
  - "rails"
  - "phlex"
---

[Pundit](https://github.com/varvet/pundit), the minimal authorization library for Ruby applications, provides a set of helpers to use in your views and controllers. These helpers are the primary way of interacting with Pundit policies.

All of the helper methods come from the `Pundit::Authorization` module. You're instructed to include this module in your `ApplicationController` (and define a `pundit_user` method to help Pundit know which user to authorize) when you install Pundit. This also makes the helpers available in your controllers as well as your vanilla ERB views. These view helpers methods can, for example, be used to conditionally render content. Here's an example from the Pundit README:

```erb
<% if policy(@post).update? %>
  <%= link_to "Edit post", edit_post_path(@post) %>
<% end %>
```

To use this technique in [Phlex](https://www.phlex.fun/) components, we need to include the `Pundit::Authorization` helper in our view components. However, this module also needs access to the currently authenticated user, so we need to tell it how to find that user. We do this the same way we did for our `ApplicationController`: by defining a `pundit_user` method.

If we're going to be doing authorization checks in many different views, it makes sense to include these in our `Base` view.

```ruby
class Views::Base
ApplicationControllerp/views/base.rb
```

Now our components have access to all of the Pundit [helper methods](https://github.com/varvet/pundit/blob/main/lib/pundit/authorization.rb), so we can do something like this in our Phlex view:

```ruby
def render_edit_link
  if policy(@post).update?
    a(href: edit_post_path(@post)) { "Edit post" }
  end
end
```
