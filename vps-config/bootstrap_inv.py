# Инвентарь для ПЕРВОГО прогона на голом сервере (заметка 08_Bootstrap_Second_Server).
# Подставь IP нового сервера. Пароль root сюда НЕ пишем —
# его спросит флаг --ssh-password-prompt.
vps = [
    ("new-server", {
        "ssh_hostname": "НОВЫЙ_IP",
        "ssh_user": "root",
    }),
]
