# Multiple Inheritance in Python

## What is it?
Imagine you have a child who inherits traits from both their mother and their father. Maybe they get their dad's height and their mom's eye color. 

In Python, **Multiple Inheritance** works exactly like that. It's when a new class (the "child" or subclass) inherits features (characteristics and methods) from more than one existing class (the "parents" or base classes).

In many programming languages, you can only inherit from one parent class at a time. However, Python allows a class to have as many parent classes as you want!

## Why do we use it?
It's really useful when you want to combine the abilities of two different classes into a single, specialized class. It saves you from having to copy-paste code and keeps things organized.

## A Simple Example

Let's say we are making a game. We have a `Bird` class that can fly, and a `Fish` class that can swim. What if we want to create a `Duck`? A duck can both fly and swim!

Instead of writing the swimming and flying methods all over again, our `Duck` class can just inherit from both `Bird` and `Fish`.

```python
# Parent Class 1
class Bird:
    def fly(self):
        print("I am flapping my wings to fly!")

# Parent Class 2
class Fish:
    def swim(self):
        print("I am moving my fins to swim!")

# Child Class inheriting from BOTH Parent classes
class Duck(Bird, Fish):
    def quack(self):
        print("Quack quack!")

# Let's test it out!
my_duck = Duck()

print("What can the duck do?")
my_duck.fly()   # Inherited from Bird
my_duck.swim()  # Inherited from Fish
my_duck.quack() # Duck's own specific method
```

### Things to watch out for
One thing you need to be careful with is the **Diamond Problem**. If both parent classes have a method with the exact same name, Python needs a way to decide which one to use. It handles this using something called **MRO (Method Resolution Order)**, which basically prioritizes the parent classes from left to right in the order you listed them when creating the child class. 

For example, in `class Duck(Bird, Fish):`, if both `Bird` and `Fish` had an `eat()` method, Python would use the `Bird`'s eat method because `Bird` is listed first!
