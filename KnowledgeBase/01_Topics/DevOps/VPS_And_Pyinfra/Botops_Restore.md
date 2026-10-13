# Восстановление botops-платформы на giorno

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Связано: [[Deploy_Plan_Giorno]]

Runbook поднятия общей прослойки деплоя после вайпа. Источник истины — README репо `botops-deploy` («Перенос на другой сервер»); сервер тот же (IP совпадает), поэтому просто повторяем по карте.

## Что уже есть (не восстанавливаем)

- Docker-ce + compose, devuser, dev-цепочка (git/uv/pnpm) — через `vps-config/deploy.py`
- DNS `*.apps.botops.ru` → `46.226.165.215` (wildcard жив)

## Зависимость: GitHub-доступ с сервера

`student-share-codex` и `ops-homebase` — приватные (анонимно 404, у Devin нет доступа). Для клонов с сервера нужен ключ/PAT:

```bash
# на сервере, один раз — машинный ключ для github:
ssh-keygen -t ed25519 -C "giorno-devuser" -f ~/.ssh/id_ed25519_github
cat ~/.ssh/id_ed25519_github.pub   # → добавить в GitHub: repo → Settings → Deploy keys (или в аккаунт)
# ~/.ssh/config: Host github.com → IdentityFile ~/.ssh/id_ed25519_github
```

Проверка: `ssh -T git@github.com` → «Hi monaxovdulov».

## Шаги восстановления

```bash
# 1. Код: скилл + router + реестр
mkdir -p ~/.agents/skills ~/deploy ~/bin ~/.local/state/botops-deploy ~/codex-vibe-data/{artifacts,previews,live,state,workspaces,builds,logs,tmp}
git clone https://github.com/monaxovdulov/botops-deploy ~/.agents/skills/botops-deploy
git clone git@github.com:monaxovdulov/student-share-codex ~/student-share-codex   # нужен ключ выше
git clone git@github.com:monaxovdulov/ops-homebase ~/ops-homebase

# 2. Скрипты в PATH
mkdir -p ~/bin
for f in botops-static botops-compose botops-ci-gate botops-ci-setup; do
  ln -sfn ~/.agents/skills/botops-deploy/scripts/$f ~/bin/$f
done
# убедиться, что ~/bin в PATH (echo $PATH; при надобности дописать в ~/.profile)

# 3. Докер-сеть для приложений
docker network create granit-staging_default

# 4. Роутер статики (из student-share-codex/deploy/)
docker compose -f ~/student-share-codex/deploy/docker-compose.yml up -d
# env в нём: CODEX_VIBE_ROOT=/home/devuser/codex-vibe-data, PUBLIC_BASE_DOMAIN=botops.ru,
# ROUTER_PORT, CADDY_DOCKER_NETWORK=granit-staging_default

# 5. Общий Caddy /srv/botops
sudo mkdir -p /srv/botops/staging-overrides && sudo chown -R devuser:devuser /srv/botops
# compose.yml (granit-staging stack: caddy:2-alpine, 80/443) и Caddyfile —
# референс: student-share-codex/deploy/Caddyfile + секция «Перенос» в README botops-deploy
docker compose -f /srv/botops/compose.yml up -d
```

## Проверка

- `docker ps` → `granit-staging-caddy-1`, `deploy-vibe-router-1` Up
- `curl -s http://localhost/internal/tls-check` внутри сети
- `botops-static status <slug>` отвечает

## Дальше

- Лендинг → `botops-static deploy <slug> "$DIST"` (см. [[Deploy_Plan_Giorno]] §1)
- SWAPP → `botops-compose deploy` + override `swapp.caddy` (§2)

#vps #debian #docker
