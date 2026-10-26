# Iva-агент на сервере — MOC

Трек: установка и настройка self-hosted Telegram-ассистента **Iva**
([github.com/smixs/iva-agent](https://github.com/smixs/iva-agent)) на сервере giorno
под учебный кейс — агент-тьютор в Telegram-группе с топиками.

Заметки лежат в `01_Topics/DevOps/Iva_Agent/`.

## Порядок чтения

| # | Заметка | Что даёт |
|---|---------|----------|
| 0 | [[00_Overview]] | Что такое Iva, вердикт «подходит ли под кейс», цены |
| 1 | [[01_Architecture]] | Устройство изнутри: пайплайн, сессии=топики, allowlist, провайдеры, точки расширения |
| 2 | [[02_Tutor_Design]] | Дизайн под кейс: два топика, роли, файлы состояния, баллы, ограничения |
| 3 | [[03_Setup_Guide]] | Пошаговая установка на giorno + готовые конфиги (rules, skill) |
| 4 | [[04_Pi_Prototype]] | Прототип тьютора на Pi Agent Core, границы приватных ответов, текущая готовность |
| — | [[Handoff_Devin_CLI]] | Готовый промпт для Devin CLI на сервере + что подготовить владельцу |

Журнал фактического прогресса: [[Practice_Log]]

## Связанное

- [[VPS_And_Pyinfra_MOC]] — сервер giorno, devuser, hardening
- [[Server_Agent_Handoff]] — очередь задач для агента на сервере (Devin CLI на giorno авторизован)

#iva #telegram #agent #vps
