---
order: 15
title: Example of Describing the Connection Between the Interests of the Supersystem
  and the Target System
---

# Example of Describing the Connection between Supersystem Interests and the System of Interest 

Let's examine the differences between the usage concept, the system concept, and architectural documentation. The systems thinking approach involves initially viewing the system as a "black box" or from the perspective of the usage concept. We first look outside the system (how it is operated) and then, based on the usage concept, delve into its internal structure, developing the system concept and architectural documentation.

The usage concept and use cases provide a description from the boundary of the system of interest, addressing the question, "how does the system perform its function?" This treats the system as a "black box." Previously, system requirements were developed, but now the focus is on developing the usage concept. You can read more about the decline of requirements engineering in the courses "Systems Thinking" and "Systems Engineering."

Viewing the system as a "transparent box" entails proposing a functional decomposition for the system (from the system's function to the functions of its subsystems) followed by a modular synthesis. This is detailed in the system concept.

Simultaneously, considering the "transparent box" separately highlights the architectural documentation. It reflects the decision to modularly break down the system to satisfy the primary (architectural) characteristics of the system or subjects of interest [ ^1 ].

All these documents are "live," meaning all these descriptions are hypotheses that need testing, modification, justification, and agreement. Testing occurs through changes in the systems, with the system initially created as an MVP [ ^2 ], and continually developed through increments [ ^3 ]. Architecturally, increments are released for maximally decoupled modules (loose coupling) by autonomous teams, thereby achieving continuous system development.

It is important to note that systems thinking is recursive, meaning each creator team applies it similarly at every system level. Recursiveness means that the usage concept of the system of interest is part of the descriptions of the supersystem's concept. This implies that in the creator team of the system of interest, some members describe the supersystem, others handle subsystems, and still others establish the creator team itself. All these systems at different system levels and creation chains need to be managed within a single project or the entire enterprise.

In the next section, we'll explore how this continuous development and consideration of multiple systems are supported by creation systems.

[ ^1 ]: Architectural decisions may include the selection of constraints and modules, inter-module connections, and other factors. Important architectural characteristics can include the system's ability to develop, ease of making changes, and accessibility. More details about the architecture concept are available in the "Systems Engineering" course.
[ ^2 ]: Minimal Viable Product (MVP).
[ ^3 ]: Small product improvements immediately ready for use after completion. Increments contrast with iterations, where something becomes usable only at the project's end (after all iterations).