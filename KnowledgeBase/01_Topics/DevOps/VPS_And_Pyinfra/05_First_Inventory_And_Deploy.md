# Шаг 5. Первые inventory.py и deploy.py

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[04_Install_Pyinfra_On_Windows]] · Следующий: [[06_Hardening_As_Code]]

Деплой = обычные Python-файлы, которые лежат в git. Два понятия:

- **Inventory** — список хостов и их данных.
- **Operations** — желаемое состояние (декларативно) или команды (императивно).

## Заводим проект

```powershell
mkdir vps-deploy; cd vps-deploy
git init
```

`inventory.py`:

```python
# Каждая переменная-список верхнего уровня — группа хостов.
vps = [
    ("aeza-vps", {
        "ssh_hostname": "ВАШ_IP",
        "ssh_user": "devuser",
        "_sudo": True,           # все операции выполнять через sudo
    }),
]
```

`deploy.py`:

```python
from pyinfra.operations import apt, server

apt.packages(
    name="Base packages",
    packages=["vim", "curl", "htop", "git", "ufw", "fail2ban", "unattended-upgrades"],
    update=True,
)

server.hostname(
    name="Set hostname",
    hostname="vps-minsk",
)
```

## Запускаем

```powershell
pyinfra inventory.py deploy.py
```

pyinfra подключится по SSH, сверит факты с целевым состоянием и применит только недостающее.

## Идемпотентность — главное свойство

Запускаем второй раз — pyinfra отвечает «no changes»: пакеты уже стоят, hostname уже тот. Деплой безопасно гонять сколько угодно раз — он доводит сервер до описанного состояния, а не «выполняет команды заново».

## Полезные флаги

```powershell
pyinfra inventory.py deploy.py --dry      # показать план, ничего не меняя
pyinfra inventory.py deploy.py -y   # без интерактивного подтверждения
pyinfra inventory.py deploy.py -v   # подробнее (-vv ещё подробнее)
pyinfra inventory.py deploy.py --limit aeza-vps   # только один хост из группы
```

## Проверь себя

- [ ] Первый прогон: изменения применились
- [ ] Второй прогон: всё зелёное, изменений нет
- [ ] `pyinfra inventory.py fact apt.AptPackages` показывает установленный `htop`

#pyinfra #vps
