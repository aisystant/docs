---
order: 8
title: Main Descriptions of the System as a "Transparent Box"
---

In systems modeling, we always start by focusing on the **areas of interest of the supersystem**^[One of the skills of systems thinking: the first step of attention is always outside the boundary of the target system, and the second step is inside the system.]—we define external project roles, their needs, and subjects of interest. Only then do we turn to the configuration of the target system, which we'll discuss in this section. In the next section, Section 7, you will learn about the specifics of modeling system creation.

The target system is viewed as a "black box" and as a "transparent box."

A system as a black box is described through its role behavior and function, subjects of interest, capabilities (needs), and external project roles. **The system as a "black box"** is conceptualized either as a future system^[That is, design in terms of modeling what kind of system is needed within the supersystem. This is direct engineering.] or an existing one^[Or reverse engineering, where we describe an already functioning system if such a description is unavailable but needed. This is known as reverse engineering.], but in both cases, attention should be paid to the following descriptions of the system:

* as a functional/role object and its behavior in interaction with the environment during operation;
* as a structural object, represented in the physical world and occupying space during operation;
* as the total cost of ownership of the system.

Note that from these descriptions of the system as a "black box," the description of the system as a "transparent box" follows. The internal description is an intrinsic consequence of the external one. For example, in Section 3, we talked about the role of an architect who defines the structural (modular) configuration of the system based on the architectural subjects of interest of the system.

In this subsection, **we will discuss** **how the internal configuration** of the system **is described** as a "transparent box." The notional "division" of a system into parts can be done in various ways^[If different people look at a kitten, they will see different things. A veterinarian will see the biological makeup of the kitten, while a grandmother sees a warm and fluffy object. A system can be divided based on materials used (metal, plastic, glass, etc.) or by the colors of its parts (black, white, or colored) or the shapes of components (round, square, etc.).]. Here are four main ways to divide a system into parts, along with corresponding descriptions, using the example of a "teapot":

* Some are interested in the functions of the parts during operation and will say that a teapot consists of a vessel, a pouring spout, a fill hole in the vessel, a handle on the vessel, a lid, and a handle on the lid, as well as a steam release hole in the lid, otherwise, water will splash out when closing a wet lid. This represents the **functional description** of the teapot system. Describing subsystems as role (functional) objects is known as **systems partitioning**.
* Another person might note that the teapot consists of only two parts that need to be manufactured, as their interest lies in the time of manufacturing the teapot. Here the subject of interest is in its construction, specifically "what to make" or "how to assemble." This is the **modular (product) description** of the system.
* A third might say the lid and the teapot should be stored together, ideally with the lid remaining on the teapot. This emphasizes spatial concerns, meaning "where the parts of the teapot are located in the Universe." This is the **description of places, placements (spatial description)** of the parts within the system.
* A fourth talks about the cost of the teapot parts, focusing on the expenses and other resources involved. This is the **cost description**, which is part of the description of total system ownership as a "black box."

Systems thinking involves multiple depictions of the system. However, four main types of descriptions or perspectives on dividing a system into parts are highlighted^[Recently, there has been an emphasis on subjects of interest related to the tasks carried out with system components.]. The main decisions on the system's configuration are called the **systems concept**. A system concept is not developed only once; it gradually becomes more detailed until the description's precision is sufficient for its manufacture on a production platform. Thus, the system concept is "alive," evolving during development, and the system is continuously modified even after its operation starts.

To compose each of these descriptions of the system, specific practices or **methods of description** must be employed. Through this method, a specific working product is achieved. For example, using a management accounting description method yields a financial description of the enterprise system, interesting to a manager.

Notice that these descriptions do not coincide with one another. Notably, it’s **difficult to notice the mismatch between functional and modular descriptions**. Typically, developers define the system's primary function and view it as a functional object composed of functional subsystems. Then, the architect determines which constructive modules (executors) will fulfill these roles. However, the alignment between functional and modular parts doesn't necessarily need to be 1:1, and their names can vary. Consider the example of scissors, where the functional parts are the blade assembly and handle, while the modular parts are half 1 and half 2.

In systems projects, functional analysis is performed, meaning dividing into parts (analysis involves division), and modular synthesis, meaning assembly. Be wary of a project when it is unclear who makes the synthesis decisions. Such projects usually employ analysts, but they do not change the world. It is synthesis and synthesis decisions that transform the world!

Thus, a person with a systems approach can view any system's structure as a "transparent box," highlighting at least four subjects of interest:

* functional=role=analytical^[Usually, analysis or division into parts is done to understand the system's principle of construction. Thus, analysis helps understand the functional parts of the system, while synthesis or assembly is related to assembling the system from physical models. Therefore, functional analysis and modular synthesis are often discussed. Both analysis and synthesis must be conducted. It's inadequate to focus solely on one or the other.];
* modular=constructive=synthetic;
* spatial=place=placement;
* cost=economic=resourceful.