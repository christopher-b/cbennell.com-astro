---
title: "Phlex Tabs: Multiple Capture Blocks in a Phlex Component"
pubDate: "2025-03-25T16:20:00.000Z"
description: "Here's how I created a flexible interface for a Phlex component that captures multiple blocks, while maintaining backward compatibility with the simpler string-based API."
slug: "phlex-tabs"
status: "published"
section: "post"
heroImage: "grain-blue2-1.jpeg"
tags:
  - "phlex"
  - "ui"
---

I've been exploring [Phlex](https://phlex.fun) recently, and I've been really happy with how easy it is to migrate existing views and components. Phlex has features to cover a lot of the more tricky cases I've come across so far, the straightforward architecture allows me to come up with solutions for cases that Phlex doesn't support out-of-the-box.

One such case is a [navigation tabs](https://getbootstrap.com/docs/5.0/components/navs-tabs/) component. Inspired by the [Yielding an Interface](https://www.phlex.fun/components/yielding.html#yielding-an-interface) section of the documentation, I came up with an implementation that looked something like this (simplified for clarity):

```ruby
class Components::Tabs < Components::Base
  def initialize
    @tabs = []
  end

  def view_template(&)
    vanish(&)

    render_tab_wrapper do
      @tabs.each { |tab| render_tab(tab) }
    end

    render_content_wrapper do
      @tabs.each { |tab| render_contents(tab) }
    end
  end

  def tab(title, &content)
    @tabs << {title:, content:}
  end

  private

  def render_tab_wrapper(&)
    ul(class: "tabs", &)
  end

  def render_content_wrapper(&)
    div(class: "tab-content", &)
  end

  def render_tab(tab)
    li(class: "tab-item") do
      button(class: "tab-link") { tab[:title] }
    end
  end

  def render_contents(tab)
    div(class: "tab-pane") { tab[:content].call(tab) }
  end
end
---
components/tabs.rb
---
```

The `view_template` method yields itself (via Phlex magic) to the caller, and we call `#tab` in the block to add a new tab (including the title and tab body) to the tab list. We then iterate that tab list twice: once to render the tabs and once to render the contents. This component could be used like so:

```ruby
Components::Tabs.new do |tabs|
  tabs.tab("Tab 1 Title") do
    h1 { "Tab 1 Content" }
  end

  tabs.tab("Tab 2 Title") do
    h1 { "Tab 2 Content" }
  end
end
---
tabs-example.rb
---
```

This method worked well, until I needed to include HTML in my tab title. It's awkward to pass HTML as a string to `#tab` (and we would need to use Phlex's `raw` and `safe`), and we're already using the block parameter to capture the tab contents. What I needed was a way to pass in two blocks when calling `#tab`, one for the title and one for the body. Here's what I came up with:

```ruby ins={2-17, 35-47,61}
class Components::Tabs < Components::Base
  class TabData
    attr_reader :title_content, :body_content

    def initialize
      @title_content = -> { raise "No title content provided" }
      @body_content = -> { raise "No body content provided" }
    end

    def title(&content)
      @title_content = content
    end

    def body(&content)
      @body_content = content
    end
  end

  def initialize
    @tabs = []
  end

  def view_template(&)
    vanish(&)

    render_tab_wrapper do
      @tabs.each { |tab| render_tab(tab) }
    end

    render_content_wrapper do
      @tabs.each { |tab| render_contents(tab) }
    end
  end

  def tab(title = nil, &body)
    tab_data = TabData.new
    @tabs << tab_data

    if String === title
      tab_data.title { title }
      tab_data.body(&body)
    else
      yield tab_data
    end

    tab_data
  end

  private

  def render_tab_wrapper(&)
    ul(class: "tabs", &)
  end

  def render_content_wrapper
    div(class: "tab-content", &)
  end

  def render_tab(tab, active)
    li(class: "tab-item") do
      button(class: "tab-link") { tab.title_content&.call || "" }
    end
  end

  def render_contents(tab, active)
    div(class: "tab-content") { tab.body_content&.call || "" }
  end
end
---
components/tabs.rb
---
```

The big change here is how the `#tab` method works. There are now two ways to call this method; we can still use the existing interface, where we pass the tab title as a string and the tab body in the block. However, the internal behaviour has changed: we now create an instance of our new `TabData` object, which is basically a container for two blocks (or procs, really). We assign the passed-in body block to the new `tab_data`, create a new block for the title and assign that block to our `tab_data` as well.

We also introduce a new way to use `#tab`. If we don't pass in a title, `#tab` will yield the `tab_data` object, allowing the caller to use `#body` and `#title`. Now we can capture HTML block for both title and body! An example:

```ruby
Components::Tabs.new do |tabs|
  tabs.tab do |tab|
    tab.title do
      strong { "HTML Tab 1 Title" }
    end
    tab.body do
      h1 { "Tab 1 Content" }
    end
  end

  tabs.tab do |tab|
    tab.title do
      strong { "HTML Tab 2 Title" }
    end
    tab.body do
      h1 { "Tab 2 Content" }
    end
  end
end

```

Here's the unabridged component, complete with Bootstrap classes and accessibility inclusions.

````ruby
class Components::Tabs < Components::Base
  class TabData
    attr_reader :title_content, :body_content
    attr_accessor :slug

    def initialize
      @title_content = -> { raise "No title content provided" }
      @body_content = -> { raise "No body content provided" }
    end

    def title(&content)
      @title_content = content
    end

    def body(&content)
      @body_content = content
    end
  end

  def initialize
    @tabs = []
    @slug_seed = rand(36**8).to_s(36).rjust(8, "0")
  end

  def view_template(&)
    vanish(&)

    render_tab_wrapper do
      @tabs.each_with_index do |tab, index|
        active = index.zero?
        render_tab(tab, active)
      end
    end

    render_content_wrapper do
      @tabs.each_with_index do |tab, index|
        active = index.zero?
        render_contents(tab, active)
      end
    end
  end

  # This method can be called one of two ways:
  #
  # ```
  # Plain text tab title:
  # Components::Tabs.new do |tabs|
  #   tabs.tab("Tab 1") do
  #     tab_content_goes_here
  #   end
  # end
  #
  # HTML Tab Title
  # Components::Tabs.new do |tabs|
  #   tabs.tab do |tab|
  #     tab.title do
  #       html_title_contents
  #     end
  #
  #     tab.body do
  #       body_contents
  #     end
  #   end
  # end
  # ```
  def tab(title = nil, &body)
    tab_data = TabData.new
    @tabs << tab_data

    tab_data.slug = @slug_seed + "-" + @tabs.size.to_s

    if String === title
      tab_data.title { title }
      tab_data.body(&body)
    else
      yield tab_data
    end

    tab_data
  end

  private

  def render_tab_wrapper
    ul(class: "nav nav-tabs", role: "tablist") do
      yield
    end
  end

  def render_content_wrapper
    div(class: "tab-content") do
      yield
    end
  end

  def render_tab(tab, active)
    li(class: "nav-item", role: "presentation") do
      button(
        class: ["nav-link", ("active" if active)],
        id: "#{tab.slug}-tab",
        role: "tab",
        type: "button",
        aria: {
          controls: "#{tab.slug}-tab-pane",
          selected: active.to_s
        },
        data: {
          bs_toggle: "tab",
          bs_target: "##{tab.slug}-tab-pane"
        }
      ) { tab.title_content&.call || "" }
    end
  end

  def render_contents(tab, active)
    div(
      class: ["tab-pane", "fade", ("show active" if active)],
      id: "#{tab.slug}-tab-pane",
      role: "tabpanel",
      aria: {labelledby: "#{tab.slug}-tab"},
      tabindex: "0"
    ) { tab.body_content&.call || "" }
  end
end
---
components/tabs.rb
---
````
