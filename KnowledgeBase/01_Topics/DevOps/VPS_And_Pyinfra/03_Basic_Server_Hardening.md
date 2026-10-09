# Шаг 3. Базовая защита руками

> Карта трека: [[VPS_And_Pyinfra_MOC]] · Предыдущий: [[02_SSH_Keys]] · Следующий: [[04_Install_Pyinfra_On_Windows]]

Делаем минимум защиты **вручную** — чтобы понимать, что потом будет писать pyinfra. Всё это потом перепишем кодом в [[06_Hardening_As_Code]].

Работаем под `roman@IP`. Перед началом: сессия SSH открыта + веб-консоль aeza под рукой.

## Закрываем root и парольный вход в sshd

Debian 12 читает drop-in файлы из `/etc/ssh/sshd_config.d/` — не трогаем основной конфиг:

```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
EOF

sudo sshd -t                 # проверка синтаксиса — должна молчать
sudo systemctl reload ssh
```

**Проверка, не закрывая текущую сессию:** в новом окне `ssh vps` должен пускать по ключу, `ssh root@IP` — отказывать. Если новое окно не пускает — откатываем файл из старой сессии.

## Файрвол: ufw

```bash
sudo apt install -y ufw
sudo ufw allow OpenSSH      # СНАЧАЛА разрешаем SSH...
sudo ufw enable             # ...потом включаем (на вопрос отвечаем y)
sudo ufw status             # должно быть: OpenSSH ALLOW
```

## fail2ban — бан за перебор паролей

```bash
sudo apt install -y fail2ban

sudo tee /etc/fail2ban/jail.local <<'EOF'
[sshd]
enabled = true
EOF

sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd   # после первых попыток покажет баны
```

## Автообновления безопасности

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades   # отвечаем Yes
```

## Проверь себя

- [ ] Новое окно `ssh vps` пускает; `ssh root@IP` — нет
- [ ] `sudo ufw status` — активен, OpenSSH разрешён
- [ ] `systemctl status fail2ban` — active (running)
- [ ] Текущую рабочую сессию не закрыли раньше времени

#vps #debian #security
