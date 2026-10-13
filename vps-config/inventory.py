# Инвентарь текущего сервера.
# "vps" — это ssh-алиас из ~/.ssh/config (Host vps → 100.x.y.z через tailnet).
# pyinfra использует тот же конфиг OpenSSH, что и команда `ssh vps`.
vps = [
    "vps",
]
