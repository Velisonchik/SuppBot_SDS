# SuppBot_SDS
Это корпоративный бот для создания быстрых задач, и фиксации потраченного времени на те или иные задачи, которые не были заведены в Redmine. 



<h2>Install:</h2>
<pre>pip3 install -r requirements.txt</pre>

Для работы бота:
1. <a href=https://habr.com/ru/companies/first/articles/654627/>Добавить</a> в свой Active Directcory атрибут telegramID 
2. Заполнить reqs_samaple.py своими данными
3. Переименовать reqs_samaple.py в reqs.py
4. <pre>python3 main_bot.py</pre>

<h2>Quick start guide</h2>
1. Атрибут <i>(telegramID)</i> твоего юзера в AD должен быть заполнен, в нашем случае он автоматически заполняется при авторизации в <a href=https://t.me/sds_corp_bot> корпоративном боте </a><br>
2. Пишем <a href=https://t.me/sds_fast_issue_bot> боту </a> по созданию уже выполненных задач. Если что то не понятно пишем <b>/help</b> боту.

<h2> Help: </h2>

Какие атрибуты я поддерживаю?<br>
Атрибутов всего три:
1. <i>Необязательный</i> атрибут <b>a</b>, используется что бы явно указать автора задачи.<br>
	<h4>Приоритет по которому выбирается автор задачи:</h4>
		1. Автор пересылаемого сообщения<br>
		2. Инструкция в тексте в виде "a=<имя_пользователя_в_AD>"<br>
		3. Сотрудник написавший сообщение.
	<h4>Примеры использования </h4>
		<pre>Исправлял ТГ бота t=1 j=i <b>a=ivanov.i</b></pre><br>
2. <i>Обязательный</i> атрибут <b>t</b>, используется что бы указать сколько было потрачено <b>часов</b> по этой задаче.<br>
Время необзходимо указывать в <b>часах</b>, т.е. <b>t=0.4</b> или <b>t=2</b>, скрипт определяет дробную часть по <b>точке</b> или <b>запятой.</b>
	<h4>Примеры использования:</h4>
    		<pre>Исправлял ТГ бота <b>t=2</b> j=i</pre><br>
		<pre>Исправлял ТГ бота <b>t=0.3</b> j=i</pre><br>
3. <i>Обязательный</i> атрибут <b>j</b>, используется что бы указать тип задачи "j=[e|c|i]" где e-ошибка, c-консультация, i-улучшение.
	<h4>Примеры использования </h4>
    		<pre>Улучшил ТГ бота t=2 <b>j=i</b></pre><br>
		<pre>Исправил ошибку ТГ бота t=0.3 <b>j=e</b></pre><br>

Поддерживается форвард сообщений и <i>даже с вложениями</i>:
1. По вложениями все просто:
	1. Вложение будет прикрепелно к задаче, если тип вложения: <b>фото или документ</b>
    2. Даже если вложений будет несколько прикрепиться только одно вложение, последнее.
2. Комментарии при форварде:
	1. При форварде сообщения, тема и описание для задачи будут взяты из сообщения которое зафорвардили.
    2. Ваш текст при форварде будет учтен в задачу в виде комментария, <b>нет текста к форварду, нет комментария.</b>
