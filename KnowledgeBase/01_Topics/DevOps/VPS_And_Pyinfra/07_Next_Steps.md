# Шаг 7. Куда дальше

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[06_Hardening_As_Code]]

Базовый цикл пройден: сервер из «root + пароль» превращён в управляемый кодом хост. Куда расти дальше.

## Читать состояние: факты

```powershell
pyinfra inventory.py fact server.Os
pyinfra inventory.py fact apt.AptPackages
pyinfra inventory.py fact server.Users
```

Внутри `deploy.py` факты доступны как `host.get_fact(...)` — можно ветвить логику по ОС, пакетам, файлам.

## Тестировать без риска: Docker-коннектор

```powershell
pyinfra @docker/debian:bookworm exec -- hostname
pyinfra @docker/debian:bookworm deploy.py
```

Каждый прогон — свежий контейнер (нужен Docker Desktop). Дешёвый полигон для деплоя перед боевым сервером. Нюанс: на свежем контейнере всегда будут изменения — идемпотентность проверяем в том же контейнере (`@docker/<ID>`).

## Несколько серверов

Добавляем хосты в группу `vps` в `inventory.py` — операции идут по всем хостам параллельно. Общие данные выносятся в `all.py` / group_data рядом с inventory.

## Безопасность секретов

- Пароли не в коде: доступ только по ключам — см. [[02_SSH_Keys]].
- sudo-пароль при необходимости: `--use-sudo-password` спросит интерактивно, не надо класть его в inventory.

## Что добавлять в деплой дальше

- `server.swap` / файл подкачки
- `docker.*` — установка Docker и контейнеры
- `apt.packages` + `files.put` — nginx, certbot, свой сайт
- `crontab.crontab` — бэкапы по расписанию

## Куда смотреть

- Операции по модулям: https://docs.pyinfra.com/en/3.x/operations.html (`apt`, `files`, `server`, `systemd`, `docker`…)
- CLI и флаги: `pyinfra --help`
- Коннекторы: `@docker/...`, `@local`, SSH

#pyinfra #vps
