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
- ⬜ Docker (`docker.io`, `docker-compose-v2`, `usermod -aG docker devuser`) — не ставили
- ⬜ **Tailscale** (план Roman'а): install.sh → `tailscale up` → вход по 100.x → потом `ufw allow in on tailscale0` и `delete allow OpenSSH` — SSH закрываем из публички, только tailnet

**Следующий шаг:** Tailscale на сервере + клиент на Windows → проверка `ssh devuser@100.x` → закрыть публичный 22 → Docker → шаг 4 [[04_Install_Pyinfra_On_Windows]] (pyinfra на Windows).

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

#vps #debian
