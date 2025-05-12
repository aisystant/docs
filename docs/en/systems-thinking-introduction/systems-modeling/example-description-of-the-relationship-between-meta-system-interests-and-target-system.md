---
order: 15
title: Example Description of the Relationship Between Meta-System Interests and Target
  System
---

# Example Description of the Relationship between Supersystem Interests and the System of Interest

Let's explore the differences between a usage concept, a system concept, and architectural documentation. The practice of using systems thinking involves first viewing a system as a "black box" or from the perspective of the usage concept. We initially look outside the system (how it is operated), and from the usage concept, we delve into its internal structure, developing the system concept and architectural documentation.

The usage concept and use cases are descriptions extending from the boundary of the system of interest, answering the question, "How does the system perform its function?" This is the description of the system as a "black box." Previously, system requirements were developed, but now the focus is on developing a usage concept. For more on the decline of requirements engineering, refer to the courses on "Systems Thinking" and "Systems Engineering."

Considering the system as a "transparent box" includes proposing a functional decomposition for the system (from the system function to subsystem functions) followed by modular synthesis. This is described in the system concept.

When examining the "transparent box," architectural documentation is highlighted separately. It reflects the decision on modular breakdown of the system to meet the main (architectural) characteristics of the system or subjects of interest[^1^].

Furthermore, all these documents are "living," meaning that all these descriptions are hypotheses that need to be tested, modified, justified, and aligned. Testing takes place through changes in systems, with the system initially created as an MVP[^2^] and then continuously developed through increments[^3^]. Architecturally, increments are released for modules with loose coupling by autonomous teams, thereby achieving continuous system development.

Note that systems thinking is recursive; each creation team applies it uniformly at every system level. Recursiveness means that the usage concept of the system of interest is part of the supersystem's concept descriptions. This implies that within the creation team of the system of interest, someone handles the supersystem description, someone the subsystems, and someone else creates the creator team itself. All these systems on different system levels and creation chains need to be handled within a single project or entire enterprise.

In the next section, we will consider how this continuous development and consideration of multiple systems is supported by creation systems.

[^1^]: Architectural decisions may include the choice of constraints and modules, connections between modules, and other factors. Key architectural characteristics might include the system's adaptability, ease of making changes, and availability. More on architecture concepts can be found in the "Systems Engineering" course.

[^2^]: Minimal Viable Product (MVP).

[^3^]: Small product improvements that are ready for use immediately after completion. Increments are contrasted with iterations, where something becomes usable only at the end of the project (all iterations).