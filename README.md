# Розробка веб-застосунку для обліку книг у бібліотеці

## Мета завдання

Оцінити навички кандидата в галузі веб-розробки на Python за допомогою фреймворку Django.

## Технічне завдання

https://docs.google.com/document/d/1OsSWOBLObDAJPWmBmH9iN2T6OgfhT658WG6mV7UGqik/edit

## Реалізовано

* Реєстрація та аутентифікація користувачів;
* Сторінка користувача з якої починається навігація
* Сторінка бібліотеки, на якій відображено список існуючих книг у бібліотеці. На сторінці реалізовано:
    - поле пошуку книги, здійснюється пошук : за назвою, автором, жанром, роком написання книги.
    - панель вибору пріоритету сортування книг за наступними критеріями: останні, назвою, датою, прочитані (тільки для
      авторизованих юзерів).
    - завантаження зображення книг, якщо зображення відсутнє використовується зображення за замовчування.
    - знайденні та відфільтровані книги завантажуються за допомогою AJAX на технології HTMX.
    - всі книги які "прочитані" юзером, помічаються галочкою у верхньому правому куті картинки книги.
* Сторінка книги, на ній відображається вся інформація про книгу, можна завантажити книгу.
    - можливість додавання книги до власної бібліотеки юзера.
    - можливість відмітки книги як прочитана, для книг яки додані до власної бібліотеки.
    - обновлення сторінки динамічне, з використання AJAX на технології HTMX.
* Сторінка власної бібліотеки користувача, відображає всі книги які користувач додав до неї. На сторінці реалізовано:
    - можливість фільтрування за прочитаними та непрочитаними книгами або побачити всі.
    - обновлення списку книг після фільтрування - динамічне, застосовується AJAX на технології HTMX.
* Сторінка додавання книги до бібліотеки, проводиться валідація переданих параметрів за допомогою форми. Якщо форма
  валідна, то книга завантажується до бібліотеки.
* Сторінка статистики. Вміщує в собі наступні підсторінки з графіками, які завантажуються динамічно AJAX(HTMX) при
  натисканні кнопок. Для візуалізації використано бібліотеку `Plotly`.
    - статистика за жанрами. Реалізована можливість обирання періодів за роками, для відображення статистик в межах
      заданого історичного інтервалу. Оновлення графіку динамічне AJAX(HTMX).
    - статистика за авторами. Графік, який показує кількість книг для кожного автора у процентах.
    - статистика за прочитаними книгами. Скільки книг прочитано, а скільки залишилося.
    - загальна статистика. Відображає загальну кількість книг у бібліотеці, середній вік книги, а також топ 5
      найчитабельніших жанрів, авторів та книг.
* Написані тести для models, views, forms для застосунку "library". Додано `coverage` для аналізу покриття.
* Сворено Makefile з командами для зручного використання.
* Додано CI/CD pipeline для автоматичного тестування коду при завантаженні на github.
* Створено `Dockerfile` та `docker-compose` файли.

## Розгортання програми

1) Клонуйте репозиторій:

```bash
git clone https://github.com/ArtemSerdechnyi/books_library
   ```

2) Перейдіть до каталогу проекту:

```bash
cd books_library/
```

3) Виконайте команду для збірки Docker-образу:

```bash
sudo docker-compose build
```

4) Запустіть контейнер:

```bash
sudo docker-compose up
```

Для локального запуску проекту використовуйте Makefile. Доступні команди:

```bash
make
```