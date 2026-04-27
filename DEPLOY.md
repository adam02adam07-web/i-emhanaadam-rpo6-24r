# Deployment Guide (Step 06)

## 1) Production settings

Already configured in `core/settings.py`:

- `DEBUG` reads from env var (`DEBUG=1` for local debug, default is `False`)
- `ALLOWED_HOSTS` includes domain and local hosts
- `STATIC_ROOT = BASE_DIR / "staticfiles"`

## 2) Install production package

```powershell
pip install gunicorn
```

## 3) Collect static files

```powershell
python manage.py collectstatic
```

## 4) Run with Gunicorn (Linux server)

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## 5) Example Nginx config

```nginx
server {
    listen 80;
    server_name i-emhana.kz www.i-emhana.kz;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/i-emhana;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 6) Local development mode (optional)

PowerShell:

```powershell
$env:DEBUG="1"
python manage.py runserver
```
