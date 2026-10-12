# Tools

## Инфраструктура и автоматизация

- [pyinfra](https://github.com/pyinfra-dev/pyinfra) — agentless IaC на Python: настройка серверов по SSH, деплой = обычный Python-код. Доки: https://docs.pyinfra.com
- [uv](https://github.com/astral-sh/uv) — менеджер Python-инструментов; рекомендуемый способ ставить pyinfra (`uv tool install pyinfra`).

## SSH и доступ

- OpenSSH Client — встроен в Windows 10/11 (`ssh` в PowerShell); им же пользуется pyinfra.
- [PuTTY](https://www.putty.org/) — альтернативный SSH-клиент для Windows.
- Веб-консоль в панели aeza — аварийный вход на VPS, если потерян SSH.

## Пароли и секреты

- [Bitwarden](https://bitwarden.com/) — менеджер паролей: бесплатный, open source, синхронизация ПК↔телефон, браузерное расширение, генератор паролей. Запоминаем один мастер-пароль.
- [KeePassXC](https://keepassxc.org/) — офлайн-альтернатива: база = файл `.kdbx` на твоём ПК, без аккаунта и облака; синхронизацию между устройствами делаешь сам (файл в облаке/на диске).

## Площадки

- [aeza](https://aeza.net/) — VPS-провайдер (используется в треке [[VPS_And_Pyinfra_MOC]]).
