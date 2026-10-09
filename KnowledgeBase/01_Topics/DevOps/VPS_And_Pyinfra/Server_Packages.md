# Базовый набор пакетов сервера

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Дополнительная заметка (вне порядка шагов)

Что ставим на голый Debian-сервер и зачем. Список пополняется по мере трека — в конце всё это станет `apt.packages(...)` в deploy-коде (см. [[05_First_Inventory_And_Deploy]]).

## Сразу после первого входа

```bash
apt update && apt upgrade -y
```

На свежем образе aeza копятся 100+ необновлённых пакетов, включая security-фиксы. Делаем до любых других работ.

## Защита (шаг [[03_Basic_Server_Hardening]])

- `ufw` — файрвол
- `fail2ban` — бан за перебор паролей
- `unattended-upgrades` — авто-обновления безопасности

## Рабочие утилиты

- `git` — клонирование репозиториев (деплой SWAPP из git)
- `vim`, `curl`, `htop` — редактор, запросы, мониторинг

## Docker (нужен для SWAPP и любых compose-деплоев)

```bash
apt install -y docker.io docker-compose-v2
usermod -aG docker devuser   # devuser и агент работают с docker без sudo
# потом relogin — группа применяется при новом входе
```

`docker.io` + `docker-compose-v2` — пакеты из репозитория Debian, самый простой путь для личного VPS. Альтернатива — официальный репозиторий Docker (новее версия): https://docs.docker.com/engine/install/debian/

## Что ставить не нужно

- Ничего для SSH — `sshd` уже работает (иначе бы не вошли), а ключи генерируются на твоём ПК; на сервер уезжает только публичная часть.

#vps #debian
