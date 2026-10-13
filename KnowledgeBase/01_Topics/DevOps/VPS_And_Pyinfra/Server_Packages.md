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

Ставим кодом — `vps-config/deploy.py`, из **официального репозитория** docker.com
(`docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`,
`docker-compose-plugin`). Инструкция: https://docs.docker.com/engine/install/debian/

Почему не пакеты Debian: `docker-compose-v2` — имя пакета Ubuntu, в Debian его
нет вообще (проверено по madison), а `docker.io` в bookworm застрял на версии
2023 года.

```bash
usermod -aG docker devuser   # devuser и агент работают с docker без sudo
# потом relogin — группа применяется при новом входе
```

Дальнейшая настройка демона и гигиена: [[Docker_Best_Practices]].

## Что ставить не нужно

- Ничего для SSH — `sshd` уже работает (иначе бы не вошли), а ключи генерируются на твоём ПК; на сервер уезжает только публичная часть.

#vps #debian
