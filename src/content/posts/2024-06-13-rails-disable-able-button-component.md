---
title: 'Rails "Disable-able" Button ViewComponent / Phlex Component'
pubDate: "2024-06-13T14:31:00.000Z"
description: "Need a button that enables or disables itself in response to events? I explain how to build a reusable DisableableButton in Rails using ViewComponent (or Phlex) plus a tiny Stimulus controller—perfect for forms where you only want to allow submission once inputs are valid."
slug: "rails-disable-able-button-component"
status: "published"
heroImage: "../../assets/images/vhs-purple.jpeg"
tags:
  - "ui"
  - "phlex"
  - "rails"
  - "stimulus"
  - "viewcomponent"
---

Here's a simple ViewComponent/Stimulus controller for a disable-able button; that is, a button that you can programmatically disable/enable. You could use this to prevent form submission until all fields are valid.

If anyone has a better name for this component, please let me know!

## First, the Template

Pretty simple: we render a button in a span, passing along some tag options from the component class.

```ruby

```

app/components/ui/disableable_button.html.erb

## The Component

The component itself has a few things going on.

```ruby
module UI
  class DisableableButton disableable-button#enable" },
            enable_events.map { |ev| "#{ev}->tooltip#disable" },
            disable_events.map { |ev| "#{ev}->disableable-button#disable" }
          ].flatten.join(" ")
        }
      }

      button_options = {
        disabled: disabled,
        class: %W[btn btn-#{variant}],
        data: {
          "disableable-button-target": "button"
        }
      }

      @container_options = container_options
      @button_options = tag_options.deep_merge(button_options)
    end
  end
end

```

app/components/ui/disableable_button.rb

Let's go over the initializer params:

```ruby
def initialize(
  disabled: false,
  disable_events: [],
  enable_events: [],
  disabled_tooltip: "",
  variant: "light",
  tag_options: {}
)

```

app/components/ui/disableable_button.rb

- disabled: set the default state of the button.
- disable_events/enable_events: a list of events that the component will respond to, which control the state of the button.
- disabled_tooltip: popover text that will appear when hovering over the disabled button. Note that this requires another Stimulus controller ("tooltip") to work.
- variant: passed along as a CSS class to the button. This allows us to set a default variant that can be overridden if required.
- tag_options: additional options that can be passed along to the button tag. Allows arbitrary customization of the button tag.

---

We then create the container options hash, which is used to create the container span tag. This is where we set up our tooltip, because the tooltip library I'm using ([Bootstrap](https://getbootstrap.com/docs/5.2/components/tooltips/)) doesn't work on disabled buttons themselves.

We also indicate the stimulus controllers to use ("disableable-button" and "tooltip") and build a list of event listeners, which are flattened into a single string.

```ruby
container_options = {
  tabindex: 0,
  title: disabled_tooltip,
  class: "d-inline-block",
  data: {
    controller: "disableable-button tooltip",
    action: [
      enable_events.map { |ev| "#{ev}->disableable-button#enable" },
      enable_events.map { |ev| "#{ev}->tooltip#disable" },
      disable_events.map { |ev| "#{ev}->disableable-button#disable" }
    ].flatten.join(" ")
  }
}

```

app/components/ui/disableable_button.rb

Finally, we set some parameters for the button itself, include indicating that it is the "target" that will be used by the Stimulus controller.

```ruby
button_options = {
  disabled: disabled,
  class: %W[btn btn-#{variant}],
  data: {
    "disableable-button-target": "button"
  }
}

```

app/components/ui/disableable_button.rb

## Speaking of the Stimulus Controller...

...it's dead simple. It has two methods that set or remove the "disabled" attribute on the button.

```ruby
import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["button"]

  enable(event) {
    this.buttonTarget.removeAttribute("disabled")
  }

  disable(event) {
    this.buttonTarget.setAttribute("disabled", "disabled")
  }
}

```

app/javascript/controllers/disableable_button_controller.js

## That's it!

Now we render the button.

```ruby


  Submit Grades

```

## Update: Now With Phlex!

Since writing this, I've migrated this component to [Phlex](https://www.phlex.fun/)/[Literal](https://literal.fun/). This replaces the ViewComponent and template, but it still requires the Stimulus controller.

```ruby
class Ui::DisableableButton disableable-button#enable" },
          enable_events.map { |ev| "#{ev}->tooltip#disable" },
          disable_events.map { |ev| "#{ev}->disableable-button#disable" }
        ].flatten.join(" ")
      }
    }
  end

  def button_options
    tag_options.deep_merge({
      disabled: disabled,
      class: %W[btn btn-#{variant}],
      data: {
        "disableable-button-target": "button"
      }
    })
  end
end

```

app/components/ui/disableable_button.rb
