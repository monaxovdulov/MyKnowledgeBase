"""Поднять botops-прослойку: /srv/botops Caddy + vibe-router + сеть + линки скриптов.

Пререквизиты (руками на сервере, см. KnowledgeBase Botops_Restore.md):
  - github-ключ у devuser (Deploy key / SSH key на github.com)
  - клоны: ~/.agents/skills/botops-deploy, ~/student-share-codex, ~/ops-homebase

Запуск с винды: pyinfra inventory.py botops.py
"""
from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.operations import files, server

DEVUSER = "devuser"
HOME = f"/home/{DEVUSER}"

server.shell(
    name="Каталоги codex-vibe-data и служебные",
    commands=[
        f"mkdir -p {HOME}/codex-vibe-data/{{artifacts,previews,live,state,workspaces,builds,logs,tmp}} "
        f"{HOME}/bin {HOME}/.local/state/botops-deploy {HOME}/deploy"
    ],
)

server.shell(
    name="/srv/botops (+ staging-overrides, владелец devuser)",
    commands=["mkdir -p /srv/botops/staging-overrides && chown -R devuser:devuser /srv/botops"],
    _sudo=True,
)

files.put(
    name="compose общего Caddy",
    src="files/botops-compose.yml",
    dest="/srv/botops/compose.yml",
    user=DEVUSER,
    group=DEVUSER,
)

files.put(
    name="Caddyfile общего Caddy",
    src="files/botops-Caddyfile",
    dest="/srv/botops/Caddyfile",
    user=DEVUSER,
    group=DEVUSER,
)

server.shell(
    name="Сеть granit-staging_default",
    commands=[
        "docker network inspect granit-staging_default >/dev/null 2>&1 "
        "|| docker network create granit-staging_default"
    ],
)

server.shell(
    name="bin symlinks на скрипты botops-deploy",
    commands=[
        f"test -d {HOME}/.agents/skills/botops-deploy && "
        f"for f in botops-static botops-compose botops-ci-gate botops-ci-setup; do "
        f"ln -sfn {HOME}/.agents/skills/botops-deploy/scripts/$f {HOME}/bin/$f; done || true"
    ],
)

if host.get_fact(File, path=f"{HOME}/student-share-codex/deploy/docker-compose.yml"):
    files.put(
        name="vibe-router .env",
        src="files/vibe-router.env",
        dest=f"{HOME}/student-share-codex/deploy/.env",
        user=DEVUSER,
        group=DEVUSER,
    )

    server.shell(
        name="vibe-router up",
        commands=[
            f"docker compose -f {HOME}/student-share-codex/deploy/docker-compose.yml up -d"
        ],
    )
else:
    host.noop("vibe-router пропущен: ~/student-share-codex ещё не склонирован")

server.shell(
    name="Общий Caddy up",
    commands=["docker compose -f /srv/botops/compose.yml up -d"],
)
