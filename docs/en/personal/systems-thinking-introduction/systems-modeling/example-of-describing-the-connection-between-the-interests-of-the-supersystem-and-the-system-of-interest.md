---
title: "Example of Describing the Connection Between the Interests of the Supersystem and the System of Interest"
order: 15
---

# Example of Describing the Connection Between the Interests of the Supersystem and the System of Interest

Let's examine the differences between the usage concept, the system concept, and architectural documentation. The systems thinking approach involves first considering the system as a "black box," or from the perspective of the usage concept. We begin by looking at the system from the outside (how it is operated), and only after understanding the usage concept do we delve into its internal structure, developing the system concept and architectural documentation.

The usage concept and use cases are descriptions that extend outward from the boundary of the system of interest, answering the question, "How does the system perform its function?" This is the description of the system as a "black box." Previously, system requirements were developed, but now the focus is on developing the usage concept. For more on the end of requirements engineering, see the courses "Systems Thinking" and "Systems Engineering."

Considering the system as a "transparent box" involves proposing a functional decomposition for the system (from the system's function to the functions of its subsystems) and then performing modular synthesis. This is described in the system concept.

At the same time, when considering the "transparent box," architectural documentation is treated separately. It reflects the decisions regarding the modular breakdown of the system to satisfy the main (architectural) characteristics of the system or subjects of interest^[Architectural decisions may include the selection of constraints and modules, the relationships between modules, and other factors. Important architectural characteristics may include the system's capacity for development, ease of making changes, and accessibility. For more on the concept of architecture, see the course "Systems Engineering."]. 

All these documents are "living," meaning all these descriptions are hypotheses that need to be tested, revised, justified, and agreed upon. Testing occurs through changes to systems, with the system initially created as an MVP^[Minimal Viable Product.], and then continuously developed through increments^[Small product improvements that are ready for use immediately after completion. Increments are contrasted with iterations, after which something will only be ready for use at the end of the project (after all iterations).]. Architecturally, increments are released for the most loosely coupled modules by autonomous teams. This enables the continuous development of the system.

Note that systems thinking is recursive, meaning each creator team applies it in the same way at every system level. Recursiveness means that the usage concept of the system of interest is part of the descriptions for the supersystem concept. This means that within the creator team of the system of interest, someone works on describing the supersystem, someone else focuses on the subsystems, and another person creates the creator team itself. All these systems at different system levels and creation chains must be addressed within a single project or across the entire enterprise.

In the next section, we will look at how this continuous development and consideration of multiple systems is supported by creation systems.