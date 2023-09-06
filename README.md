### Дипломный проект — сайт Foodgram

«Продуктовый помощник» онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии
Python 3.8, Django 3.2, DRF 3.12, Docker, Nginx

## Как запустить проект

Клонировать репозиторий и перейти в директорию для развертывания:

```
git clone git@github.com:ragecodemode/foodgram-project-react.git
cd foodgram-project-react/infra/
```

Переменные окружения, используемые в проекте(для этого создайте и заполните файл .env):

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт
```
В settings.py добавляем следующее:

```
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}
```

Чтобы развернуть проект выполните команду:

```
docker-compose up -d
```
Затем следует сделать миграции и собрать статику.
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```
Остановка проекта осуществляется командой.
```
docker-compose stop
```

## Развёрнутый проект на сервере доступен по ссылке:

 https://158.160.31.210
