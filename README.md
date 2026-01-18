## Сокращатель ссылок

### Быстрый запуск

```docker-compose up -d ```

доступно по адресу: http://localhost:8000

Лоин/пароль по дефолту: admin/password

### Если не запустилось то

```docker build -t shortener:latest .```
```docker-compose up -d```

### Описание:

Использовано: Django 4.2.27, qrcode, psycopg2-binary, pandas, openpyxl, celery, redis, gunicorn