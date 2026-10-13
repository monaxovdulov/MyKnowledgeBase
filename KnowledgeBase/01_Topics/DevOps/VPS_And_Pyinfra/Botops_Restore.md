# Восстановление botops-платформы на giorno

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Связано: [[Deploy_Plan_Giorno]]

Runbook поднятия общей прослойки деплоя после вайпа. Источник истины — README репо `botops-deploy` («Перенос на другой сервер»); сервер тот же (IP совпадает). Вся серверная механика живёт кодом в `vps-config/botops.py` — руками только клоны и github-ключ.

## Что уже есть (не восстанавливаем)

- Docker-ce + compose, devuser, dev-цепочка (git/uv/pnpm) — через `vps-config/deploy.py`
- DNS `*.apps.botops.ru` → `46.226.165.215` (wildcard жив)

## Шаг 1 — прогон с винды

```powershell
cd C:\Users\monax\Desktop\MyKnowledgeBase\vps-config
git pull
pyinfra inventory.py botops.py
```

`botops.py` делает за прогон: каталоги `~/codex-vibe-data/{...}` + `~/bin` + `~/.local/state/botops-deploy` + `~/deploy` + `~/.agents/skills` → машинный ключ `~/.ssh/id_ed25519_github` (без passphrase) + блок `Host github.com` в `~/.ssh/config` + `known_hosts` → **печатает pubkey** → клоны `botops-deploy` / `student-share-codex` / `ops-homebase` (guarded: уже есть → skip; github ещё не принимает ключ → SKIP с подсказкой) → `/srv/botops` + `compose.yml` + `Caddyfile` → сеть `granit-staging_default` → symlinks `~/bin/botops-*` → `.env` роутера → `docker compose up` роутера и общего Caddy.

## Шаг 2 — единственное ручное действие

В выводе прогона напечатан pubkey — добавить его в GitHub (github.com → Settings → SSH and GPG keys → New SSH key; Deploy keys тоже годятся, но они per-repo — ключ придётся добавлять в каждый репозиторий отдельно, поэтому удобнее ключ уровня аккаунта).

## Шаг 3 — повторный прогон

```powershell
pyinfra inventory.py botops.py
```

Клоны докатятся, роутер поднимется (guard видит `deploy/docker-compose.yml` после клона), контейнеры up.

### Ключевые файлы (лежат в `vps-config/files/`)

**`/srv/botops/compose.yml`** (`files/botops-compose.yml`) — `caddy:2-alpine`, `container_name: granit-staging-caddy-1`, порты 80/443 (+udp для HTTP/3), монтирует `Caddyfile` + `staging-overrides → /srv/overrides`, volumes `caddy_data`/`caddy_config`, external-сеть `granit-staging_default`.

**`/srv/botops/Caddyfile`** (`files/botops-Caddyfile`) = референс из `student-share-codex/deploy/Caddyfile` + строка `import /srv/overrides/*.caddy` в конце (именно она подключает маршруты приложений; override с точным доменом `<app>.apps.botops.ru` автоматически перекрывает wildcard-блок).

**`~/student-share-codex/deploy/.env`** (`files/vibe-router.env`) — `CODEX_VIBE_ROOT` и `CODEX_VIBE_HOST_ROOT` = `/home/devuser/codex-vibe-data` (одинаковый путь снаружи и внутри → относительные symlink'и артефактов работают), `ROUTER_PORT=8090`, `CADDY_DOCKER_NETWORK=granit-staging_default`.

### Почему 80/443 работают при «пустом» ufw

Публикация портов идёт через DNAT/FORWARD мимо INPUT-цепочки ufw — та же «дыра», что в [[Docker_Best_Practices]], только здесь она осознанная фича: общий Caddy — единственный легальный публичный вход. Проверить с винды: `curl http://46.226.165.215` → ответ Caddy (не таймаут).

## Проверка

- `docker ps` → `granit-staging-caddy-1`, `deploy-vibe-router-1` Up
- `docker exec granit-staging-caddy-1 wget -qO- "http://vibe-router:8090/internal/tls-check?domain=example.apps.botops.ru"` → ответ роутера (до деплоев — deny, это норма)
- `docker exec granit-staging-caddy-1 caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`
- `curl http://46.226.165.215` с винды → ответ Caddy, не таймаут

## Дальше

- Лендинг → `botops-static deploy <slug> "$DIST"` (см. [[Deploy_Plan_Giorno]] §1)
- SWAPP → `botops-compose deploy` + override `swapp.caddy` (§2)

#vps #debian #docker
