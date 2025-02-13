---
order: 12
title: Example of Describing the Connection Between Supersystem and Target System
  Interests
---

Let's explore the differences between a usage concept, a systems concept, and architectural documentation. **The practice of systems thinking involves initially viewing the system** **as a 'black box'** or from the perspective of its usage concept. Initially, we look externally at the system (how it's operated), and from this usage concept, we delve into its internal structure, creating the systems concept and architectural documentation.

**The usage concept** and use cases describe the system from the boundary upwards, answering the question, "How does the system perform its function?" This describes the system as a "black box." Previously, systems requirements were developed; now, the usage concept is developed. For more on the decline of requirements engineering, see the courses "Systems Thinking" and "System Engineering."

Viewing a system as a "transparent box" involves proposing functional decomposition of the system (from the system's function to the functions of subsystems) and subsequent modular synthesis. This is detailed in the **systems concept**.

When considering the "transparent box," **architectural documentation** is highlighted. It reflects decisions on the system's modular division to meet the main (architectural) characteristics or subjects of interest^ [Architectural solutions can include the selection of constraints and modules, the connections between modules, and other factors. Significant architectural characteristics can include the system's development capability, ease of modification, and availability. For details on architectural concepts, see the course "System Engineering".].

All these documents are "living," meaning all these descriptions are hypotheses that need testing, modification, justification, and alignment. Testing is conducted by changing systems, initially creating them as MVPs^ [Minimal Viable Product], and continuously developing them through increments^ [Small product improvements that are ready for use immediately after completion. Increments are opposed to iterations, where something becomes usable only at the end of the project (all iterations).]. Architecturally, **increments** are released for the most loosely coupled modules (loose coupling) by autonomous teams, thus achieving continuous system development.

Note that **systems thinking is recursive**, meaning that each creator team applies it identically at every system level. Recursiveness implies the usage concept of a target system is part of the overarching system concept descriptions. This means that within the creator team of the target system, someone handles the overarching system description, someone else handles the subsystems, and yet another is forming the creator team itself. Within a single project or the entire enterprise, all these systems at various system levels and creation chains need to be managed.

In the next section, we'll examine how this continuous development and the examination of multiple systems are supported by systems of creation.