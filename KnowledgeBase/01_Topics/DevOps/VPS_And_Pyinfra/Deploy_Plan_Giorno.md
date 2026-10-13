# План: проекты на сервер giorno (через botops-платформу)

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Плановая заметка (что и как деплоим)

База готова: tailnet-only SSH, docker-ce + compose, `vps-config/deploy.py` (docker + daemon.json + dev-цепочка git/uv/pnpm), docker context на Windows.

**Ключевое изменение плана:** у Roman уже есть готовая деплой-платформа — скилл [botops-deploy](https://github.com/monaxovdulov/botops-deploy), написанный под ЭТОТ сервер (IP совпадает). После вайпа её надо поднять заново — и все приложения идут через неё, а не через свои контейнеры-Caddy.

## 0. Восстановление botops-инфраструктуры (первым шагом)

Общий прокси-слой: один Caddy на 80/443 для всех проектов + on-demand TLS.

- `/srv/botops/` — compose общего Caddy (`granit-staging-caddy-1`) + `Caddyfile` + `staging-overrides/`
- Docker-сеть `granit-staging_default` (external) — точка подключения приложений
- `deploy-vibe-router-1` — роутер статики + `/internal/tls-check` (репо `monaxovdulov/student-share-codex`, есть на GitHub)
- `/home/devuser/codex-vibe-data/` — artifacts/previews/live symlink-модель статики
- Скилл: clone `botops-deploy` → `~/.agents/skills/botops-deploy`, symlink'и `botops-*` в `~/bin/`
- `ops-homebase` — реестр (clone с GitHub)
- DNS `*.apps.botops.ru` → wildcard уже на сервере

Всё это описано в `README.md` репо botops-deploy («Перенос на другой сервер») — сервер у нас тот же, восстановление по этой карте.

## 1. Лендинг — `botops-static`

Домен у Roman — `*.67.barabashka.pro` (не botops.ru → сначала проверить `getent hosts <домен>`; нужна A-запись на `46.226.165.215`).

Два варианта:
- `<slug>.apps.botops.ru` — штатный путь: `botops-static deploy <slug> "$DIST"` (артефакт → preview → smoke → атомарный live-symlink → внешний smoke; rollback одной командой).
- Свой домен barabashka.pro — override-маршрут `/srv/botops/staging-overrides/landing.caddy` → `botops-static` всё равно хранит сборки, а Caddy смотрит на live-symlink либо прокси. Точную механику берём по `references/docker.md` при выполнении.

Файлы сайта: собранный `DIST` с `index.html` в корне (без src/.git/node_modules) — откуда брать, уточняем при деплое.

## 2. SWAPP — `botops-compose` (уже интегрирован!)

В репо `eco-swapp-minsk` уже лежит `compose.botops.yml`: app подключается к `granit-staging_default` с алиасом `swapp-app`, свой caddy НЕ запускаем (80/443 держит общий Caddy). Запуск:

```
docker compose --env-file .env -f compose.production.yml -f compose.botops.yml up -d --build db app
```

**Шаги:**
1. Runtime clone: `git clone` → `/home/devuser/deploy/eco-swapp-minsk` (repo ≠ runtime, отдельно от dev-копий).
2. `.env` — обязательные: `POSTGRES_PASSWORD`, `DOMAIN=swapp.apps.botops.ru`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_GROUP_CHAT_ID`, `TELEGRAM_GROUP_MESSAGE_URL_PREFIX`, `TELEGRAM_MINI_APP_SHORT_NAME`, `TELEGRAM_WEBHOOK_SECRET`.
3. `.botops-deploy.env`: `BOTOPS_COMPOSE_PROJECT`, `BOTOPS_COMPOSE_ARGS`, `BOTOPS_SERVICES="app db"`, `BOTOPS_HEALTH_URL=http://swapp-app:8000/health`, `BOTOPS_PUBLIC_URL=https://swapp.apps.botops.ru/`, `BOTOPS_BRANCH`.
4. `botops-compose deploy /home/devuser/deploy/eco-swapp-minsk --latest` (код 2 ожидаем — маршрута ещё нет).
5. Маршрут: `/srv/botops/staging-overrides/swapp.caddy` → `caddy validate` → `caddy reload` → smoke `https://swapp.apps.botops.ru`.
6. Строка в реестре ops-homebase.

## 3. Hermes — много агентов на одной установке

Первые агенты (от Roman): **семейный** (организация быта) → дальше **для студентов** (геймификация обучения, домашки, организационное).

**Модель A — профиль на агента (рекомендуемая).** `hermes agent add <имя>` → свой профиль (память, скиллы, SOUL.md, модель, токены интерфейсов) + свой процесс-шлюз `hermes-gateway-<профиль>.service` (systemd user). Один агент = один Telegram-бот/интерфейс. Жёсткая изоляция процессов. Док: `user-guide/multi-profile-gateways.md`.

**Модель B — мультиплекс-gateway** (экономия RAM): один процесс на всех, маршрутизация по `routes:` в `~/.hermes/config.yaml`. На 4 GB может понадобиться позже.

**Безопасность:** docker-песочница на агента (terminal backend) + iron-proxy (opaque-токены, реальные ключи только на хосте); чат-шлюзам входящие порты не нужны — под tailnet-only файрвол идеально.

**Шаги:** установка Hermes под devuser → `agent add family` (+ Telegram-бот токен) → `gateway install`/`start` → docker-сандбоксы + iron-proxy → второй агент `student` аналогично.

## Ресурсы (2 CPU / 4 GB / 60 GB)

Caddy+router ~50 MB · лендинг в router ~0 · SWAPP ~500–800 MB · Hermes ~300–500 MB на активного агента. `docker stats` + local-логи (уже в daemon.json) обязательны.

## Открытые вопросы

- Лендинг: какой slug/финальный домен и где собранные файлы (какой репо)?
- SWAPP: есть ли живые токены бота (вайп стёр старый `.env`)?
- Hermes: API-ключи моделей для профилей (через iron-proxy на хосте)?

#vps #debian #docker
