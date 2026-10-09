# Журнал практики

> Карта трека: [[VPS_And_Pyinfra_MOC]]

Фактический лог прохождения трека на живом сервере: что делал, что выводил терминал, выводы. Записываем сюда по мере прохождения шагов.

Сервер: `giorno` (`46.226.165.215`), aeza, Debian 12 bookworm, ядро 6.1 — свежепересозданный (голый) инстанс.

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

#vps #debian
