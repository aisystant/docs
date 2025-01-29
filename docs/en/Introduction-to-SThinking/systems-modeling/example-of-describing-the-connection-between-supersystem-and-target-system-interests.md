---
order: 12
title: Example of Describing the Connection between Supersystem and Target System
  Interests
---

Let's explore the differences between the usage concept, the system concept, and architectural documentation. **The practice of systems thinking involves** **first viewing the system** **as a "black box"** or from the perspective of the usage concept. Initially, we assess the system externally (in terms of how it operates) and then, based on the usage concept, delve into its internal structure, creating the system concept and architectural documentation.

**The usage concept** and use cases provide a description from outside the boundary of the target system, answering the question, "how does the system perform its function?" This is akin to describing the system as a "black box." Previously, system requirements were developed, but now the usage concept is created. For more details on the decline of requirements engineering, refer to the courses "Systems Thinking" and "Systems Engineering."

Viewing the system as a "transparent box" involves proposing a functional decomposition for the system (from the system's function to the functions of its subsystems) followed by modular synthesis. This is outlined in the **system concept**.

Moreover, when considering the "transparent box," **architectural documentation** is specifically highlighted. It reflects the decisions regarding the modular division of the system to meet the primary (architectural) characteristics or subjects of interest^[Architectural decisions may include choosing constraints and modules, connections between modules, and other factors. Important architectural characteristics can include system scalability, ease of modification, and usability. For more on architectural concepts, refer to the "Systems Engineering" course.].

All these documents are "living," meaning these descriptions are hypotheses that need to be tested, modified, justified, and aligned. Testing occurs through system changes, with the system initially created as an MVP^[Minimal Viable Product.], and then continuously developed through increments^[Small product improvements that are ready for use immediately upon completion. Increments are contrasted with iterations, after which something is only ready for use at the end of the project (all iterations).]. Architecturally, **increments** are released for the most loosely coupled modules by autonomous teams, thereby achieving continuous system development.

Note that **systems thinking is recursive**, meaning each creator team applies it consistently at every system level. Recursiveness indicates that the usage concept of the target system is part of the overarching system concept. This implies that within the creator team, someone is responsible for describing the overarching system, another for subsystems, and yet another for building the creator team itself. All these systems, across various system levels and creation chains, need to be managed within a single project or the entire organization.

In the next section, we'll explore how this continuous development and consideration of multiple systems are supported by creation systems.