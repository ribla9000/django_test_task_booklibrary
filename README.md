**StepByStep**:

1.`pip3 install -r requirements.txt` \
2.`python3 manage.py runserver 8000` \

**Features** *rus:
1)	Создание книг – книги имеют название и автора. У одного автора может быть несколько книг
2)	Учет читателей – читатель имеет Фамилию, Имя и Отчество. Один читатель может быть зарегистрирован в библиотеке один раз. Читатель может взять одновременно несколько книг
3)	Учет выдачи книг – фиксация даты, когда была выдана книга читателю и когда она была возвращена читателем
4)	Учет хранения книг – по запросу возможность определить какие книги есть на остатках в библиотеке, какие книги выданы читателям

**Tech**⚙️: \
1. Django \
2. SQLite \
3. CSS \
4. HTML \
5. 10% orm 90% sql query (sqlite)

\
**Description** *rus:
1. Создание карты читателя
2. поиск книг по артиклю
3. кабинет читателя
4. Booking/Unbooking книг
5. Учет кол-ва книг
6. Фильтр по забуканым книгам
7. Добавления обложек
8. Количество книг оставшихся на складе смотрится через поиск по Артиклю (поисковик под навигацией) 
