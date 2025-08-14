---
title: "Describing the System as a \"Black Box\""
order: 8
---

# Describing the System as a "Black Box"

When we consider a system as a black box, we are interested in how it interacts with the external world—what functions it performs, which interfaces it uses, what states it can be in, and which characteristics affect its operation. The internal structure of the system remains outside the scope of this analysis (that would be viewing the system as a glass box).

The following descriptions can be distinguished when viewing a system as a black box:

1. The function of the system – what the system does, what its purpose is.
2. The interfaces of the system – how it interacts with the external world.
3. The states of the system – the different states the system can be in.
4. The characteristics of the system – the properties of the system that affect its operation.

These descriptions help us understand how the system works without studying its internal mechanisms, which is useful when designing, analyzing, or integrating the system into more complex structures. Describing a system as a black box provides a universal view of the system, while the usage concept clarifies how it operates in specific scenarios.

Let’s break down each description with several examples.

**The function of the system** answers the question of what the system does and what problem it solves. The function describes the main purpose of the system.

Examples:

* A car performs the function of transporting people and goods.
* A person in the role of a thinker performs the function of processing information and carrying out physical or intellectual tasks.
* A phone performs the function of transmitting and processing voice, text, and digital data.

The function of the system directly determines which interfaces it needs. For example, if the function of a phone is to transmit data, it must have the appropriate communication interfaces (screen, speaker, microphone, touch input). If the system acquires additional functions, it may require new interfaces or modifications to existing ones.

**Interfaces** describe how the system interacts with the external world. An interface is a description of the rules of interaction, and interface modules are the physical objects that implement these rules.

Examples:

* A car has a driving control interface, which describes how the driver gives commands to the car. Interface modules: steering wheel, gas pedal, brake, gear shift lever.
* A person has a visual interface, which describes the rules for perceiving visual information. Interface module: eyes.
* A phone has a tactile control interface, which describes how the user interacts with the phone through touch. Interface module: touch screen.

Interfaces are closely connected to the states of the system. For example, if a car is in the “moving” state, the driving control interface allows the driver to change speed and direction. But if the car is in the “malfunction” state, some interfaces may become unavailable.

**The states of the system** answer the question of what modes it can be in at different times.

Examples:

* Car: moving, stationary, malfunctioning.
* Person: awake, asleep, ill, tired.
* Phone: on, off, in power-saving mode.

States determine which functions the system can perform at a given moment and which interfaces are active. For example, if a phone is off, its control interface is unavailable, and it cannot perform its data transmission function. In some systems, states may change automatically depending on characteristics (for example, a phone switches to power-saving mode when the battery is low).

Characteristics (or subjects of interest) answer the question of which properties of the system affect its operation. They define its capabilities and limitations.

Examples:

* Car: speed, fuel consumption, payload capacity.
* Person: strength, intelligence, endurance, reaction speed.
* Phone: weight, performance, screen resolution.

The characteristics of the system directly affect its interfaces and states. For example, if a car has a low maximum speed, this affects the behavior of the driving control interface. If a phone has a weak processor, it may more often enter a “response delay” state, reducing the quality of user interaction with the interface.

Thus, the descriptions of a system as a black box—function, interfaces, states, and characteristics—give us a holistic understanding of how the system works and interacts with the external world. However, to understand why and under what conditions this system is used, we need to develop a usage concept for the system. This helps connect the technical and functional characteristics of the system with its real-world use cases, determining which of its properties and capabilities are most important in a specific context.

**The usage concept of the system** describes under what conditions, by whom, and how the system is used. This is not part of the black box description of the system, but it helps select the important characteristics, interfaces, and functions for a specific use case.

Examples:

* A car can be used as a personal vehicle, a taxi, or a truck.
* A person in different contexts takes on the roles of worker, student, or athlete.
* A phone can be a personal device, a corporate tool, or a gaming platform.

The main goal of the usage concept is to understand what changes the system causes in its surroundings and how it performs its main function. This helps determine exactly what the system must do to deliver “irreversible benefit” in the supersystem. This approach allows you to focus on the results and effects the system should achieve, without being distracted by the details of its internal structure. In the usage concept, the functions, interfaces, states, and characteristics of the system that are important in specific conditions are defined. For example, a taxi requires an interface for communication with a dispatcher, while a truck requires interfaces for managing payload capacity. It is important to understand that the same system can be used in different usage concepts, and its parameters must match the chosen scenario.

When analyzing a system as a black box, it is important to consider several key aspects:

* The function of the system answers the question of what it does.
* The interfaces of the system describe how it interacts with the world and through which interface modules this is implemented.
* The states of the system determine the modes in which it operates.
* The characteristics of the system set the parameters that define its capabilities.
* The usage concept explains where, by whom, and how the system is applied, determining which parameters of the system description are most important in a specific context.

This approach allows you to analyze a system without studying its internal structure, which is necessary when designing, researching, and integrating systems into more complex supersystems.