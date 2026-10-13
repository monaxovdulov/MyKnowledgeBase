# Фаза 1 бутстрапа голого сервера (под root, см. bootstrap_inv.py).
# Создаёт devuser + кладёт твой pubkey. SSH-конфиг НЕ трогает —
# прогон безопасен, локаута быть не может.
# Запуск:  pyinfra bootstrap_inv.py bootstrap.py --ssh-password-prompt
from pyinfra.operations import apt, server

apt.packages(
    name="Base packages (sudo до пользователя — нужен для группы sudo)",
    packages=["sudo", "git", "vim", "curl", "htop"],
    update=True,
)

server.user(
    name="Admin user devuser",
    user="devuser",
    shell="/bin/bash",
    groups=["sudo"],
    append=True,
    create_home=True,
)

server.user_authorized_keys(
    name="Authorize my Windows pubkey",
    user="devuser",
    public_keys=["files/id_ed25519.pub"],  # положи свой pubkey в files/
)
