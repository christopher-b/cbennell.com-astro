---
title: "Parameterized Modules in Ruby"
pubDate: "2024-05-01T04:31:00.000Z"
description: "Ruby lets you use `[]` for more than arrays—and that opens the door to clever tricks like parameterized modules."
slug: "parameterized-modules-in-ruby"
status: "published"
heroImage: "glitch1.jpeg"
tags:
  - "ruby"
---

Reading the documentation for some [dry-rb](https://dry-rb.org/) projects, like [dry-](https://dry-rb.org/gems/dry-container/0.11/)[auto_inject](https://dry-rb.org/gems/dry-auto_inject/1.0/), I was intrigued by the syntax in examples like this:

```ruby
class CreateUser
  include Import["users_repository"]
  ...
end
```

What is this usage of square brackets in the included module? Is this some arcane syntax I’ve never seen before? How can I replicate this in my own code?

It’s actually nothing too magical. Include isn’t a keyword, it’s a method (defined on `Module` itself) and it takes a `Module` as an argument.

We also know that we can define a method named `[]` (as class or instance methods) to give that object “array access” syntax.

```ruby
class List
  def [](index)
    items = [:zero, :one, :two]
    items[index]
  end
end

list = List.new
puts list[1] # :one

```

Same for class methods.

```ruby
class List
  def self.[](index)
    items = [:zero, :one, :two]
    items[index]
  end
end

puts List[2] # :two
```

If this `[]` method returns a module, we can supply that return value to our `include` call.

Let’s implement the `[]` method on our module.

```ruby
module ParameterizedModule
  def self.[](item)
    puts "It works"
    self
  end
end

class Test
  include ParameterizedModule["test"]
end
```

We define `[]` on the module itself so we can call it as we would a class method. We return `self` because `include` is expecting a `Module`.

Now comes the tricky part. How can we use the supplied parameter to customize the behaviour of the module? The parameter is only in scope in the call to `self.[]`, not the rest of module implementation.

The trick is to use `define_method` to add an instance method to the module. `define_method` captures the lexical scope, so the parameters are available within the method you’re defining.

```ruby
module ParameterizedModule
  def self.[](item)
    define_method :item_parameter do
      item
    end

    self
  end

  def get_item
    item_parameter
  end
end

class Test
  include ParameterizedModule["test"]
end

puts Test.new.get_item # "test"
```

This approach does add an extra method (`item_parameter`) to the client class, which is not ideal, as we’re slightly polluting that class’ namespace; I prefer to keep the module’s interface as small as possible. But this is an OK trade-off in my opinion. Just make sure to name your method appropriately to avoid a collision.

We could also choose to just dynamically define the methods that reference the parameter themselves.

```ruby
module ParameterizedModule
  def self.[](item)
    define_method :get_item do
      item
    end

    self
  end
end

class Test
  include ParameterizedModule["test"]
end

  puts Test.new.get_item # test
```

But this comes with its own problem. I can imagine myself doing a global search for “def get_item” to find where this method is defined; this approach breaks that ability. I prefer to have my important methods look like methods. The `item_parameter` method in the previous example is more like plumbing, so we can get away with it there.

## “Array Access” vs. Regular Method Calls

Using the array access syntax implies that we are accessing an item from a collection. That is the convention associated with the syntax, and this is what’s happening in the example from dry-auto_inject. If we want to keep the semantics of a regular method call wherein we are supplying a parameter that doesn’t imply an item in a list, we can just rename the method:

```ruby
module ParameterizedModule
  def self.with_item(item)
    define_method :get_item do
      item
    end

    self
  end
end

class Test
  include ParameterizedModule.with_item("test")
end

puts Test.new.get_item
```

This makes it a bit more obvious what we are actually doing.

There are other situations in the dry-rb documentation where it seems to just use the array access as a shortcut for a “default” method, to avoid needing to call a specific method on a class. From [dry-types:](https://dry-rb.org/gems/dry-types/1.7/)

```ruby
Types::Strict::String["foo"]
# => "foo"
```

There are a few similar example in the official Ruby [docs for Data](https://docs.ruby-lang.org/en/master/Data.html).

```ruby
# https://docs.ruby-lang.org/en/master/Data.html
Measure = Data.define(:amount, :unit)

# Positional arguments constructor is provided
distance = Measure.new(100, 'km')
#=> #

# Alternative form to construct an object:
speed = Measure[10, 'mPh']
#=> #

# https://ruby-doc.org/stdlib-3.0.2/libdoc/set/rdoc/Set.html#class-Set-label-Example
s1 = Set[1, 2] #=> #
```

It seems to have become a convention for calling a _default_ method on a class, much like `.call`. I _want_ to like this approach, because it’s clean and concise, but I think it’s abusing the semantics of the array access syntax.

## Use Case

One way I’m planning to use this in my own code is to supply a list of plugins when `includ`ing my Authentication module in my Rails `ApplicationController` (I may expand on this in a future post).

```ruby
class ApplicationController < ActionController::Base
  include Authentication[
    Authentication::LTIPlugin.new,
    Authentication::SessionPlugin.new,
    Authentication::XhrPlugin.new
  ]
  before_action :require_login
  ...
```

## Conclusion

Parameterized modules give us new options for expressing ourselves in Ruby. The syntax may seem unconventional at first glance, but the underlying mechanisms are straightforward.

The main trade-off in these approaches is between dynamically defining an important method (which becomes less searchable) and dynamically defining an extra helper method, which pollutes the client namespace.

I’m interested in exploring this further and discovering other approaches to solve the problems mentioned above.
