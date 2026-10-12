# Шаг 2. SSH-ключи вместо пароля

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[01_First_SSH_Connection]] · Следующий: [[03_Basic_Server_Hardening]]

Пароль на видном из интернета SSH — это брутфорс 24/7. Переходим на ключи; парольный вход отключим на следующем шаге.

## Генерируем ключ на Windows

В PowerShell запускаем **одну** команду:

```powershell
ssh-keygen -t ed25519 -C "devuser-giorno"
```

Дальше отвечаем на вопросы по очереди:

- `Enter file in which to save the key` — просто **Enter**: дефолт `C:\Users\<ты>\.ssh\id_ed25519`, ничего не вводим
- `Enter passphrase` — задаём фразу (это пароль на сам файл ключа: украденный `id_ed25519` без passphrase бесполезен)
- `Enter same passphrase again` — повторяем

> ⚠️ Пока идёт интерактивный ввод, **не вставляй следующие команды** — строка уйдёт ответом на вопрос (см. затык в [[Practice_Log]]). Команды этого шага выполняем по одной.

Получаем два файла: `id_ed25519` (приватный, никому не показываем) и `id_ed25519.pub` (публичный, его кладём на сервер).

### Как не вводить passphrase каждый раз — ssh-agent

Агент держит расшифрованный ключ в памяти: passphrase вводится **один раз за сессию Windows**, дальше `ssh vps` работает без вопросов.

```powershell
# один раз, PowerShell от администратора:
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent

# после каждой перезагрузки (здесь и спросят passphrase):
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

Ключ уже создан без passphrase? Добавить задним числом: `ssh-keygen -p -f $env:USERPROFILE\.ssh\id_ed25519`.

### Забыл passphrase / потерял ключ — что делать

Приватный ключ восстановить нельзя — но это не катастрофа: ключ — просто строка в `authorized_keys`, заменяется за минуту.

1. Генерируем новую пару: `ssh-keygen -t ed25519`.
2. Авторизуем новый публичный ключ любым оставшимся путём:
   - **веб-консоль aeza** (вход под root с паролем из панели) → дописать новый pubkey в `/home/devuser/.ssh/authorized_keys`;
   - или другой рабочий ключ, если он есть на втором устройстве.
3. Старый ключ удаляем из `authorized_keys`.

Единственное, что нельзя терять по-настоящему, — доступ в панель aeza (оттуда веб-консоль и сброс root-пароля). Passphrase держим в менеджере паролей.

## Кладём публичный ключ на сервер

В PowerShell одной командой (введёт пароль `devuser`):

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -o PubkeyAuthentication=no devuser@ВАШ_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

`-o PubkeyAuthentication=no` — не предлагать ключи из ssh-agent, сразу пароль: без флага сервер может оборвать по `Too many authentication failures` до запроса пароля (см. [[Practice_Log]]).

На Linux/macOS/Git Bash то же самое делает готовая утилита: `ssh-copy-id devuser@ВАШ_IP`.

### Переносимый вариант — функция в PowerShell-профиле

Чтобы не помнить длинную команду, один раз записываем функцию в `$PROFILE` —
файл, который PowerShell грузит при каждом старте:

```powershell
notepad $PROFILE   # если файла нет — согласиться создать
```

Вставляем и сохраняем:

```powershell
function Copy-SshKey {
    param(
        [Parameter(Mandatory=$true)][string]$Target,  # например devuser@46.226.165.215
        [string]$Key = "$env:USERPROFILE\.ssh\id_ed25519.pub"
    )
    Get-Content $Key | ssh -o PubkeyAuthentication=no $Target "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
}
```

Активируем без перезапуска: `. $PROFILE` (или просто новое окно). Теперь для
любого сервера достаточно:

```powershell
Copy-SshKey devuser@ВАШ_IP
```

Для другого ключа: `Copy-SshKey devuser@IP -Key C:\Users\<ты>\.ssh\id_rsa.pub`.

> Когда серверов станет больше одного — эта команда сменяется прогоном
> `bootstrap.py` из [[08_Bootstrap_Second_Server]]: ключ кладёт
> `server.user_authorized_keys`, а не ручная команда.

## Проверяем

```powershell
ssh devuser@ВАШ_IP
```

Пускает без пароля (или спрашивает passphrase ключа) — ключ работает.

## Делаем короткий алиас `vps`

Создаём/открываем `C:\Users\<ты>\.ssh\config`:

```sshconfig
Host vps
    HostName ВАШ_IP
    User devuser
    IdentityFile ~/.ssh/id_ed25519
```

Теперь вход — это просто `ssh vps`. **Важно:** pyinfra читает этот же конфиг, так что `vps` станет именем хоста и для деплоев.

## Проверь себя

- [ ] `ssh vps` входит без пароля сервера
- [ ] Файл `id_ed25519` никуда не коммитим и никому не шлём
- [ ] Помним путь отхода: веб-консоль aeza (парольный вход ещё включён — отключим в [[03_Basic_Server_Hardening]])

#vps #ssh #windows
