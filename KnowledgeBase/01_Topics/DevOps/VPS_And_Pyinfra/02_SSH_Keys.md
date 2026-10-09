# Шаг 2. SSH-ключи вместо пароля

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[01_First_SSH_Connection]] · Следующий: [[03_Basic_Server_Hardening]]

Пароль на видном из интернета SSH — это брутфорс 24/7. Переходим на ключи; парольный вход отключим на следующем шаге.

## Генерируем ключ на Windows

В PowerShell:

```powershell
ssh-keygen -t ed25519 -C "roman-laptop"
```

- Путь по умолчанию `C:\Users\<ты>\.ssh\id_ed25519` — оставляем.
- Passphrase: лучше задать — тогда ключ бесполезен даже при угоне файла.

Получаем два файла: `id_ed25519` (приватный, никому не показываем) и `id_ed25519.pub` (публичный, его кладём на сервер).

## Кладём публичный ключ на сервер

В PowerShell одной командой (введёт пароль `roman`):

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh roman@ВАШ_IP "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## Проверяем

```powershell
ssh roman@ВАШ_IP
```

Пускает без пароля (или спрашивает passphrase ключа) — ключ работает.

## Делаем короткий алиас `vps`

Создаём/открываем `C:\Users\<ты>\.ssh\config`:

```sshconfig
Host vps
    HostName ВАШ_IP
    User roman
    IdentityFile ~/.ssh/id_ed25519
```

Теперь вход — это просто `ssh vps`. **Важно:** pyinfra читает этот же конфиг, так что `vps` станет именем хоста и для деплоев.

## Проверь себя

- [ ] `ssh vps` входит без пароля сервера
- [ ] Файл `id_ed25519` никуда не коммитим и никому не шлём
- [ ] Помним путь отхода: веб-консоль aeza (парольный вход ещё включён — отключим в [[03_Basic_Server_Hardening]])

#vps #ssh #windows
