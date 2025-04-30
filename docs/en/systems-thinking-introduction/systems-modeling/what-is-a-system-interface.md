---
order: 10
title: What is a System Interface?
---

### Understanding Interfaces: The Bridge Between Us and Systems

Imagine you want to charge your phone, but the charger and smartphone have different connectors. Or you sit in a new car and can't immediately figure out how to turn on the headlights. Why does this happen? It all comes down to the interface!

When we interact with any system, we don't see its inner workings—it's a black box to us. For the system to function properly, it must have clear points of interaction, which are defined through interfaces. In describing a system as a black box, we're only concerned with how it interacts with the external world, without delving into its internal mechanisms.

An **interface** is the description of the rules and standards for a system's interaction with the external world. It exists as a mental or informational concept and lacks physical embodiment. However, to facilitate actual interaction, an interface module is needed—a physical object that implements the interface. The interface defines how interactions should occur, while the interface module ensures the physical execution of these rules.

The interface is a component of the system description, but not the system itself. It outlines how data can be fed into the system, how to get the results of its work, and what input and output constraints exist.

#### Example: The Car as a System

In a car system, the interface is the description of interaction rules between the driver and the car. It specifies the actions a driver must take to issue commands to the vehicle. For instance, the car control interface includes rules like: "turning the steering wheel changes the direction of movement," "pressing the accelerator pedal increases speed," and "activating the ignition button starts the engine." In turn, the interface module is the physical object that implements this described interface. In a car, interface modules include the steering wheel (directional control device), gas pedal (acceleration device), and engine start button. Here, the concept of a “black box” explains that the driver doesn't see how the car works or how the engine converts fuel into motion, but interacts with the system through interface modules, thus controlling the car.

In this example, the following interfaces and their interface modules can be identified:

- **Physical interface**: rules for interaction with mechanical control elements; interface modules include pedals, steering wheel, and dashboard buttons.
- **Informational interface**: rules for providing the driver with data about the car's status; interface modules include the speedometer, fuel indicators, and dashboard display.
- **Energy interface**: guidelines for delivering energy to the car; interface modules include the fuel tank and electric vehicle charging port.
- **Voice interface**: rules for voice interaction with the car; interface modules include the microphone, voice processor, and audio system.

If each car had a unique control interface, drivers would need to relearn for each trip. It's the standardization of interfaces that makes driving understandable and universal.

In conclusion, an interface is an intangible concept describing the rules for a system's interaction with the external world. The interface module is the physical component that implements this interface. The interface is part of the system's description as a black box, but not the system itself. Without interfaces, systems can't interact with each other or with users. We live in a world of interfaces—from cars and gadgets to language and social interactions. The better the interface is designed, the easier and more convenient it is to work with the system!