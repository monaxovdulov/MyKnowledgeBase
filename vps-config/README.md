# vps-config

Код состояния сервера `giorno` (и будущих VPS) — pyinfra.
Учебный трек: `KnowledgeBase/01_Topics/DevOps/VPS_And_Pyinfra/`.

## Первый запуск на Windows

```powershell
winget install astral-sh.uv     # или: irm https://astral.sh/uv/install.ps1 | iex
uv tool install pyinfra
pyinfra --version
```

## Файлы

- `inventory.py` — текущий сервер. Имя `vps` резолвится через `~/.ssh/config`
  (Host vps → tailscale-адрес 100.x.y.z).
- `deploy.py` — обычный деплой: Docker из официального репозитория docker.com
  (в Debian нет пакета `docker-compose-v2` — это имя Ubuntu), devuser в группе docker.
- `bootstrap.py` + `bootstrap_inv.py` — фаза 1 для НОВОГО голого сервера
  (создать devuser, положить ключ; под root с `--ssh-password-prompt`).
- `files/` — сюда кладёшь свой `id_ed25519.pub` для бутстрапа.

## Команды

```powershell
pyinfra inventory.py exec -- hostname     # связь работает? → giorno
pyinfra inventory.py fact server.Os       # факт с сервера (Debian bookworm)
pyinfra inventory.py deploy.py --dry      # сухой прогон: что бы изменилось
pyinfra inventory.py deploy.py            # применить (docker + группа)
```

После `deploy.py` — перелогин (`exit` + `ssh vps`), потом `docker ps` без sudo.

## Правила

- Секреты и приватные ключи — никогда в репозиторий (см. `.gitignore`).
- Сначала `--dry`, потом реальный прогон.
- Новый сервер: `bootstrap_inv.py` (IP + root) → `bootstrap.py` → проверка
  `ssh devuser@IP` → дальше обычный `deploy.py`.
