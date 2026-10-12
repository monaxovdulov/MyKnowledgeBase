# Второй сервер за минуты: повторяемый бутстрап

> Карта трека: [[VPS_And_Pyinfra_MOC]]

Первый сервер проходим руками (шаги 1–3) — это обучение. Начиная со второго
«голого сервера» повторять всё вручную не нужно: вся настройка превращается в
**два прогона pyinfra**.

## Что навсегда остаётся ручным

- Получить у провайдера **IP + root-пароль** нового сервера.
- Иметь на ПК свой **публичный ключ** (`id_ed25519.pub`) — он один на все серверы.
- Знать про веб-консоль провайдера как аварийный вход.
- Пароль devuser/root — только в менеджере паролей, нигде в коде.

## Почему две фазы, а не одна

Золотое правило из [[03_Basic_Server_Hardening]]: **парольный вход отключаем
только после того, как вход по ключу проверен**. Поэтому:

1. `bootstrap.py` — создаёт пользователя и кладёт ключ. SSH-конфиг **не трогает**:
   прогон безопасен, локаута быть не может.
2. Проверка руками: `ssh devuser@IP` входит по ключу.
3. Обычный `deploy.py` из [[06_Hardening_As_Code]] — идемпотентен, повторно
   подсунет ключ, поднимет ufw/fail2ban и закроет парольный вход.

## `bootstrap_inv.py` — инвентарь под root

```python
# Инвентарь для первого прогона на голом сервере.
# Пароль root НЕ храним здесь — спросит --ssh-password-prompt.
vps = [
    ("new-server", {
        "ssh_hostname": "НОВЫЙ_IP",
        "ssh_user": "root",
    }),
]
```

## `bootstrap.py` — пользователь + ключ + базовые пакеты

```python
from pyinfra.operations import apt, server

apt.packages(
    name="Base packages (sudo до пользователя — он нужен для группы sudo)",
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
    public_keys=["files/id_ed25519.pub"],  # копия твоего pubkey рядом с deploy-кодом
)
```

`files/id_ed25519.pub` — тот же каталог, что в [[06_Hardening_As_Code]]: берём
`C:\Users\<ты>\.ssh\id_ed25519.pub` и кладём в проект.

## Запуск (PowerShell)

```powershell
pyinfra bootstrap_inv.py bootstrap.py --ssh-password-prompt
# вводим пароль root из панели провайдера (в истории не светится)

ssh devuser@НОВЫЙ_IP        # проверяем вход по ключу + sudo whoami → root

pyinfra inv.py deploy.py    # фаза 2: харденинг + ufw + fail2ban (шаг 6)
```

## Почему pyinfra, а не баш-скрипт

- **Идемпотентность**: повторный прогон не создаёт юзера заново и не дублирует
  ключ — pyinfra сравнивает желаемое состояние с фактическим.
- Скрипт — это уже часть твоего деплоя: bootstrap и обычный deploy лежат рядом и
  используют общие файлы (`files/id_ed25519.pub`, drop-in'ы sshd/fail2ban).
- Несколько серверов = несколько строк в инвентаре, а не несколько скриптов.

## Когда руки всё же нужны

- Первый сервер в жизни — пройти по треку вручную, чтобы понимать код.
- Авария (потерян ключ, нет ssh-agent): веб-консоль провайдера + [[02_SSH_Keys]],
  раздел «Потерял ключ».

#vps #debian #pyinfra
