"""Поднять botops-прослойку: /srv/botops Caddy + vibe-router + сеть + линки скриптов.

Пререквизит — одно ручное действие: после первого прогона добавить
выведенный pubkey в GitHub (Settings → SSH keys или Deploy keys репо),
затем перезапустить — клоны и контейнеры докатятся повторным запуском.

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
        f"{HOME}/bin {HOME}/.local/state/botops-deploy {HOME}/deploy {HOME}/.agents/skills"
    ],
)

server.shell(
    name="github-ключ devuser (id_ed25519_github, без passphrase — машинный)",
    commands=[
        f"mkdir -p {HOME}/.ssh && "
        f"test -f {HOME}/.ssh/id_ed25519_github || "
        f"ssh-keygen -t ed25519 -N '' -C giorno-devuser -f {HOME}/.ssh/id_ed25519_github"
    ],
)

server.shell(
    name="Host github.com + known_hosts в ~/.ssh/config",
    commands=[
        f"touch {HOME}/.ssh/config {HOME}/.ssh/known_hosts && "
        f"grep -q id_ed25519_github {HOME}/.ssh/config || "
        f"printf 'Host github.com\\n    IdentityFile ~/.ssh/id_ed25519_github\\n' >> {HOME}/.ssh/config && "
        f"grep -q '^github.com' {HOME}/.ssh/known_hosts || "
        f"ssh-keyscan -t ed25519 github.com >> {HOME}/.ssh/known_hosts 2>/dev/null"
    ],
)

server.shell(
    name="pubkey для GitHub — добавить в Settings → SSH keys",
    commands=[
        f"echo '=== добавь эту строку в GitHub: Settings -> SSH and GPG keys -> New SSH key ===' "
        f"&& cat {HOME}/.ssh/id_ed25519_github.pub"
    ],
)

for _repo, _dest in (
    ("botops-deploy", f"{HOME}/.agents/skills/botops-deploy"),
    ("student-share-codex", f"{HOME}/student-share-codex"),
    ("ops-homebase", f"{HOME}/ops-homebase"),
):
    server.shell(
        name=f"git clone {_repo}",
        commands=[
            f"test -d {_dest} || git clone git@github.com:monaxovdulov/{_repo} {_dest} "
            f"|| echo 'SKIP: pubkey ещё не добавлен в GitHub — добавь и перезапусти botops.py'"
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
