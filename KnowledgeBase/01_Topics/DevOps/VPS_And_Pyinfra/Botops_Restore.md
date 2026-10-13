# Восстановление botops-платформы на giorno

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Связано: [[Deploy_Plan_Giorno]]

Runbook поднятия общей прослойки деплоя после вайпа. Источник истины — README репо `botops-deploy` («Перенос на другой сервер»); сервер тот же (IP совпадает). Вся серверная механика живёт кодом в `vps-config/botops.py` — руками только клоны и github-ключ.

## Что уже есть (не восстанавливаем)

- Docker-ce + compose, devuser, dev-цепочка (git/uv/pnpm) — через `vps-config/deploy.py`
- DNS `*.apps.botops.ru` → `46.226.165.215` (wildcard жив)

## Шаг 1 — GitHub-доступ с сервера (руками)

`student-share-codex` и `ops-homebase` — приватные. Машинный ключ:

```bash
ssh vps
ssh-keygen -t ed25519 -C "giorno-devuser" -f ~/.ssh/id_ed25519_github
cat ~/.ssh/id_ed25519_github.pub   # → GitHub: repo → Settings → Deploy keys (read-only)
# в ~/.ssh/config:
# Host github.com
#     IdentityFile ~/.ssh/id_ed25519_github
ssh -T git@github.com              # → Hi monaxovdulov
```

## Шаг 2 — клоны (руками, на сервере)

```bash
git clone https://github.com/monaxovdulov/botops-deploy ~/.agents/skills/botops-deploy
git clone git@github.com:monaxovdulov/student-share-codex ~/student-share-codex
git clone git@github.com:monaxovdulov/ops-homebase ~/ops-homebase
```

## Шаг 3 — кодом (с винды)

```powershell
cd C:\Users\monax\Desktop\MyKnowledgeBase\vps-config
git pull
pyinfra inventory.py botops.py --dry
pyinfra inventory.py botops.py
```

`botops.py` делает: каталоги `~/codex-vibe-data/{artifacts,previews,live,state,workspaces,builds,logs,tmp}` + `~/bin` + `~/.local/state/botops-deploy` + `~/deploy` → `/srv/botops` (владелец devuser) → кладёт `compose.yml` + `Caddyfile` → сеть `granit-staging_default` → symlinks `~/bin/botops-*` → `.env` роутера → `docker compose up` роутера и общего Caddy.

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
