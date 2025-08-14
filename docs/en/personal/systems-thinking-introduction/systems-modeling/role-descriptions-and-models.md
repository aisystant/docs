---
title: "Role Descriptions and Models"
order: 3
---

# Role Descriptions and Models

In the first section of the course, it was discussed that a system possesses certain classic properties and depends on design roles. We then established that there are numerous subjects of interest regarding a system, and that each description is created for a particular subject of interest.

In the adapted diagram from the ISO 42010 standard^[For more details about this standard, see the textbook "Systems Thinking."], you can see how one might reason about interests in a system, design roles, role-based descriptions, models, and so on. This international standard provides recommendations on how to think about system descriptions.

![](/en/systems-thinking-introduction/Role_Description_and_Model_Tax_Example.png)

The standard itself only addresses architectural descriptions, but its principles can easily be applied to any descriptions of different systems. For example, you can use this framework not just for the system of interest, but also for the creation system.

In practice, everything usually begins with identifying the type of role-based description, which stems from a particular interest. For instance, when it comes to an enterprise, there is a subject of interest—taxes. There are specific design roles (each with their own methods and work artifacts) that have this subject of interest. However, the preferences of a tax officer, a manager, and an accountant regarding this subject of interest may not align.

To address this subject of interest, a tax description is created, which should incorporate all the preferences of the design roles. Each design role has its own desires, but in order to reach an agreement, it is necessary to create a description that is common to all interested^[That is, those who share the same subject of interest.] design roles.

This description consists of specific models. It is relatively straightforward to discuss tax matters because many metamodels are established by the government in the relevant regulatory documents. These include documents such as the "Balance Sheet," "Profit and Loss Statement," and others. When these metamodels are filled in with the appropriate reporting data, they become models—descriptions of a specific enterprise and its business activities.

As you may have guessed, there is a particular method of description used to create this tax description. This is the method of accounting and tax reporting.

The government is concerned with taxes, so it advances its subject of interest by officially approving methods of description (metamodels) and meticulously reviewing the models submitted by accountants. You should take a cue from tax authorities in how much attention they pay to modeling.

However, on the other hand, you must never forget that, in the end, what you need is the implementation of the system, and the description—provided to us in the form of models, drawings, manufacturing instructions, and so on—is only necessary because, without a description, it is very difficult to bring a working system to life.