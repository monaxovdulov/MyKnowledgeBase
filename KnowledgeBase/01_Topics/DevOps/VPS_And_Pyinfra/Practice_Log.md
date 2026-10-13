# Журнал практики

> Карта трека: [[VPS_And_Pyinfra_MOC]]

Фактический лог прохождения трека на живом сервере: что делал, что выводил терминал, выводы. Записываем сюда по мере прохождения шагов.

Сервер: `giorno` (`46.226.165.215`), aeza, Debian 12 bookworm, ядро 6.1 — свежепересозданный (голый) инстанс.

## Текущее состояние (обновлять по ходу)

Точка восстановления на **2026-10-09**:

- ✅ sudo установлен, `devuser` создан (uid 1000) и в группе `sudo`
- ✅ SSH-ключ `id_ed25519` (ed25519, passphrase есть) сгенерирован на ПК (`C:\Users\monax\.ssh\`)
- ✅ pubkey на сервере (`authorized_keys` у devuser) — команда с `-o PubkeyAuthentication=no`, пароль devuser
- ✅ вход `ssh devuser@IP` по ключу проверен — попал в `devuser@giorno` (спросил passphrase ключа)
- ✅ ssh-agent на Windows настроен: `Set-Service ssh-agent` Automatic + `ssh-add` — ключ в агенте, passphrase до перезагрузки не спросит
- ✅ алиас `vps` в `~/.ssh/config` создан — `ssh vps` входит без вопросов (агент + конфиг); pyinfra сможет звать хост по имени `vps`
- ✅ sshd захарден: drop-in `00-hardening.conf` (`PermitRootLogin no`, `PasswordAuthentication no`) + `sshd -t` + `reload`; `ssh vps` входит, `ssh root@IP` → `Permission denied (publickey)` — пароль не спрашивается вообще
- ✅ `apt update && apt upgrade -y` + `apt install ufw fail2ban unattended-upgrades` — выполнены
- ✅ ufw включён: `allow OpenSSH` → `enable` → «Firewall is active and enabled on system startup», сессия не порвалась
- ✅ fail2ban: `jail.local` (`[sshd] enabled = true`) + `enable --now` — запущен
- ✅ **Tailscale готов**: сервер `giorno-1` в tailnet, клиент на Windows, exit node проверен; `ssh devuser@100.x` работает, `HostName` в `~/.ssh/config` → 100.x
- ✅ **ufw финал**: `Anywhere on tailscale0 ALLOW` — единственное правило входа; публичный 22 закрыт (`delete allow OpenSSH`); `deny incoming / allow outgoing`. Снаружи сервер «пустой»
- ✅ Docker установлен **кодом**: `pyinfra inventory.py deploy.py` — docker-ce + compose plugin из официального репо docker.com; `docker ps` без sudo работает
- ✅ pyinfra на Windows работает: `uv tool install pyinfra`, прогон идёт через tailnet (`vps` алиас)
- ✅ репозиторий `vps-config/` создан в корне MyKnowledgeBase: `inventory.py`, `deploy.py`, `bootstrap.py` + `bootstrap_inv.py` (по [[08_Bootstrap_Second_Server]]), `files/` для pubkey и daemon.json, README
- ✅ `daemon.json` добавлен в deploy.py (`local` логи + live-restore) — применить `sudo systemctl restart docker` при следующем заходе
- ✅ `daemon.json` применён прогоном + `systemctl restart docker`; теперь все повторные прогоны — «No changes»
- ✅ на Windows: DockerCLI + Compose plugin + lazydocker; `docker context vps` через ssh-алиас
- ✅ план проектов расписан: [[Deploy_Plan_Giorno]] — **через платформу botops-deploy** (скилл Roman'а под этот же сервер: общий Caddy 80/443 + granit-staging_default + vibe-router + botops-static/compose скрипты). Восстановление: `/srv/botops` + сеть + router (student-share-codex на GH) + codex-vibe-data + skill/bin symlink + ops-homebase
- ✅ вводные: лендинг на `*.67.barabashka.pro`; SWAPP домен тот же (`swapp.apps.botops.ru`, в репо уже есть `compose.botops.yml` — интеграция готова); Hermes: 1-й агент семейный, дальше студенты (геймификация/домашки)
- ✅ dev-цепочка установлена кодом: git + build-essential + unzip (apt) + uv (~/.local/bin) + pnpm (~/.local/share/pnpm) — guarded-установки per-user, повторные прогоны чистые
- ✅ доступ к приватным репо выдан Devin'у (student-share-codex, ops-homebase клонируются); подняты реальные `deploy/docker-compose.yml` + `Caddyfile` роутера
- ✅ runbook восстановления → [[Botops_Restore]]; вся серверная механика — кодом `vps-config/botops.py` (/srv/botops compose+Caddyfile, сеть, symlinks, .env роутера, up контейнеров)
- ✅ github-ключ на сервере работает (`ssh -T git@github.com` → Hi monaxovdulov), все клоны на месте (`botops-deploy`, `student-share-codex`, `ops-homebase`, `MyKnowledgeBase`)
- ✅ **botops-инфра жива**: `granit-staging-caddy-1` + `deploy-vibe-router-1` оба Up, tls-check отвечает; проверено с моего прямого SSH (tailnet-нода `devin-vm-giorno`)
- ✅ **Devin CLI на сервере авторизован**: `~/.local/bin/devin` v3000.11.3, креды перенесены `scp credentials.toml` с Windows → `Logged in as monaxovdulov@yandex.by`, орг `monaxovdulov`; агент на сервере работает
- ✅ **Мой прямой доступ**: pubkey в `authorized_keys` + tailscale auth key → `ssh devuser@100.82.224.13` с моей VM — проверяю и делаю на сервере сам
- ✅ **Лендинг задеплоен**: slug `rabushko` → `botops-static deploy` → живой `https://rabushko.apps.botops.ru` (200, on-demand TLS); TG → `t.me/mosqitu`; реестр `ops-homebase` обновлён + карточка `services/rabushko-landing.md`
- ✅ Caddy расширен кодом: монт `codex-vibe-data → /srv/data:ro` в `files/botops-compose.yml` + override `files/rabushko.caddy` (`file_server` для `rabushko.67.barabashka.pro`) + ops validate+reload в `botops.py`
- ⬜ `rabushko.67.barabashka.pro` — ждёт DNS: `barabashka.pro` сейчас NXDOMAIN у публичных резолверов (8.8.8.8/1.1.1.1) — Roman уточняет у провайдера; как резолвится → reload caddy выпустит сертификат сам
- ✅ `gh auth` на сервере — Roman прогнал `gh auth login` вживую (SSH-протокол + paste token) → `Logged in as monaxovdulov`; `gh repo create` и пр. теперь доступны агенту.
- ✅ **SWAPP жив**: `https://swapp.apps.botops.ru` — root/health/webhook все 200; контейнеры `eco-swapp-minsk-app-1` + `-db-1` Up; webhook перерегистрирован (`setWebhook url=/telegram/webhook + secret_token`). chat_id группы вытащил через getUpdates: `-1003931924827` («тест группа SWAP»).
- ⬜ `rabushko.67.barabashka.pro` — ждёт DNS: `barabashka.pro` сейчас NXDOMAIN у публичных резолверов — Roman уточняет у провайдера; override выключен в `.disabled` (его неудачные ACME-ретраи держали лимитер), вернуть после фикса DNS → reload.
- ⏳ **Hermes-каркас ставится**: модель «1 агент = 1 контейнер» — образ `hermes-agent` (официальный Dockerfile), `~/hermes-agents/<имя>/{compose.yml,.env,home}`; кодом в `agents.py::hermes_runtime()`. Первый агент — family: ждёт от Roman'а модель+ключ и токен нового TG-бота.
- ⬜ дальше: харденинг-кодом (шаг 6)

**Следующий шаг:** Roman приносит (1) модель/API-ключ для family-агента, (2) токен бота из BotFather → поднимаю `hermes-family` контейнер → потом шаг 6.

## 2026-10-09 — Шаг 1: sudo и пользователь devuser

Вход: `ssh root@46.226.165.215` + пароль из панели aeza.

Выполнено:

```bash
apt update && apt install -y sudo
adduser devuser
usermod -aG sudo devuser
```

Что произошло:

- `apt update` — скачал индексы пакетов (25.5 MB). Ответ «114 packages can be upgraded» — образ старый, полный `apt upgrade` сделать отдельно.
- `apt install -y sudo` — sudo в минимальном образе отсутствовал; установлен 1.9.13p3.
- `adduser devuser` — пользователь uid 1000, группа `devuser`, `/home/devuser` из `/etc/skel`. Пароль задан; анкета (Full Name и т.д.) — «lexa minsky». Debian добавил его и в общую группу `users`.
- `usermod -aG sudo devuser` — добавлен в группу `sudo`.

Осталось проверить: `ssh devuser@46.226.165.215` во втором окне + `sudo whoami` → `root`. Дальше [[02_SSH_Keys]].

## 2026-10-09 — Шаг 2 (начало): генерация SSH-ключа — затык с вставкой

Команда: `ssh-keygen -t ed25519 -C "devuser-giorno"` (PowerShell).

**Что случилось:** на вопрос `Enter file in which to save the key` в поле ввода улетела **следующая команда** из скопированного блока (`type ... | ssh devuser@...`) — ssh-keygen принял её за имя файла и упал: `Saving key ... failed: No such file or directory`. Ключ не создан, всё повторяем заново.

**Урок:** на вопрос про путь — просто `Enter` (дефолт правильный); пока идёт интерактивный ввод, вставлять команды строго по одной.

**Повторная попытка — успех:** создана пара `C:\Users\monax\.ssh\id_ed25519` (приватный) + `id_ed25519.pub` (публичный), passphrase задан. Фингерпринт `SHA256:FSbY...`. Разбор вывода: identification = приватный (не светим), public key = то, что кладём на сервер, fingerprint = «номер» ключа, randomart — визуальный отпечаток для глазного сравнения.

**Затык 2 — `Too many authentication failures` при копировании pubkey.** Команда `type ... | ssh devuser@IP "..."` оборвалась ещё до пароля: клиент сначала предложил серверу все ключи из ssh-agent (на ПК их несколько), сервер насчитал лимит `MaxAuthTries` и отключил. **Фикс:** `-o PubkeyAuthentication=no` — не предлагать ключи, сразу пароль:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -o PubkeyAuthentication=no devuser@46.226.165.215 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Посмотреть ключи в агенте: `ssh-add -l`.

**Затык 3 — `Permission denied`: вводил пароль root вместо devuser.** Спрашивают пароль именно того пользователя, под которым логинимся (`devuser@IP` → пароль devuser, а не root). Пароль devuser забыт → сброс из-под root (root-вход по паролю пока включён):

```powershell
ssh -o PubkeyAuthentication=no root@46.226.165.215   # входим по паролю root
passwd devuser                                        # задаём devuser новый пароль
```

**Урок:** пароль devuser нужен для `sudo` — записать в менеджер паролей сразу при создании.

**Дизайн-разбор:** обсудили «как не делать одно и то же на следующем сервере». Ответ: первый сервер — руками (обучение), второй и дальше — два прогона pyinfra: `bootstrap.py` (root + `--ssh-password-prompt`, только юзер+ключ, безопасно от локаута) → проверка `ssh devuser` → `deploy.py` из шага 6. Оформлено заметкой [[08_Bootstrap_Second_Server]]. Плюс исследование переносимости ключа между машинами → [[SSH_Key_Portability]] (выбор Roman'а: Bitwarden SSH-агент).

**Ключ на сервере + вход по ключу работают.** Команда копирования (`type ... | ssh -o PubkeyAuthentication=no devuser@IP "..."`) прошла молча — отсутствие вывода = успех, pubkey дописан в `~/.ssh/authorized_keys`. Проверка `ssh devuser@46.226.165.215` → спросил passphrase ключа → `devuser@giorno` без пароля сервера. Урок: «молчит» ≠ «не сработало» у Unix-команд; passphrase спрашивает при каждом входе, пока ключ не в ssh-agent (см. раздел агента в [[02_SSH_Keys]]).

## 2026-10-12 — Шаг 2 (финал) и Шаг 3 (начало): агент, алиас, отключение паролей

- `Set-Service ssh-agent -StartupType Automatic` + `Start-Service ssh-agent` + `ssh-add ...\id_ed25519` → `Identity added` — passphrase до перезагрузки не спрашивает.
- Алиас `Host vps` в `~/.ssh/config` → `ssh vps` входит молча.
- Харденинг по [[03_Basic_Server_Hardening]]: drop-in `/etc/ssh/sshd_config.d/00-hardening.conf` (`PermitRootLogin no`, `PasswordAuthentication no`), `sudo sshd -t` → `systemctl reload ssh`. Проверка из нового окна: `ssh vps` пускает, `ssh root@IP` → `Permission denied (publickey)` — парольный вход закрыт полностью, сессию не порвало.
- Защита включена: `apt upgrade -y` + `ufw allow OpenSSH && ufw enable` («Firewall is active and enabled on system startup») + `jail.local` (`[sshd] enabled = true`) + `systemctl enable --now fail2ban`. Сообщение «Command may disrupt existing ssh connections» — штатное предупреждение ufw, `y` + OpenSSH уже разрешён → сессия жива.
- **Вопрос: забанит ли fail2ban за частые входы через VPN?** Нет — банятся провалы (дефолт 5 неудач за 10 мин → бан ~10 мин), успешные входы по ключу не считаются. Риск с VPN — общий выходной IP: чужие брутфорсы с того же IP могут достаться тебе. Выходы из бана: подождать bantime / другой IP (выход VPN, хотспот) / веб-консоль aeza → `sudo fail2ban-client unban <IP>` (или `--all`). `ignoreip` белый список есть, но с динамическим IP бесполезен.
- **План: Tailscale** — Roman ставит tailnet для входа с Windows. Это апгрейд всей схемы: после проверки `ssh devuser@100.x` публичный порт 22 закрываем (`ufw allow in on tailscale0` + `ufw delete allow OpenSSH`) — SSH будет существовать только внутри tailnet; fail2ban/брутфорс из интернета вообще исчезают как класс. Правило то же, что с паролями: новый путь проверен → старый закрываем.
- **Tailscale поднят + exit node.** `sysctl.d/99-tailscale.conf` (ip_forward v4+v6), `tailscale set --advertise-exit-node`, аппрув в админ-консоли; на Windows выбран exit node — `ifconfig.me` показывает IP aeza. **Затык:** включение exit node во время SSH-сессии по публичному IP → `Connection reset` (трафик сессии ушёл в собственный туннель). Урок: админский вход переводим на `100.x` адрес — тогда SSH не зависит ни от публички, ни от exit node.
- **ufw перекрыт на tailnet-only.** `sudo ufw allow in on tailscale0` + `sudo ufw delete allow OpenSSH` → статус: единственное правило `Anywhere on tailscale0 ALLOW`, публичного 22 нет. Урок: `ufw` без sudo → `command not found` (`/usr/sbin` не в PATH обычного юзера — все админ-команды через `sudo`).
- **Решение: Docker ставит pyinfra, а не руки.** Roman справедливо заметил: «разве pyinfra Docker сама не поставит?» — да, и это правильный способ: первый настоящий `deploy.py`. Под это создан проект `vps-config/` в корне репо: `inventory.py` (хост `vps` через ssh-конфиг/tailnet), `deploy.py` (`apt.packages` docker.io+docker-compose-v2 + `server.user` groups=docker с `append=True`), бутстрап-файлы для будущих серверов по [[08_Bootstrap_Second_Server]].
- **Первый прогон pyinfra.** `pyinfra inventory.py exec -- hostname` → `giorno.ptr.network` через tailnet — связь есть. `--dry` показал 2 изменения, pyinfra интерактивно спросил sudo-пароль. Реальный прогон упал на `E: Unable to locate package docker-compose-v2`. **Затык:** `docker-compose-v2` — имя пакета Ubuntu; в Debian его нет вообще (madison пуст по всем suite), а `docker.io` в bookworm — версия 2023 г. **Решение:** официальный репозиторий docker.com — `files.download` GPG в `/etc/apt/keyrings/docker.asc` + `apt.repo` в `sources.list.d/docker.list` + пакеты `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`. Тот же drop-in паттерн, что у sshd. Сервер не задело — apt-установка атомарна.
- **Успешный деплой Docker кодом.** Второй прогон: 4 success + 1 «No changes» (каталог keyrings уже существовал — идемпотентность вживую). Перелогин → `docker ps` без sudo работает. Docker engine + compose v2 из официального репо.
- **Ресёрч Docker-практик → заметка [[Docker_Best_Practices]].** Ключевое: (1) `docker -p` обходит ufw через DNAT/FORWARD — «пустой» файрвол не защищает опубликованные порты, биндим к конкретным IP (`127.0.0.1`, tailnet `100.x`, публично только caddy); (2) `daemon.json`: `local` log-driver (json-file не ротирует — диск 60 GB) + `live-restore`; (3) `docker context create vps --docker "host=ssh://vps"` — управление с Windows без входа по SSH; (4) compose-гигиена (.env, healthcheck, restart, пины версий); (5) `docker system df/prune` для диска. В `deploy.py` добавлен `files.put` daemon.json.
- **Платформа botops-deploy.** У Roman есть готовый скилл-репо `botops-deploy` под этот сервер: общий Caddy на 80/443 + on-demand TLS через vibe-router (`/internal/tls-check`), статика `botops-static` (иммутабельные артефакты + атомарный live-symlink + rollback), compose-приложения `botops-compose` (external-сеть `granit-staging_default`, override-маршруты `/srv/botops/staging-overrides/*.caddy`, deploy по sha с auto-rollback по health). В `eco-swapp-minsk` уже лежит `compose.botops.yml` — SWAPP был подключён до вайпа. Клонируемо с GitHub: botops-deploy, student-share-codex (router), ops-homebase (реестр).
- **Dev-цепочка через pyinfra.** Прогон `deploy.py` v3: 4 success + 5 «No changes» — git/build-essential/unzip через apt, uv и pnpm per-user в ~/.local с `host.get_fact(File)` guard'ами (не переустанавливают при повторе).
- **Доступ к приватным репо.** Roman выдал Devin доступ → `student-share-codex` и `ops-homebase` склонированы, подняты реальные файлы: роутер — `node:22-bookworm` + `src/router-server.js` (env `CODEX_VIBE_ROOT`, `ROUTER_PORT=8090`, `CADDY_DOCKER_NETWORK`), Caddyfile — `on_demand_tls → vibe-router` + wildcard-блоки apps/preview.
- **Восстановление botops → кодом.** Создан `vps-config/botops.py` + `files/botops-compose.yml` (общий Caddy `granit-staging-caddy-1`, 80/443, external-сеть, монт `staging-overrides → /srv/overrides`) + `files/botops-Caddyfile` (референс + `import /srv/overrides/*.caddy`) + `files/vibe-router.env`. `/srv/botops/compose.yml` на старом сервере жил только локально — теперь он кодом и переезжает вместе с репо. Руками остаются только github-ключ devuser и три клона; остальное — `pyinfra inventory.py botops.py`. Runbook: [[Botops_Restore]].
- **botops.py: первый прогон 13/13 success.** Затык: операция «напечатать pubkey» ничего не показала — **pyinfra не выводит stdout успешных команд**, только ошибки. Вывод: публичные строки достаём руками (`cat ~/.ssh/id_ed25519_github.pub`) или фактами, а не эхо-операциями. Второй затык: `clone || echo SKIP` даёт «Success» даже при неудаче клона — проверять `ls` каталогов и `ssh -T git@github.com`, а не цвет строки. Роутер в план не попал (guard не видел клона до его выполнения) → повторный прогон после добавления pubkey в GitHub.

- **botops.py прогоны → инфра поднята.** 3 прогона: клоны прошли со 2-го (pubkey добавлен в GitHub), vibe-router ops попали в план только когда guard увидел клон. **Затык:** роутер ушёл в restart-луп — `ensureLayout()` делает `fs.mkdir` по data-корню, а mount `:ro` → EROFS. **Фикс:** `ROUTER_ENSURE_LAYOUT=0` в .env (каталоги создаёт botops.py, роутеру хватает чтения). Урок: ro-mount + «создай если нет» на старте — несовместимы; проверка `docker logs` при любом Restarting.

- **Инфра botops поднята и проверена — я зашёл на сервер.** Tailscale на моей VM → `devin-vm-giorno` в tailnet, SSH devuser@100.x работает. **Разбор затыка роутера:** рестарт-луп был НЕ от ro-mount (как гадали), а от brace-расширения: `server.shell` идёт через `sh` (dash) → `mkdir -p ~/{a,b,c}` создал ОДИН литеральный каталог `{a,b,c}` → `ensureLayout` в контейнере падал с `ENOENT`. Фикс: реальные каталоги руками + в botops.py явные пути без `{}`. Также `ROUTER_ENSURE_LAYOUT` бесполезен — переменной нет в `environment:` compose-файла роутера → удалена из .env. Итог: `deploy-vibe-router-1` Up, tls-check отвечает (403 до деплоев — норма), caddy Up. Урок: server.shell ≠ bash — никаких расширений `{}`, `[[ ]]`, heredoc-фишек bash.
- **Модель «агент на сервере».** Roman хочет агента локально на giorno → два слоя: Devin CLI на сервере (`curl install.sh | bash` → `~/.local/bin/devin`, логин — браузерная ссылка/токен; headless-флоу) + мой SSH через tailnet (auth key). Установки агентов вынесены в модуль `vps-config/agents.py` — туда же лягут hermes-профили. Handoff-док: [[Server_Agent_Handoff]].

## 2026-10-13 — Первый реальный деплой: лендинг через botops-static

- **Devin CLI авторизован** через перенос `credentials.toml` с Windows (`scp` в `~/.local/share/devin/`) → `Logged in as monaxovdulov@yandex.by`. Затык: `ssh vps "devin"` → `command not found` — non-interactive ssh не подхватывает `~/.local/bin` в PATH; решение — полный путь `~/.local/bin/devin` в one-liner'ах.
- **Мой SSH на сервере поднят.** Тailscale на VM Devin → нода `devin-vm-giorno` (100.82.59.67), pubkey в `authorized_keys` devuser → `ssh devuser@100.82.224.13` работает. Теперь проверки и правки — без Roman'а как «рук».
- **Первый деплой лендинга.** Файл `index (2).html` (949 KB, JS-рендер, фотки base64 внутри). Заглушки: `TG = USERNAME_TODO` → `t.me/mosqitu`. Деплой: `scp` → `botops-static deploy rabushko /tmp/dist-rabushko --source devin-landing --skip-public-smoke` → build `b202610131548025b1772b5`, live `https://rabushko.apps.botops.ru` → 200 (первый запрос ~8.5с — выпуск on-demand сертификата). Slug выбрал Devin: `rabushko` (фамилия, коротко, валидно по `^[a-z0-9-]{1,40}$`).
- **Внешний домен `*.67.barabashka.pro` — через file_server, не через роутер.** Разбор: `parseHost` в `router-hosts.js` понимает только `botops.ru` → любой чужой домен падает в `unknown` → 404. Вместо прокси на роутер с rewrite — прямой `file_server` в Caddy на том же артефакте: домаунтован `codex-vibe-data → /srv/data:ro` в `files/botops-compose.yml`, override `files/rabushko.caddy` (`root /srv/data/live/rabushko; file_server`). Бонус — тот же артефакт обслуживает и apps.botops.ru. Validate+reload — ok.
- **Затык: `barabashka.pro` не резолвится публично.** ACME упал: `NXDOMAIN looking up A for rabushko.67.barabashka.pro`. Проверка `dig @8.8.8.8/@1.1.1.1`: `barabashka.pro` вообще NXDOMAIN (даже NS не виден), хотя у Roman локально `test.67.barabashka.pro → 46.226.165.215`. Причины: зона не делегирована/свежая + не дошла до публичных резолверов, или кривой wildcard у провайдера. Урок: TLS по HTTP-01 требует, чтобы домен резолвился ВЕЗДЕ (LE ходит со своих резолверов) — «у меня резолвится» недостаточно. Override-файл ждёт: как DNS починится → `caddy reload` выпустит сертификат.
- **Урок caddy volumes:** в `caddy:2-alpine` volume `caddy_data` уже сидит на `/data` — второй mount туда же даёт коллизию (compose молча подхватил не то). Свои каталоги — на отдельные пути (`/srv/data`).
- **Реестр обновлён** в ops-homebase: строка в `botops-apps-registry.md` (live + соседний маршрут pending DNS) + карточка `services/rabushko-landing.md` — по правилу «registry update обязателен после ручного деплоя».
- **Кодом перенесено в vps-config:** монт `/srv/data` в `files/botops-compose.yml`, `files/rabushko.caddy`, ops `files.put` override + `caddy validate + reload` в `botops.py` — переезд на новый сервер повторит и маршрут.
- **GitHub CLI на сервере.** `gh` v2.62.0 в `~/.local/bin` (per-user бинарь, без sudo — паттерн uv/pnpm). Установка закодирована `github_cli()` в `agents.py`. Авторизация — одноразовый ручной шаг Roman'а: `gh auth login` в интерактивной ssh-сессии (browser-code, работает headless как devin-флоу) или PAT через `--with-token`. **Затык:** первый fine-grained PAT отклонён API (401 Bad credentials) — вероятно неполная копия. **Решено:** Roman прогнал `gh auth login` в интерактивной сессии сам (SSH-протокол → paste token) → `Logged in as monaxovdulov`. Урок: для headless-логинов paste-token внутри `gh auth login` надёжнее, чем генерация PAT в вебе + `--with-token` (меньше мест обрезать строку).
- **SWAPP задеплоен целиком.** Roman дал TG-значения (бот `@eco_swap_minsk_bot`, токен, группа `eco_swap_minsk_beta`, short name `swapp`). **chat_id группы** получил сам: у бота стоял webhook со старого сервера → `deleteWebhook` → `getUpdates` показал сообщение Roman'а → `-1003931924827`. `.env` заполнен (0 FILL_ME). Сборка `docker compose --env-file .env -f compose.production.yml -f compose.botops.yml up -d --build db app`: db healthy → app up.
- **Затык TLS: `tls force_automate`.** swapp.apps.botops.ru давал TLS internal error, сертификат даже не пытался выпускаться. Причина двойная: (1) в очереди ACME ретраил rabushko-блок (NXDOMAIN) и держал внутренний лимитер; (2) главное — имя покрывается wildcard `*.apps.botops.ru` с `tls on_demand` → его policy побеждает → handshake идёт в роутер `/internal/tls-check` → 403 (live-symlink `swapp` не существует, это docker-приложение). **Фикс из `references/docker.md` скилла:** в override-блоке обязательна директива `tls force_automate` — тогда имя получает обычный ACME-сертификат при reload, минуя роутер. Плюс выключил rabushko-override в `.disabled` до фикса DNS. Сертификат выпустился мгновенно, `/health` → 200, root → 200, probe POST на webhook → 200 в логах приложения.
- **Webhook зарегистрирован:** `setWebhook url=https://swapp.apps.botops.ru/telegram/webhook&secret_token=<из .env>` → ok, getWebhookInfo подтвердил. Урок: webhook бота НЕ внутри приложения — внешний вызов api.telegram.org после подъёма.
- **Учёт по docker.md выполнен полностью:** README.md с таблицей в staging-overrides (создан — не существовал), строка в «Соседние маршруты» реестра обновлена, карточка сервиса уже была. Правило занесено в код: `files/swapp.caddy` с `tls force_automate` + комментарий почему.

#vps #debian

## 2026-10-13 — Hermes: модель изоляции и каркас

- **Выбор модели.** По SECURITY.md hermes-agent единственная настоящая граница — ОС-изоляция; два постулата: terminal-backend (команды в песочнице, но python-процесс агента на хосте) vs whole-process wrap (весь процесс в контейнере). Взяли второй: **1 агент = 1 контейнер** на общем образе — официальный `Dockerfile` репо (s6-overlay `/init`, ремап `HERMES_UID/GID`, state в `/opt/data`).
- **Раскладка на сервере:** `~/hermes-agents/` с `README.md` + `agent.compose.template.yml`; агент = каталог `<имя>/{compose.yml, .env(600), home→/opt/data}`. Контейнер `hermes-<имя>` в bridge-сети без опубликованных портов — Telegram gateway работает по исходящему long-polling, входящие не нужны. `restart: unless-stopped` даёт автостарт через docker daemon.
- **Кодом:** `agents.py::hermes_runtime()` — mkdir каркаса, guarded clone `NousResearch/hermes-agent` в `~/ai-projects`, guarded `docker build -t hermes-agent`, `files.put` шаблона и README. Секреты агентов в код не идут — per-agent `.env` вручную.
- **Секреты модели:** `.env` агента — только секреты (по правилам самого hermes: поведение в config.yaml, .env = secrets only).
- Первый агент `family`: каталог создан; ждёт модель+ключ и TG-бот токен от Roman'а.
