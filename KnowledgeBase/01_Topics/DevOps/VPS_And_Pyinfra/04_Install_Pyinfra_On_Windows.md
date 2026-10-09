# Шаг 4. Ставим pyinfra на Windows

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[03_Basic_Server_Hardening]] · Следующий: [[05_First_Inventory_And_Deploy]]

pyinfra — это Python-утилита: код-деплой пишется на Python, выполняется по SSH на голом сервере (агенты не нужны — только sshd). Ставится как обычный Python-пакет.

## Способ 1 (рекомендуемый): через uv

В PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install pyinfra
```

## Способ 2: через venv + pip

Нужен установленный Python (python.org, галочка «Add Python to PATH»). Дальше в папке проекта:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pyinfra
```

## Проверяем и делаем первый запуск

```powershell
pyinfra --version

# ad-hoc команда по SSH: pyinfra <инвентарь> <операции>
pyinfra vps exec -- hostname
```

`vps` — это алиас из `~/.ssh/config` из шага [[02_SSH_Keys]]. pyinfra берёт конфиг, ключи и агента текущего пользователя — раз `ssh vps` работает, то и pyinfra подключится.

Без алиаса то же самое явно:

```powershell
pyinfra ВАШ_IP --ssh-user devuser exec -- hostname
```

## Факты — чтение состояния сервера

```powershell
pyinfra vps fact server.Os      # Debian GNU/Linux 12 ...
pyinfra vps fact server.Hostname
```

## sudo

Операции, требующие root, запускаем с флагом `--sudo` (или `_sudo` в данных хоста — см. [[05_First_Inventory_And_Deploy]]):

```powershell
pyinfra vps --sudo exec -- ufw status
```

## Проверь себя

- [ ] `pyinfra --version` отвечает
- [ ] `pyinfra vps exec -- hostname` возвращает имя сервера
- [ ] `pyinfra vps fact server.Os` возвращает Debian

#pyinfra #windows #vps
