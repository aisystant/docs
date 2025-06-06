---
title: "Main Descriptions of the System as a "Transparent Box""
order: 11
---

# Main Descriptions of the System as a "Transparent Box"

In systems modeling, we always begin by focusing on the area of interest of the supersystem^[One of the system thinking skills: the first step of attention is always outward from the boundary of the system of interest, and the second step is inward into the system.]—identifying the external project roles, their needs, and subjects of interest. Only after that do we move on to the structure of the system of interest, which we will discuss in this subsection. In the next section, Section 7, you will learn about the specifics of modeling creation systems.

The system of interest is considered both as a "black box" and as a "transparent box."

A system as a black box is described through role-based behavior and function, subjects of interest, capabilities (needs), and external project roles. The system as a "black box" can be described as a future system^[That is, design in terms of modeling what kind of system is needed as part of the supersystem. This is direct engineering.] or as an existing one^[Or reverse engineering, meaning we describe an already functioning system if such a description is unavailable but needed for some purpose. This is "reverse engineering."]. In both cases, you need to pay attention to the following descriptions of the system:

* as a functional/role-based object and its behavior in interaction with the environment during operation;
* as a structural object, which is represented in the physical world and occupies space during operation;
* as the total cost of ownership of the system.

Note that from these descriptions of the system as a "black box," the description of the system as a "transparent box" follows. The internal description is an inherent consequence of the external one. For example, in Section 3, we already discussed the role of the architect, who determines the structural (modular) design of the system based on the architectural subjects of interest of the system.

In this subsection, we will discuss how to describe the internal structure of a system ("transparent box"). The conventional "breakdown" of a system into parts can be done in various ways^[If different people look at a kitten, they will see different things. A veterinarian will see the biological structure of the kitten, while a grandmother will see a warm and fluffy object. A system can be divided by the materials used (iron, plastic, glass, etc.), by the color of the parts (black, white, or colored), or by the shape of the parts (round, square, etc.).]. Here are four main types of dividing a system into parts, with corresponding descriptions using the example of a "teapot" system:

* Someone is interested in the functions of the parts during operation and will say that a teapot consists of a vessel, a pouring spout, a filling hole in the vessel, a handle on the vessel, a lid, a handle on the lid, and also a steam vent in the lid—otherwise, when closing a wet lid, water will splash out of the spout. This is called the functional description of the teapot system, and the description of subsystems as role-based (functional) objects is called a system breakdown.
* Another person says that the teapot consists of only two parts in its design that need to be manufactured, because their interest lies in the time required to make the teapot. Here, the subject of interest is in the structure, specifically in "what to manufacture" or "how to assemble." This is the modular (product-based) description of the system.
* A third person says that the lid and the teapot should be stored together, and it would be better if the lid were right on the teapot. This is an interest in placement, that is, "where in the universe the parts of the teapot are located." This is the description of locations, placements (spatial description) of the system's parts within it.
* A fourth person talks about the cost of the teapot's parts, that is, what will require spending money and other resources. This is the cost-based description, which is part of the description of the total ownership of the system as a "black box."

Systems thinking involves multiple descriptions of a system. However, four main types of descriptions or perspectives on dividing a system into parts are distinguished^[For example, recently, an additional subject of interest has been identified regarding what work is performed with the system's parts.]. The main decisions about the structure of a system are called the system concept. Usually, the system concept is not created just once; it gradually accumulates details until the description of the system is precise enough for its production on a manufacturing platform. In other words, the system concept is "alive"—it changes as development progresses, and the system is constantly modified even after the start of its operation.

To create each of these system descriptions, you need to know a specific practice or method of description. Using this method, a specific work artifact is produced. For example, as mentioned earlier, using the method of management accounting description, you can obtain a financial description of the enterprise system, which is of interest to a manager.

Note that all these descriptions do not coincide with each other. It is especially difficult to notice the mismatch between the functional and modular descriptions. Usually, developers define the main function of the system and consider the system as a functional object consisting of functional subsystems. The architect then determines which structural modules (executors/performers) will play these roles. The correspondence between functional and modular parts does not have to be one-to-one, and the names of these parts may differ. Look at the example with scissors, where the functional parts are the blade assembly and the handle, while the modular parts are half 1 and half 2.

![](/en/systems-thinking-introduction/Scissors_Functional_vs_Modular_Description.png)

In systems projects, functional analysis is performed—that is, breaking down into parts (analysis means division)—and modular synthesis, that is, assembly. Beware of a project where it is unclear who makes the synthesis decisions. Such projects usually involve analysts, but they do not change the world. Synthesis and synthesis decisions are what change the world!

Thus, a person using a systems approach is able to consider the structure of any system as a "transparent box," identifying at least four subjects of interest:

* functional=role-based=analytical^[Usually, analysis or breaking down into parts is done to understand the principle of the system's structure. That is, analysis helps to understand the functional parts of the system. Synthesis or assembly is related to the procedure of assembling the system from physical models. Therefore, people often talk about functional analysis and modular synthesis. Both analysis and synthesis are necessary. You cannot focus on only one.];
* modular=structural=synthetic;
* spatial=location=placement;
* cost-based=economic=resource-based.