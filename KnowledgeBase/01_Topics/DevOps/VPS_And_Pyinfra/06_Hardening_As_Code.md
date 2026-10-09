# Шаг 6. Защита сервера как код

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[05_First_Inventory_And_Deploy]] · Следующий: [[07_Next_Steps]]

Переписываем шаги 1–3 одним деплоем: пользователь, ключи, sshd, UFW, fail2ban, автообновления. На новом сервере aeza это будет единственное, что нужно запустить.

## Файлы рядом с deploy.py

`files/sshd_hardening.conf` — drop-in, который уйдёт в `/etc/ssh/sshd_config.d/`:

```sshconfig
PermitRootLogin no
PasswordAuthentication no
```

`files/jail.local`:

```ini
[sshd]
enabled = true
```

Кладём в `files/` и **свой публичный ключ**: копируем `C:\Users\<ты>\.ssh\id_ed25519.pub` в `files/id_ed25519.pub` (публичный ключ коммитить можно — он для того и публичный).

## deploy.py

```python
from pyinfra.operations import apt, files, server, systemd

# --- пользователь ---
server.user(
    name="Admin user with sudo",
    user="devuser",
    shell="/bin/bash",
    groups=["sudo"],
    append=True,
    create_home=True,
)

server.user_authorized_keys(
    name="Authorize laptop key",
    user="devuser",
    public_keys=["files/id_ed25519.pub"],  # принимает и пути к файлам
)

# --- пакеты ---
apt.packages(
    name="Base packages",
    packages=["vim", "curl", "htop", "ufw", "fail2ban", "unattended-upgrades"],
    update=True,
)

# --- sshd ---
files.put(
    name="sshd hardening drop-in",
    src="files/sshd_hardening.conf",
    dest="/etc/ssh/sshd_config.d/00-hardening.conf",
    mode="644",
)

systemd.service(
    name="Reload sshd",
    service="ssh",
    running=True,
    reloaded=True,   # перезагружает при каждом прогоне — безопасно, просто шумно
)

# --- firewall ---
server.shell(
    name="UFW: allow OpenSSH and enable",
    commands=[
        "ufw allow OpenSSH",
        "ufw --force enable",
    ],
)

# --- fail2ban ---
files.put(
    name="Enable sshd jail",
    src="files/jail.local",
    dest="/etc/fail2ban/jail.local",
    mode="644",
)

systemd.service(
    name="fail2ban running and enabled",
    service="fail2ban",
    running=True,
    enabled=True,
)
```

`inventory.py` — как в [[05_First_Inventory_And_Deploy]] (`_sudo: True`).

## Запуск — аккуратно

```powershell
pyinfra inventory.py deploy.py --dry   # сначала план
pyinfra inventory.py deploy.py         # потом применяем
```

Проверка после прогона — **в новом окне**: `ssh vps` пускает, `ssh root@IP` отказывает. Текущую сессию держим открытой до результата.

## Что тут учебного

- `server.user_authorized_keys` понимает пути к файлам — ключ не надо вставлять строкой в код.
- `files.put` + `systemd.service(..., reloaded=True)` — простой рабочий вариант «применить конфиг». «Reload только при изменении файла» делается через операции-уведомления — см. доки, [[07_Next_Steps]].
- `server.shell` — императивная операция: выполняется каждый раз (ufw сам идемпотентен, так что безвредно).

## Проверь себя

- [ ] `--dry` показывает осмысленный план, а не ошибки
- [ ] После прогона: `ssh vps` по ключу работает, root не пускает
- [ ] Повторный прогон — изменений почти нет (кроме shell/systemd-операций)

#pyinfra #vps #debian #security
