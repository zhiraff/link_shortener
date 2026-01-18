import os
workers = os.getenv("gunicorn_workers", 3)
timeout = os.getenv("gunicorn_timeout", 780)
bind = os.getenv("gunicorn_bind", "0.0.0.0:8000")
reload = os.getenv("gunicorn_reload", True)


