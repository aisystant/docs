---
order: 15
title: Example of Describing the Connection Between the Interests of the Supersystem
  and the Target System
---

Let's examine the differences between the usage concept, system concept, and architectural documentation. The approach in systems thinking is to first consider the system as a "black box" or from the perspective of the usage concept. Initially, we observe the system’s external use (how it operates) and then, based on this usage concept, delve into its internal structure by creating the system concept and architectural documentation. 

The usage concept and use cases involve describing everything beyond the system of interest, answering the question, "how does the system perform its function?" This represents the system as a "black box." Previously, systems requirements were developed, but now the focus is on developing the usage concept. For more on the obsolescence of requirement engineering, refer to the courses "Systems Thinking" and "Systems Engineering."

Viewing the system as a "transparent box" involves proposing a functional decomposition of the system (from the system function to the functions of its subsystems) and subsequent modular synthesis. This is encapsulated in the system concept.

When considering the "transparent box," architectural documentation is separately highlighted. It reflects the decision on the modular breakdown of the system to satisfy the primary (architectural) characteristics or subjects of interest. Architectural decisions may include the choice of constraints and modules, the connections between modules, and other factors. Important architectural characteristics can include the system’s ability to evolve, the ease of making changes, and accessibility. More on the architecture concept can be learned in the "Systems Engineering" course.

All these documents are "living," meaning their descriptions are hypotheses that need to be tested, modified, justified, and aligned. Testing occurs through system changes, initially creating the system as an MVP (Minimal Viable Product), and it continues to develop through increments. These increments, which are small product improvements ready for use immediately upon completion, contrast with iterations, where something is only ready for use at the end of the project (all iterations). Architecturally, increments are released for the most loosely coupled modules by autonomous teams. This ensures the continuous development of the system.

Note that systems thinking is recursive, meaning each creation team applies it consistently at every system level. Recursion indicates that the usage concept of the system of interest is part of the supersystem description. This means that within the creation team for the system of interest, some members work on the supersystem description, others on subsystems, and others on the creation team itself. All these systems across different system levels and creation chains must be addressed within a single project or the entire enterprise.

In the next section, we will explore how this continuous development and exploration of multiple systems are supported by creation systems.