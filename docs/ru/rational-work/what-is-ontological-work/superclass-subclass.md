---
title: "Надкласс — подкласс"
order: 23
---

# Надкласс — подкласс

Мы обсуждали уже, что и категории могут быть тоже категоризированы. Давайте поймём, что это значит в более строгом смысле, и как это может быть выражено в новых терминах.

Оказывается, есть два формальных (точно определённых, онтологических) отношения, которые могут быть так описаны. Сначала обсудим **первое из них**.

Мы говорили, что категория «Шуруповёрт Makita» относится к категории «Шуруповёрт»

На «бытовом» уровне мы понимаем, что любой шуруповёрт, выпущенный фирмой Makita, является шуруповёртом.

Мы объединяем все столы (конкретные физические объекты) в класс «*Стол*», это отношение «экземпляр класса – класс».

Некоторые из столов (сделанные из дерева) входят в другой класс — «*Деревянный стол*».

При этом все деревянные столы также входят в класс «*Стол*», то есть один класс включает в себя все экземпляры другого класса.

Мы говорим, что «*Деревянный стол*» - ***подкласс*** класса «*Стол*». А «*Стол*» - ***надкласс*** для класса «*Деревянный стол*».

Все предметы класса «Стол» также входят в класс «Мебель». Получается, что «Стол» — *надкласс* для «Деревянный стол» и *подкласс* для «Мебель».

Точно так же мы понимаем, что любая лошадь – является непарнокопытным, любая лошадь является позвоночным. В обратную сторону такого соотношения нет – не любое позвоночное является лошадью, есть ещё множество других позвоночных, коровы и овцы, например.

Итак, если все элементы класса А принадлежат также классу Б – мы говорим, что класс А ***является подклассом*** класса Б, а класс Б – ***является надклассом*** класса А. Все объекты, которые входят в подкласс, также входят в надкласс.

![](/ru/rational-work/5.png)

На картинке выше – белые желуди (класс «Белый желудь») являются подклассом класса «Желудь». В класс «Желудь» входят разные индивидуальные жёлуди. В класс «Белый желудь» входят только белые жёлуди.

Для отношения ***надкласс-подкласс*** есть гораздо меньше синонимов. Это отношение называют отношением ***специализации*** – подкласс является более узкой выборкой элементов надкласса, это «более специальный» набор элементов. Можно также услышать, что «*класс А* ***входит в*** *класс Б*», «*класс Б* ***шире*** *класса А*».

Обратное отношение называют также ***генерализацией***, так как оно отражает обобщение понятий от подклассов к надклассам.. То же самое имеют в виду, когда говорят, что надклассы выражают ***более абстрактные*** понятия, чем их подклассы. Переход к надклассу – это обобщение, избавление от каких-то черт, свойств и признаков. Поэтому переход от класса к надклассу могут называть ***абстрагированием***, а обратный переход, к подклассу – ***конкретизацией***. Но с этими терминами надо быть осторожнее – иногда их используют и для описания переходов от экземпляров к классам и наоборот!

Математики скажут «***множество А является подмножеством множества Б***» и напишут “***А******⊂******Б***”.

Чтобы определить подкласс для какого-то класса (определить эту более узкую выборку) – обычно указывают такое дополнительное свойство, чтобы *примеров стало меньше*.

Признак «*сделаны из дерева*» является отличительным свойством, определяющим класс «*Деревянный стол*», который уже, чем просто класс «Стол».

И наоборот, если вы хотите отразить в модели новое свойство– определите класс обладающих им объектов как подкласс более широкого класса.

Класс «*Инструмент* *Makita**»* вводится для того, чтобы можно было отмоделировать свойство«*изготовлен фирмой* *Makita*».

Заметим, что иногда люди используют слово «*например*» не совсем так, как мы обсуждали в предыдущем разделе. Можно услышать такое: «*продукты,* *например,* *овощи*». То есть в качестве примера приводится не **экземпляр** класса, а его **подкласс** (ведь понятно, что «Овощ» - подкласс для «Продукт питания»). Хорошо ли, что в ответ на просьбу *привести пример* вам отвечают *чуть менее абстрактно,* указывают **более узкий класс**? Этого может оказаться вполне достаточно для понимания, но это редко проясняет ситуацию до конца. Мы в руководстве будем следить за различением примеров (экземпляров) и более узких классов (подклассов).