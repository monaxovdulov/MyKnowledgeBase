# Handoff — установка Iva на giorno через Devin CLI

Готовый промпт для `devin` на сервере. Перед запуском владелец готовит:
токен бота (@BotFather), группу с Topics (топики «Задания» и «Решения»,
бот — участник), OpenAI API-ключ (или выбор codex).

Контекст исполнителя: машина giorno, Debian 12, юзер `devuser` (sudo),
SSH только через tailnet, public 22 закрыт. Рядом живут botops (Caddy),
SWAPP — ничего существующего не трогать. Iva работает long-poll'ом и
никаких портов не открывает — конфликтов нет.

## Промпт (вставить в `~/.local/bin/devin` на giorno)

```text
Установи и настрой Iva (github.com/smixs/iva-agent) для devuser на этом
сервере по официальной инструкции https://iva-agent.com/install.txt —
читай её SKILL.md и следуй шагам. Установка под обычным юзером, не root.
Если linger у devuser не включён — включи через sudo (loginctl enable-linger).

Модель: MODEL_PROVIDER=custom (OpenAI API ключ):
  CUSTOM_BASE_URL=https://api.openai.com/v1
  CUSTOM_API_KEY — спроси у меня, я дам (записать только в .env, никуда не печатать)
  CUSTOM_MODEL=gpt-5.1
  CUSTOM_CONTEXT_WINDOW=131072
  CUSTOM_VISION_MODEL=gpt-4o-mini

.env дополнительно (спроси у меня недостающие ID по ходу):
  TELEGRAM_ALLOWED_USER_IDS=<мой id>,<id ученика>,<group_id группы>
  TELEGRAM_DIGEST_CHAT_ID=<мой id>

После установки настрой учебный контур (дизайн: группа с Topics,
топик «Задания» = Куратор, топик «Решения» = Тьютор):
1. Спроси у меня group_id и thread_id обоих топиков (я узнаю у бота после
   запуска или скажу сам).
2. Запиши data/custom/agent/instructions/90-tutor.md и
   data/custom/agent/skills/tutor/SKILL.md — тексты возьми из
   https://github.com/monaxovdulov/MyKnowledgeBase/blob/main/KnowledgeBase/01_Topics/DevOps/Iva_Agent/03_Setup_Guide.md
   (разделы 4 и 5), подставив реальные ID.
3. Создай vault/tutoring/state.md и vault/tutoring/score.md по разделу 6
   того же документа.
4. Приёмка по чек-листу раздела 7 там же.

Правила безопасности: секреты только в .env; systemd-юниты не писать руками
(ставит официальный installer); чужие сервисы на сервере не трогать.
```

## Что владелец делает до/во время

1. @BotFather → токен.
2. Группа → Topics ON → топики «Задания», «Решения» → добавить бота.
3. Свой Telegram ID (@userinfobot) и ID ученика (он у себя через @userinfobot).
4. OpenAI API-ключ.
5. `ssh vps` → `~/.local/bin/devin` → вставить промпт выше.
6. После запуска бота: в каждом топике написать боту «какой chat_id и
   message_thread_id у этого топика» — отдать агенту для правил.
7. Приёмочный прогон — чек-лист в [[03_Setup_Guide]] п.7.

#iva #handoff #giorno
