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

server.user(
    name="devuser в группе docker (docker без sudo)",
    user="devuser",
    groups=["docker"],
    append=True,  # добавить в группу, а не заменить список групп
    _sudo=True,
)
