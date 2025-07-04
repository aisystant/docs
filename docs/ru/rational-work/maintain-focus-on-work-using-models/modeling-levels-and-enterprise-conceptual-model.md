---
title: "Уровни моделирования и принципиальная модель предприятия"
order: 5
---

# Уровни моделирования и принципиальная модель предприятия

Для моделирования потоков работ мы применим алгоритмы онтологического моделирования, изученные ранее. В частности, пройдемся по уровням моделирования/онтологическим уровням (см подраздел «Онтологические уровни» раздела «Описания и шаблоны описаний»):

|  |  |
| --- | --- |
| **Ме****нтальный мир** | **Физический мир** |
| **(****M****4****)** **Язык записи и неявно выбранные способы описания/неявные предположения:** предположения о том, что BORO более для моделирования работ по методу, чем другие системы типов, … |  |
| **(****M****3****)** **Система типов**: система типов BORO |  |
| **(****M****2****)** **Фундаментальная онтология**: онтология путешествий объектов, онтология потоков |  |
| **(****M****1****)** **Мета-У-модель/прикладная онтология**: онтология работ |  |
| **(****M****1****)** **Мета-С-модель/модель данных/рабочая онтология/шаблон описания**: онтология работ TameFlow, заземлённая для конкретного предприятия |  |
| **(****M****0)** **Э****кземпляры модели****/****модели конкретных объектов****, операционная модель**: описание работы №324 в отчёте | **Объекты физического мира****:** конкретные исполнители, конкретные акты выполнения работ и так далее |

Нам надо будет пройтись по этим уровням и описать онтологию работ так, чтобы после изучения этого раздела вы смогли расшифровать/правильно интерпретировать содержание учебников по операционному менеджменту, в которых предлагаются прикладные онтологии и прикладные способы моделирования потоков (например, учебников Factory Physics от Wallace Hopp, The Book of TameFlow от Steve Tendon и так далее). В этих учебниках хватает дребезга, связанного, например, с отсутствием разделения методов и работ, что сильно мешает пониманию при прочтении и затрудняет моделирование. Нам нужно вывести во внимание эти противоречия и устранить их.

Самый высокий уровень моделирования предполагает обсуждение языка записи и неявных предположений, которые могут повлиять на то, как вы составляете модели. Неявные предположения мы уже обсуждали ранее, кратко повторим тут:

* Полноценно моделировать потоки работ на предприятии имеет смысл, если вы более-менее разобрались с вещью, графом создателей и методами создателей. До этих пор составление модели потоков работ будет бессмысленным, потому что неясно, зачем создатель вообще выполняет работы;
* Операционный менеджер – оператор предприятия, который может управлять только тем конвейером, который ему создали бизнесмен, стратег, методолог, оргпроектировщик, орг-архитектор, лидер, администратор. Он выполняет самые простые действия вида «добавить/убрать ресурса». Многие фундаментальные проблемы, замедляющие выпуск, можно исправить исключительно методами других менеджерских ролей;
* Модель потоков работ может лишь помочь локализовать такие фундаментальные проблемы, а также не терять выпуск по-глупому, например, из-за перегрузки ваших рабочих станций.

С онтологией путешествий объектов и потоков объектов вы уже встречались при изучении раздела «Удержать внимание на сменах состояний объектов». На этом же уровне обсуждают граф создателей вещи, или **принципиальную модель предприятия**, который вы встречали в том же разделе. Графически граф создателей можно изобразить так:

![](/ru/rational-work/58.png)

Но вы наверняка встречались и с другими вариантами визуального представления графа создателей. Например, описание графа создателей в виде схемы бизнес-процессов предприятия:

![](/ru/rational-work/59.png)

*Принципиальная схема производственного предприятия (производство под заказ)*

![](/ru/rational-work/60.png)

*Принципиальная схема типографии*

В учебниках по операционному менеджменту вы найдете еще один вариант графа создателей – модель Demand-Stock-Production (DSP) или Demand-Stock-Transformation, то есть, Спрос–Запасы–Производство или Спрос–Запасы–Изменения/Превращения^[Factory Physics – Wallace Hopp, Mark Spearman]. Модель показывает, как предприятие, получая «на входе» спрос на создаваемую вещь, использует запасы для её создания/производства:

![](/ru/rational-work/61.png)

*Схем**ы**Demand**-**Stock**-**Production* *для производства электронных компонентов и лекарств*

На схемах отражен рыночный спрос/market demand как «входные данные» для предприятия как системы, а также планируемый/прогнозируемый спрос/planned demand. Отражены названия методов производства (fabrication, assembly; mix-tablet-coat, packaging) и показаны функциональные физические объекты – производственные потоки, где выполняются указанные методы (черные прямоугольники со стрелками – Production Flows). Показаны и складские пункты/Stock Points/расположение «складов», где хранятся как материалы для производства, так и частично готовая продукция, которая затем пойдет дальше по цепочке. Даже отражена «незавершенка» в примерном относительном количестве (те по схеме можно понять, в каких местах конвейера скапливается больше незавершёнки, а в каких меньше; но о точных физических количествах мы ничего не знаем).

Благодаря наличию такой модели мы можем обсуждать **выпуск** как количество продуктов/вещей, покидающих границу предприятия, например, количество инженеров-менеджеров, владеющих мастерством:: вещью (обучающие организации изготавливают мастерство как часть агента), использованных покупателями лекарств и прочего. С точки зрения операционного менеджмента такая «вещь» уже известна или определена, и операционные менеджеры, которые эксплуатируют предприятие как конвейер, заботятся о количестве таких вещей, покинувших границу предприятия.

Кроме выпуска, при помощи принципиальной модели мы можем обсудить **скорость выпуска****/****Throughput****rate**, то есть, с какой скоростью вещи в среднем проходят путь от начального состояния до конечного (за границами предприятия!). Действия операционных менеджеров направлены на то, чтобы изменить скорость выпуска, а именно, ускорить его, чтобы предприятие быстрее оборачивало выпускаемые вещи в деньги. Это ключевой интерес операционных менеджеров (по роли). Часто топ-менеджеров (по должности) вы заинтересуете своим проектом или инициативой, если покажете, как он ускоряет выпуск. Или, если речь идёт о сравнении проектов или инициатив, как он позволяет обеспечить рывок (показываете, что рывок, те изменение ускорения, от вашего проекта больше 0 и больше рывка другого).

Чтобы обсудить, что может сделать операционный менеджер для обеспечения рывка, нужно воспользоваться онтологией работ.