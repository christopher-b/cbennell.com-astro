---
title: "Default, Dynamic Slot Content in Rails ViewComponents"
pubDate: "2024-09-25T15:30:00.000Z"
description: "Ever wished your ViewComponent slots could have dynamic defaults? In this post, I show how I built an Alert component that automatically picks the right icon for its type, but can easily swap in a spinner or any custom icon with a single line of code."
slug: "defaults-slot-content-in-rails-viewcomponents"
status: "published"
heroImage: "holo-1.jpeg"
tags:
  - "rails"
  - "viewcomponent"
---

Have you ever wanted to have a default value for a [ViewComponent slot](https://viewcomponent.org/guide/slots.html), or to make the default value dynamic?

I have an "alert" component which usually renders an icon based on the alert variant (sucess, error, warning, etc.) I recently had a requirement to conditionally render a different icon (in this case, a spinner) independent of the alert variant. The solution I came up with was to use the [polymorphic slots](https://viewcomponent.org/guide/slots.html#polymorphic-slots), along with a `before_render?` check to see if an icon has been declared for that slot.

This solution made rendering a spinner icon very concise; I don't need to include the entire instantiation of the `Ui::Spinner` component.

Here's the component template.

```erb
<div class="alert alrt-<%= @type %>" role="alert">
  <span class="alert-icon">
    <%= icon %>
  </span>

  <div class="alert-content">
    <%= content %>
  </div>
</div>
---
app/components/ui/alert.html.erb
---
```

And the component class. If the icon slot has not been explicitly filled, we set it to a dynamic default.

```ruby
module Ui
  class Alert (size: :small) { Ui::Spinner.new(size: size) },
      icon: Ui::Icon
    }

    def initialize(type)
      @type = type
    end

    def before_render
      unless icon?
        set_slot(:icon) do
          render default_icon
        end
      end
    end

    def default_icon
      case @type
      when :error
        Ui::Icon.new("block")
      when :primary
        Ui::Icon.new("info_i")
      when :secondary
        Ui::Icon.new("more_horiz")
      when :success
        Ui::Icon.new("check")
      when :warning
        Ui::Icon.new("priority_high")
      end
    end
  end
end
---
app/components/ui/alert.rb
---
```

We can render an alert like so, to have the default icon for the alert variant.

```erb
<%# Renders the success "check" icon %>
<%= render Ui::Alert.new(:success) do %>
  Content...
<% end %>`
```

Or with a spinner.

```erb
<%= render Ui::Alert.new(:secondary) do |alert| %>
  <% alert.with_icon_spinner %>
    Content...
<% end %>
```

Or with an any icon we like, using the awkwardly named `.with_icon_icon`!

```erb
<%= render Ui::Alert.new(:secondary) do |alert| %>
  <% alert.with_icon_icon("search") %>
<% end %>
```

I love discovering the flexibility and power of ViewComponents. I often feel like I'm just scratching the surface of the capabilities.
