# Обычный деплой: желаемое состояние сервера кодом.
# Запуск:  pyinfra inventory.py deploy.py
# Сухой прогон (ничего не меняет, только показывает):
#          pyinfra inventory.py deploy.py --dry
#
# Docker ставим из ОФИЦИАЛЬНОГО репозитория docker.com:
# docker-compose-v2 в Debian не существует (это имя пакета Ubuntu),
# а docker.io из bookworm застрял на версии 2023 года.
# Схема та же, что с sshd-drop-in'ами: ключ в /etc/apt/keyrings,
# репо отдельным файлом в /etc/apt/sources.list.d/.
from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.operations import apt, files, server

files.directory(
    name="Каталог для GPG-ключей репозиториев",
    path="/etc/apt/keyrings",
    mode="755",
    _sudo=True,
)

files.download(
    name="GPG-ключ Docker",
    src="https://download.docker.com/linux/debian/gpg",
    dest="/etc/apt/keyrings/docker.asc",
    mode="644",
    _sudo=True,
)

apt.repo(
    name="Репозиторий Docker",
    src="deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable",
    filename="docker",  # → /etc/apt/sources.list.d/docker.list
    _sudo=True,
)

apt.packages(
    name="Docker engine + compose plugin",
    packages=[
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin",  # даёт команду `docker compose` (v2)
    ],
    update=True,
    _sudo=True,
)

files.put(
    name="daemon.json: локальный драйвер логов + live-restore",
    src="files/daemon.json",
    dest="/etc/docker/daemon.json",
    mode="644",
    _sudo=True,
)
# применяется после `sudo systemctl restart docker` (или перезагрузки);
# ротация логов действует только на контейнеры, созданные после рестарта.

server.user(
    name="devuser в группе docker (docker без sudo)",
    user="devuser",
    groups=["docker"],
    append=True,  # добавить в группу, а не заменить список групп
    _sudo=True,
)

# --- Dev-цепочка: сервер = прод + разработка ---

apt.packages(
    name="Dev-пакеты (git и компания)",
    packages=["git", "build-essential", "unzip"],
    _sudo=True,
)

# uv и pnpm ставятся per-user инсталляторами в $HOME — запускаем БЕЗ _sudo
# (как devuser). Guard: ставим, только если бинаря ещё нет — идемпотентно.
if not host.get_fact(File, path="/home/devuser/.local/bin/uv"):
    server.shell(
        name="uv в ~/.local/bin (devuser)",
        commands=["curl -LsSf https://astral.sh/uv/install.sh | sh"],
    )

if not host.get_fact(File, path="/home/devuser/.local/share/pnpm/pnpm"):
    server.shell(
        name="pnpm standalone в ~/.local/share/pnpm (devuser)",
        commands=["curl -fsSL https://get.pnpm.io/install.sh | sh -"],
    )
