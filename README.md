## Сокращатель ссылок

## Пример работы можно посмотреть по адресу:

https://safe-click.ru

Логин/пароль для входа в админку: guest/guest


### Быстрый запуск

```bash 
docker-compose build && docker-compose up -d 
```


доступно по адресу: http://localhost:8000

Лоин/пароль по дефолту: admin/password

### Если не запустилось то

```bash 
docker pull python:3.12-slim
```
```bash 
docker pull postgres:16.4
```
```bash 
docker pull redis:8.0.1-alpine
```
```bash 
docker-compose build && docker-compose up -d
```

### Для правильного запуска нужно редактировать файлы:
.env-sample
.env_db-sample
docker-compose.yaml

### Описание:

Использовано: Django, qrcode, psycopg2-binary, pandas, openpyxl, celery, redis, gunicorn

Одиночная ссылка конвертируется сразу и отдаётся пользователю.
Если загружается файл excel, то пользователю отдаётся ссылка на скачивание. Сам файл обрабатывается фоном в Celery.
Если файл очень большой то скачивание не будет доступно какое-то время (об это будет сообщение на странице)

