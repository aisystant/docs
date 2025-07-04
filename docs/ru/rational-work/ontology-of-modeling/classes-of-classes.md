---
title: "Классы классов"
order: 1
---

# Классы классов

Посмотрим на некоторые нетривиальные примеры категоризации и попробуем тоже перевести их на язык классов (множеств).

На уровне индивидов разных вариантов трактовки отношения «*категоризации*» нет. Категория, объединяющая индивидов – всегда класс, индивиды могут быть только экземплярами класса, отношение между индивидами и классами – всегда *классификация*. Такие классы мы будем называть **классами индивидов**.

Мы уже знаем один вариант интерпретации отношения «*категоризация*» между категориями - когда категоризируемый класс является *подклассом* другого класса, отношение специализации. Но категоризация категорий может иметь и совсем **другой формальный смысл**, принципиально отличающийся от специализации. Это та же самая *классификация*, но не между индивидом и классом, а *между классами*.

Описать мы этот второй смысл мы можем многими способами:

* класс ***является экземпляром*** другого класса;
* класс ***является членом*** другого класса;
* класс ***является элементом*** другого класса;
* класс ***принадлежит*** другому классу,
* класс ***представляе******т***другойкласс;
* класс ***имеет*** тип;
* класс ***относится к*** типу;
* класс **классифицирует** другой класс

Название отношения в этом случае используется из уже известного нам рядасинонимов ***классификаци******и*** ***- принадлежность, типизация, членство,*** ***экземпляризация*****.**

Если класс включает как члены другие классы - мы говорим, что в модели появляется **класс классов.**

(А вот такие классы, в которых элементами являются как индивиды, так и абстрактные объекты, классы – математически возможны, в математике используются, но в онтологическом моделировании мира – практически никогда.)

![](/ru/rational-work/9.png)

На картинке выше в класс «Цвет жёлудя» входят класс «Белый желудь» и класс «Чёрный жёлудь». В класс «Цвет жёлудя» не входит ни одного жёлудя! В класс «Белый желудь» входят только белые жёлуди. В класс «Чёрный желудь» входят только чёрные жёлуди.

Самое важное что надо запомнить – что *в классе классов экземплярами являются классы*. А экземпляры (члены, элементы) экземпляров класса классов – в класс классов не входят.

Как мы говорили, объекты выделяются из фона вниманием, приобретают имена (названия) в естественном языке по его законам, и, когда мы начинаем извлекать из наших представлений о мире формальные онтологические модели, самое главное для нас– это **не запутаться**. Мы много обсуждали раньше: как отличать индивид, физический объект, от категории, класса, абстрактного объекта, элемента ментального пространства. Обсудим теперь, как проверить, является ли выделенный нами абстрактный объект **классом индивидов** или **классом классов**?

Допустим, мы пришли к выводу, что нам нужен в модели абстрактный объект «Вид животных». Нужен потому, что учёные (не онтологи, а биологи) постоянно употребляют этот термин. Что это? Какие члены у этого класса?

Рассмотрим корову Зорьку, конкретный физический объект. Биологи нам уже рассказали про класс «Корова», уровнем выше, чем корова Зорька. Ещё уровнем выше у нас есть класс «Животное»». А ещё есть классы «Лошадь», «Волк» и т.д.

Послушаем, как ученые говорят:

*Зорька – это Корова*

*Корова – это Животное*

*Корова – это Вид животных*

*Лошадь – это Вид животных*

Выглядит всё одинаково. Какое же онтологическое отношение (или разные отношения) скрывается за словом «это»?

С фразой «*Зорька – это Корова*» мы уже умеем разбираться. Зорька – индивид, «Корова» – класс, значит отношение может быть только **классификацией**, «Корова» - **класс индивидов**. Как разбираться дальше?

Давайте попробуем сказать через уровень:

*Зорька – это Животное*

*Зорька – это Вид животных*

Фраза «*Зорька – это Животное*» звучит нормально, всякая корова – животное, поэтому и Зорька – животное. Тут у нас отношение **специализации**, «Корова» - подкласс «Животное».

А вот мы и увидели разницу: вторая фраза звучит бессмысленно, мы чувствуем, что оно напрягает, *дребезжит* (мы уже говорили про «*дребезг**»* как инструмент для настройки нашего чувства правильности).

Поэтому мы делаем вывод – произошла смена отношения, скрывающегося за словом «это». «*Корова – это Вид животных*» - здесь возникло отношение **классификации**.

«Вид животных» –это **класс классов**, его члены – классы «Корова», «Лошадь», «Волк». А корова Зорька – член класса Корова, но не член класса «Вид животных», что и проявилось в бессмысленной фразе.

Классы классов будут появляться в ваших моделях тогда, когда вы будете вводить признаки объектов.

На картинке выше абстрактный концепт «Цвет жёлудя» появился именно так. Теперь понятно, почему в классе «Цвет жёлудя» нет ни одного индивидуального жёлудя – вы ведь чувствуете дребезг во фразе «*найденный вчера на прогулке жёлудь – это цвет жёлудя*»?

**Замечание для системных аналитиков и программистов**

Когда вы проектируете информационную систему – вы создаёте множество справочников (классификаторов) для описания объектов. Каждый такой справочник – это и есть класс классов, его название – имя класса классов. Обычно именно название (имя) класса классов используется как заголовок колонки в интерфейсе программы, а элементы класса классов появляются в поле выбора при заполнении клеточек этой таблицы.

«Пол» - это класс классов, его элементы – это классы «Мужской», «Женский», «Не сообщаю».

«Материал столешницы» - - это класс классов, его элементы – это классы «Дерево», «Металл», «Пластик».

Вы же помните, что «Дерево», «Металл», «Пластик» - это абстрактные объекты, концепты, воплощениями которых являются все вещи в мире, сделанные из соответствующих материалов?