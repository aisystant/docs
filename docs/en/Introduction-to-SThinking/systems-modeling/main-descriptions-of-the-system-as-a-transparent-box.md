---
order: 8
title: Key Descriptions of the System as a "Transparent Box"
---

In systems modeling, we always begin our work by focusing on the **area of interest of the superset**^[This is one of the systems thinking skills: the first step is to look outward from the boundary of the target system, and the second step is to look inside the system.] — identifying external project roles, their needs, and subjects of interest. Only after this do we move on to the structure of the target system, which we will discuss in this subsection. In section 7, you will learn about the nuances of modeling systems creation.

The target system is examined both as a "black box" and a "transparent box."

A system as a black box is described through role behavior and function, subjects of interest, capabilities (needs), and external project roles. **The system as a "black box"** is described as either a future system^[This pertains to design and engineering in terms of modeling the required system within the superset. This is direct engineering.] or as an existing system^[This involves reverse engineering, where we describe a functioning system if such a description is unavailable but necessary. This is "reverse engineering."]. In both cases, attention must be paid to the following system descriptions:

* As a functional/role object and its behavior in interaction with the environment during operation;
* As a constructive object, which exists in the physical world and occupies space during operation;
* As the full cost of owning the system.

Note that from these descriptions of a system as a "black box," the description of the system as a "transparent box" follows. The internal description is an intrinsic outcome of the external. For instance, in section 3, we discussed the role of the architect who determines the constructive (modular) setup of the system based on the system's architectural subjects of interest.

In this subsection, **we will discuss** **how the internal structure of a system** **(the "transparent box")** **is described.** The conventional "division" of a system into parts can be done in various ways^[If different people look at a kitten, they will see different things. A vet would notice the biological makeup of the kitten, while a grandmother might see a warm and fluffy being. A system can be divided based on materials used (metal, plastic, glass, etc.), color of components (black, white, colorful), or shapes of parts (round, square, etc.)]. Here are four primary ways to divide a system into parts and corresponding descriptions using the example of a "teapot" system:

* Someone interested in the functions of parts during operation might say that a teapot consists of a container, a spout, a filling hole in the container, a handle on the container, a lid, a handle on the lid, and a steam vent in the lid to prevent water from splashing out of the spout when closing a wet lid. This is the so-called **functional description** of the teapot, and the description of subsystems as role (functional) objects is known as **systems breakdown**.
* Another person may focus on the fact that a teapot consists of only two parts in its construction that need to be manufactured, which aligns with their interest in the time of manufacturing the teapot. Here, the subject of interest is the construction, specifically "what to make" or "how to assemble." This is **modular** **(product)** **description of the system**.
* A third person might emphasize that the lid and teapot should be stored together, preferably with the lid directly on the teapot. This reflects an interest in placement, i.e., "where in the universe the parts of the teapot are located." This is **description of locations, placements** **(spatial description)** within the system.
* A fourth person might discuss the cost of teapot parts, indicating what money and resources are needed. This is a **cost description**, which is part of the description of the total ownership of the system seen as a "black box."

System thinking provides for numerous descriptions of a system. However, there are four primary types of descriptions or perspectives on dividing a system into parts^[Lately, an additional subject of interest regarding the operations conducted with parts of the system has been identified.]. The main solutions for the system's structure are known as the **system concept**. Typically, the system concept isn't created just once; it gradually acquires details until the system description is precise enough for manufacturing on a production platform. Thus, the system concept is "alive," evolving throughout development, with the system continually being modified even after the start of its operation.

To create each of these system descriptions, you need to know a certain practice or **method of description.** Via this method, a specific working product is obtained. For instance, the method of management accounting description can yield a financial description for a business system, which interests the manager.

Note that all these descriptions do not match with each other. It is especially **difficult to notice discrepancies between functional and modular descriptions.** Usually, developers define the core function of the system and consider it as a functional object composed of functional subsystems. An architect then determines which constructive modules (executors) will play these roles. The alignment of functional and modular parts doesn't necessarily need to be a 1:1 match, and the names of these parts may differ. Consider the example with scissors, where functional parts are the blade unit and handle, while modular parts are half 1 and half 2.

![](/text/Introduction-to-SThinking/2024-11-23T2158/6150/20.jpeg)

In systems projects, functional analysis occurs, which means dividing into parts (analysis is division), and modular synthesis, which means assembly. Beware of projects where it's unclear who makes the synthesis decisions. In such projects, analysts typically work, but they don't change the world. Synthesis and decisions about synthesis change the world!

Thus, a person using a systems approach can view the structure of any system as a "transparent box," identifying at least four subjects of interest:

* functional=role=analytical^[Usually, analysis or dividing into parts is done to understand a system's principle. Analysis helps to comprehend the system's functional parts. Synthesis or assembly is linked with assembling the system from physical models. Hence, there is often talk of functional analysis and modular synthesis. Both analysis and synthesis should be conducted. One can't focus on just one task.];
* modular=constructive=synthetic;
* spatial=location=placement;
* cost=economic=resource-based.