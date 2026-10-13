# Docker: актуальные практики для личного VPS

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Дополнительная заметка (вне порядка шагов)

Ресёрч по официальной документации Docker (docs.docker.com) и трекеру moby — что реально стоит настроить на маленьком VPS (2 CPU / 4 GB / 60 GB) под будущий SWAPP.

## 1. daemon.json — две настройки, которые стоит иметь сразу

`/etc/docker/daemon.json` (кладёт `vps-config/files/daemon.json` через pyinfra):

```json
{
  "log-driver": "local",
  "live-restore": true
}
```

- **`"log-driver": "local"`** — дефолтный `json-file` **не ротирует логи**: контейнер с болтливым выводом за недели съест весь диск (60 GB — мало). Docker официально рекомендует `local`: ротация включена по умолчанию, формат компактнее. Источник: [docs.docker.com/config/containers/logging/configure](https://docs.docker.com/config/containers/logging/configure)
- **`"live-restore": true`** — контейнеры продолжают работать при рестарте/обновлении dockerd (обновление docker-ce через `apt upgrade` больше не роняет прод). Источник: [docs.docker.com/engine/daemon](https://docs.docker.com/engine/daemon)

Применяется: `sudo systemctl restart docker`. Ротация логов действует только на контейнеры, созданные **после** рестарта.

## 2. Главный готча: Docker обходит ufw

`-p 8080:80` у контейнера пробивает дыру **мимо ufw**: публикация идёт через DNAT в цепочке FORWARD, а ufw правит цепочку INPUT — его «пустого» файрвола Docker вообще не видит. Снаружи твой сервер «пустой» только пока ни один контейнер не опубликован. Источники: [docs.docker.com/engine/network/firewall-iptables](https://docs.docker.com/engine/network/firewall-iptables), [moby#45524](https://github.com/moby/moby/discussions/45524) (десятилетняя болячка, `ufw` + `docker -p` — классика инцидентов с открытыми БД).

**Правило для нашего сетапа — всегда биндить порт к конкретному адресу:**

```yaml
ports:
  - "127.0.0.1:8080:80"        # только с самого сервера (отладка)
  - "100.x.y.z:5432:5432"      # только внутри tailnet (база, админки)
  - "80:80"                    # публично — только для caddy SWAPP (это и цель)
```

Если понадобится явная блокировка поверх — правила пишут в цепочку `DOCKER-USER` (`iptables -I DOCKER-USER ...`), не в ufw.

## 3. docker context — управлять с Windows без входа по SSH

docker-клиент умеет ходить по ssh — использует тот же алиас `vps` через tailnet:

```powershell
# на Windows, один раз (Docker Desktop или docker CLI):
docker context create vps --docker "host=ssh://vps"

# дальше все команды «на сервере» — с винды:
docker --context vps ps
docker --context vps compose -f compose.production.yml up -d
```

Это и будет рабочий способ деплоя SWAPP: локально правишь compose → `docker --context vps compose up -d`.

**TUI-аналог Docker Desktop — lazydocker** (от автора lazygit): контейнеры, образы, volumes, логи, статы, compose — всё в терминале с винды, работает поверх context:

```powershell
winget install -e --id JesseDuffield.lazydocker
docker context use vps
lazydocker
```

Мелкие аналоги: `ctop` (htop по контейнерам), `dive` (разбор слоёв образа).

## 4. Гигиена compose-файлов

- `restart: unless-stopped` — сервис переживает ребут и падения.
- `healthcheck` + `depends_on: condition: service_healthy` — `app` стартует после готовой `db`, а не после запущенной.
- `.env` рядом с compose-файлом для секретов (`POSTGRES_PASSWORD` и т.д.) — **не в git** (уже в `.gitignore` проекта).
- Образы пиновать версией (`postgres:18.6`, не `latest`) — повторяемый деплой.
- Данные — в named volumes, не в bind-монты по всему диску.
- Одно приложение = один compose-проект (`-p имя` или папка) — изоляция сетей и volumes.
- `docker compose up -d --wait` — ждёт healthcheck'и вместо «упал через минуту».

## 5. Диск на 60 GB — регулярная подметка

Образы/кэш/остановленные контейнеры копятся быстро:

```bash
docker system df          # сколько занято чем
docker system prune -f    # остановленные контейнеры, висячие образы, неиспользуемые сети
docker builder prune -f   # build-кэш (может быть гигабайты)
```

Дальше по желанию — systemd-таймер с еженедельным `docker system prune -f` (кодом, в deploy.py).

## 6. Границы безопасности (коротко)

- Группа `docker` = фактический root (монт `/` в контейнер = полный доступ). Для devuser-админа это приемлемо и осознанно; не давать её сервисным пользователям приложений.
- Никогда `-H tcp://0.0.0.0:2375` — нешифрованный сокет демона в сеть = мгновенный рут для всех.
- Образы — только официальные/доверенные (`postgres`, `caddy`, свой собранный).
- rootless docker (демон без root) — продвинутый вариант «на вырост», сейчас не нужен.

## Что уже сделано у нас

- Docker-ce + compose plugin из официального репозитория (deploy.py)
- `daemon.json` с local-логами и live-restore — в deploy.py
- Порядок: `docker --context vps` и/или pyinfra для дальнейших сервисов

#vps #debian #docker
