# План: три проекта на сервер giorno

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Плановая заметка (что и как деплоим)

База готова: tailnet-only SSH, docker-ce + compose, `vps-config/deploy.py`, docker context на Windows. Дальше — три реальных проекта по нарастающей сложности; каждый переиспользует паттерн предыдущего.

## 0. Общая рамка для всех деплоев

- Порты публикуются осознанно: голый `80:80` — только для публичных сервисов (docker обходит ufw, см. [[Docker_Best_Practices]] п.2). Внутреннее — на `127.0.0.1` или `100.x`.
- Одно приложение = один compose-проект (своя сеть и volumes).
- Секреты — `.env` рядом с compose на сервере, не в git. Пароли генерим длинные случайные (Bitwarden).
- Каждый проект — своя папка под `/home/devuser/`: `ai-projects/<имя>` (как было до вайпа).
- `restart: unless-stopped`, healthcheck, `up -d --wait`, пины версий образов.

## 1. Лендинг — самый простой деплой (учим паттерн «публикация + TLS»)

**Схема:** один контейнер `caddy:2-alpine` + файлы сайта. Caddy сам выпускает и обновляет Let's Encrypt-сертификат по домену.

```
~/ai-projects/landing/
  compose.yml        # caddy + volume со статикой
  Caddyfile          # {$DOMAIN} { root * /srv; file_server; encode zstd gzip }
  site/              # index.html и ассеты (собранные файлы лендинга)
```

**Шаги:**
1. Выбрать домен и направить A-запись на `46.226.165.215`.
2. Положить собранные файлы сайта в `site/` (git clone репо лендинга или scp/rsync собранного бандла).
3. `docker compose up -d` → проверка `https://<домен>`.

TLS выйдет автоматически при первом заходе. Если лендинг чисто статический — альтернатива вообще без контейнера (`caddy` как systemd-сервис), но compose-вариант единообразен со SWAPP.

## 2. SWAPP — основной деплой (compose.production.yml)

Факты из репозитория `eco-swapp-minsk`:

- `compose.production.yml`: `caddy` (80/443+udp, авто-TLS, читает `DOMAIN`), `app` (сборка из `backend/Dockerfile`, FastAPI :8000, healthcheck `/health`), `db` (postgres:18.6, наружу не открыт, volume `swapp-db-data`).
- Обязательные `.env`: `POSTGRES_PASSWORD`, `DOMAIN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_GROUP_CHAT_ID`, `TELEGRAM_GROUP_MESSAGE_URL_PREFIX`, `TELEGRAM_MINI_APP_SHORT_NAME`, `TELEGRAM_WEBHOOK_SECRET`. Шаблон — `.env.example` в репо. Опционально Sentry-* и SUPPORT_*.
- `deploy/Caddyfile`: `{$DOMAIN} { reverse_proxy app:8000 }` + JSON-ответ при 413.

**Шаги:**
1. На сервере: `git clone` репо в `~/ai-projects/eco-swapp-minsk` (нужен доступ к репо с сервера — deploy key или https).
2. `.env` из `.env.example` + реальные значения (токены бота — из BotFather/чата).
3. DNS `swapp.apps.botops.ru` уже указывает на сервер.
4. `docker compose -f compose.production.yml up -d --wait` — первая сборка собирает app-образ локально.
5. Проверка: `https://swapp.apps.botops.ru` открывает mini-app, `/health` отвечает, `docker compose ps` — все healthy.
6. Деплой-поток дальше: `git pull` → `docker --context vps compose -f compose.production.yml up -d --build` с Windows.

Важно: 80/443 станут публичными — это осознанно (первый легальный публичный вход, SWAPP и есть публичный сервис).

## 3. Hermes — много агентов на одной установке

Ресёрч по `NousResearch/hermes-agent` (официальные доки + PR):

**Модель A — профиль на агента (дефолт, рекомендуемая).** `hermes agent add <имя>` создаёт профиль: своя память, скиллы, SOUL.md, модель, свои токены интерфейсов. Каждый профиль = свой процесс-шлюз как systemd user service (`hermes-gateway-<профиль>.service`), рестарт при падении. Это и есть «одна установка — много агентов под разные задачи и интерфейсы»: один Telegram-бот = один агент, другой = второй, Slack-воркспейс = третий. Жёсткая изоляция процессов. Док: `user-guide/multi-profile-gateways.md`.

**Модель B — один мультиплексирующий gateway.** Один процесс принимает сообщения для всех агентов, маршрутизация по `routes:` в `~/.hermes/config.yaml` (платформа/чат/тред/юзер → агент). Экономит RAM и операционку — актуально на 4 GB, когда профилей станет много. Компромисс: слабее изоляция (общий процесс). Дефолт `default_agent: main` — обратная совместимость.

**Безопасность (по SECURITY.md Hermes):** единственная реальная граница — изоляция ОС; терминальный бэкенд `docker` = песочница на агента; секреты через **iron-proxy** (в песочнице только opaque-токены, реальные ключи подменяет прокси на хосте; биндится на docker0-bridge, не 0.0.0.0); egress-фильтрация сети. Чат-шлюзам входящие порты не нужны (long-polling/websocket наружу) — идеально под наш tailnet-only файрвол.

**Шаги:**
1. Установка Hermes на хост под devuser (по официальной инструкции; uv/pip).
2. `hermes agent add <имя>` для каждого агента + токены ботов в профилях.
3. `hermes gateway install`/`start` на профиль — systemd-сервисы.
4. Sandbox-бэкенд: docker (уже есть) + iron-proxy с реальными ключами только в env хоста.
5. Нагрузка: каждый профиль — лёгкий python-процесс; песочницы поднимаются по требованию. На 4 GB начнём с 2–3 агентов, смотрим lazydocker/`docker stats`.

## Ресурсный итог (2 CPU / 4 GB / 60 GB)

- Лендинг: ~20 MB RAM (caddy).
- SWAPP: postgres + FastAPI + caddy ≈ 500–800 MB.
- Hermes: 1 процесс-шлюз на профиль + песочницы по требованию ≈ 300–500 MB на активного агента.
- Запас есть, но `docker stats` и ротация логов (уже в daemon.json) — обязательны.

## Открытые вопросы для Roman

- Какой домен для лендинга и где файлы сайта (какой репо/папка)?
- Токены SWAPP: бот уже создан в BotFather? Есть ли сохранённые значения `.env` со старого сервера (вайп всё стёр)?
- Hermes: какие первые агенты (имена + платформы — Telegram/Slack/др.) и чьи модели/API-ключи?

#vps #debian #docker
