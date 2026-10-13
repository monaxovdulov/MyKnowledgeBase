# Handoff для агента на сервере (giorno)

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Журнал: [[Practice_Log]] · Планы: [[Deploy_Plan_Giorno]], [[Botops_Restore]]

Документ для агента, работающего локально на VPS (`devuser@giorno`, Debian 12, 2CPU/4GB/60GB). Всё ниже — факты состояния на момент записи и очередь действий. Правила базы: контент на русском, коммиты в `main`, `python3 Scripts/check_structure.py` перед коммитом, секреты не в репо.

## Состояние (проверено)

- SSH только через tailnet (`100.x`), ufw: единственное правило `Anywhere on tailscale0`. Публично открыты только порты контейнера Caddy (80/443 через docker-NAT, ufw их не видит — осознанно).
- Docker-ce + compose из официального репо; `daemon.json`: `log-driver: local`, `live-restore: true`. devuser в группе docker.
- Dev-цепочка: git, build-essential, unzip, uv (`~/.local/bin`), pnpm (`~/.local/share/pnpm`), lazydocker на Windows.
- GitHub с сервера: машинный ключ `~/.ssh/id_ed25519_github` зарегистрирован, `ssh -T git@github.com` → «Hi monaxovdulov». Клоны есть: `~/.agents/skills/botops-deploy`, `~/student-share-codex`, `~/ops-homebase`.
- Botops-инфра поднята через `vps-config/botops.py`: `granit-staging-caddy-1` (caddy:2-alpine, 80/443, Up), сеть `granit-staging_default`, `/srv/botops/{compose.yml,Caddyfile,staging-overrides/}`, `~/bin/botops-*` symlinks, `~/codex-vibe-data` layout.
- **Кандидат на проверку:** `deploy-vibe-router-1` — был restart-луп (mkdir по ro-mount), фикс `ROUTER_ENSURE_LAYOUT=0` в `~/student-share-codex/deploy/.env` + `docker compose -f ~/student-share-codex/deploy/docker-compose.yml up -d`. Проверить: `docker ps` → Up; `docker exec granit-staging-caddy-1 wget -qO- "http://vibe-router:8090/internal/tls-check?domain=x.apps.botops.ru"` → ответ (403 до деплоев — норма).

## Очередь действий

1. **Подтвердить роутер Up** (см. выше). Если ещё Restarting → `docker logs deploy-vibe-router-1 --tail 30` → диагностика, запись затыка в [[Practice_Log]].
2. **Лендинг** (`*.67.barabashka.pro`): проверить `getent hosts <домен>` → если A-записи нет — Roman делает её. Затем `botops-static deploy <slug> <DIST>` (скрипт в `~/bin`, правила slug/артефактов — в `~/.agents/skills/botops-deploy/SKILL.md`). От Roman ждём: выбор slug + откуда взять файлы сайта.
3. **SWAPP**: runtime clone `git clone git@github.com:monaxovdulov/eco-swapp-minsk ~/deploy/swapp` → `.env` по `.env.example` (секреты у Roman'а) → `docker compose --env-file .env -f compose.production.yml -f compose.botops.yml up -d --build db app` → override `/srv/botops/staging-overrides/swapp.caddy` (`tls force_automate`, `reverse_proxy swapp-app:<port>`) → `caddy validate` → `caddy reload` → строка в реестре ops-homebase.
4. **Hermes multi-agent**: профиль `family` первым (свой Telegram-бот → свой `hermes-gateway-family.service`), потом `students`. Секреты — iron-proxy-паттерн. Детали: [[Deploy_Plan_Giorno]] §3.
5. **Харденинг-кодом**: портировать ufw/fail2ban/sshd drop-ins в `vps-config/deploy.py` (шаг 6 трека).

## Правила для агента на сервере

- Не пересоздавать контейнеры/порты без явной причины; `docker -p` голым портом только у Caddy (остальное — bind к IP, см. [[Docker_Best_Practices]]).
- botops-инварианты: slug/build-id форматы, артефакты иммутабельны, `staging-overrides/*.caddy` → сначала `caddy validate`, потом `reload`; реестр `~/ops-homebase/servers/personal-vps-01/botops-apps-registry.md` обновлять после каждого deploy/unpublish.
- Каждый фактический шаг → запись в [[Practice_Log]] + «Текущее состояние» → `check_structure.py` → commit + push (`git push` из клона `~/MyKnowledgeBase`, ключ github уже работает).
- Рабочий каталог базы на сервере: `~/MyKnowledgeBase`; код сервера — `~/MyKnowledgeBase/vps-config/` (запуск `pyinfra inventory.py <file>` локально через `@local`-режим или прямыми командами — pyinfra local connector).

#vps #debian #docker
