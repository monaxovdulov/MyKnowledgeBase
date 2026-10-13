# Обычный деплой: желаемое состояние сервера кодом.
# Запуск:  pyinfra inventory.py deploy.py
# Сухой прогон (ничего не меняет, только показывает):
#          pyinfra inventory.py deploy.py --dry
from pyinfra.operations import apt, server

apt.packages(
    name="Docker + compose plugin",
    packages=["docker.io", "docker-compose-v2"],
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
