# Деплой на VPS (Ubuntu) за Nginx + HTTPS

Приложение — один Docker-контейнер: фронтенд собирается в статику и отдаётся вместе
с API на порту `8000`. База — SQLite в volume `./data`. Наружу контейнер не публикуется —
доступ идёт через Nginx reverse-proxy с TLS.

Файлы для прода уже в репозитории: `docker-compose.prod.yml`, `.env.example`, `deploy/nginx.conf`.

Ниже замените `protocol.example.com` на свой домен и `you@example.com` на свою почту.

> Предварительно: создайте в DNS **A-запись** домена → публичный IP VPS и дождитесь,
> пока `dig +short protocol.example.com` вернёт ваш IP (иначе Certbot не выпустит сертификат).

---

## 1. Docker

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
docker compose version
```

## 2. Код (ветка beta)

```bash
sudo mkdir -p /opt && cd /opt
git clone https://github.com/SckraT/Meeting-Minutes.git protocol
cd protocol
git checkout beta
```

## 3. Секреты

```bash
cp .env.example .env
openssl rand -hex 32        # скопировать вывод в SECRET_KEY
nano .env                   # задать SECRET_KEY и FIRST_ADMIN_PASSWORD
```

- `SECRET_KEY` — подпись JWT; смена ключа разлогинит всех. В git не коммитится.
- `FIRST_ADMIN_PASSWORD` — действует **только при первом старте** (пустая таблица `users`).
  После запуска смените пароль в UI; правка переменной потом ни на что не влияет.

## 4. Запуск контейнера

```bash
sudo docker compose -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.prod.yml ps      # статус → healthy через ~15–30 сек
curl -s http://127.0.0.1:8000/health                   # {"status":"ok","version":"..."}
```

## 5. Nginx

```bash
sudo apt install -y nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/protocol
sudo sed -i 's/protocol.example.com/ВАШ_ДОМЕН/' /etc/nginx/sites-available/protocol
sudo ln -s /etc/nginx/sites-available/protocol /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

## 6. HTTPS (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d protocol.example.com --email you@example.com --agree-tos --redirect
```

Certbot сам перепишет конфиг на `443 + редирект с 80` и поставит таймер автообновления
(`sudo systemctl list-timers | grep certbot`).

## 7. Файрвол

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'    # 80 + 443
sudo ufw enable
```

Порт `8000` наружу **не открываем** — он привязан к `127.0.0.1` в `docker-compose.prod.yml`.

---

## Готово

Откройте `https://protocol.example.com`, войдите под `admin` / вашим паролем и сразу
смените пароль в разделе «Пользователи».

## Обновление версии

```bash
cd /opt/protocol && git pull && sudo docker compose -f docker-compose.prod.yml up -d --build
```

SQLite-база живёт в `/opt/protocol/data/` (volume) и переживает пересборки.
Миграции Alembic применяются автоматически при старте.

## Бэкап

```bash
cp /opt/protocol/data/protocol.db ~/protocol-$(date +%F).db
```
