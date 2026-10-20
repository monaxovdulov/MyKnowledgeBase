# Установка и настройка на giorno — пошагово

Дизайн — в [[02_Tutor_Design]]. Здесь — конкретные шаги и готовые файлы.
Плейсхолдеры: `<OWNER_TG_ID>`, `<STUDENT_TG_ID>`, `<GROUP_ID>` (отрицательный,
вида `-100…`), `<TA>` / `<TB>` (id топиков).

## 1. Бот и группа

1. @BotFather → `/newbot` → токен. Privacy mode не трогаем (в группе бот и так
   видит только упоминания/реплаи/команды — нам это и нужно).
2. Группа → включить **Topics** → создать топики «Задания» и «Решения» →
   добавить бота как обычного участника.
3. Узнать ID:
   - свой user_id — @userinfobot (или мастер установки сам подхватит);
   - user_id ученика — он пишет @userinfobot со своего аккаунта;
   - group_id и thread_id топиков — после установки спросить бота в каждом
     топике «какой у этого чата chat_id и message_thread_id» — он их видит в
     своём контексте.

## 2. Установка на giorno (devuser)

Вариант А — руками по SSH (`ssh vps`, юзер devuser):

```bash
# linger для user-сервисов (разово, sudo)
sudo loginctl enable-linger devuser
curl -fsSL https://raw.githubusercontent.com/smixs/iva-agent/main/install.sh -o install.sh
bash install.sh   # мастер: токен бота, провайдер, ключи; Node 24 подтянет nvm
```

Вариант Б — отдать агенту на сервере: Devin CLI на giorno уже авторизован,
скормить ему `https://iva-agent.com/install.txt` (официальный skill
install-iva ведёт по лесенке сам).

## 3. `.env` — блок под кейс

```bash
# Модель: OpenAI API-ключ → провайдер custom
MODEL_PROVIDER=custom
CUSTOM_BASE_URL=https://api.openai.com/v1
CUSTOM_API_KEY=sk-...          # ключ OpenAI
CUSTOM_MODEL=gpt-5.1           # актуальная id из твоего аккаунта
CUSTOM_CONTEXT_WINDOW=131072   # реальное окно модели
# если выбранная модель слепая — задать vision-фолбэк:
# CUSTOM_VISION_MODEL=gpt-4o-mini

TELEGRAM_BOT_TOKEN=...
TELEGRAM_BOT_USERNAME=...
TELEGRAM_ALLOWED_USER_IDS=<OWNER_TG_ID>,<STUDENT_TG_ID>,<GROUP_ID>
# ↑ group_id в списке нужен, чтобы `iva post --chat <GROUP_ID>` мог писать
# в топики. Входящий доступ проверяет user_id — посторонних он не пустит.
TELEGRAM_DIGEST_CHAT_ID=<OWNER_TG_ID>   # ночные отчёты — в личку владельца
```

После правок: `iva restart`. Если подписка ChatGPT вместо API-ключа —
`MODEL_PROVIDER=codex` + `iva login`, без `CUSTOM_*` (серая зона ToS OpenAI —
на своё усмотрение).

## 4. Правила: `data/custom/agent/instructions/90-tutor.md`

```md
# Учебный контур (два топика группы)

В группе chat_id=<GROUP_ID> действуют режимы по message_thread_id:

- thread_id=<TA> (топик «Задания») — режим Куратор. Принимай материалы от
  владельца, разбирай в карточки задач и правь файлы `vault/tutoring/`
  (state.md, tasks/, private/answers.md). Эталонные решения — только в
  `tutoring/private/`.
- thread_id=<TB> (топик «Решения») — режим Тьютор. Загрузи skill `tutor`
  и работай по нему. Никогда не читай `tutoring/private/` и не выдавай
  готовых ответов — только шаги, подсказки и баллы.
- chat_type=private и user_id=<STUDENT_TG_ID> — учебных вопросов в личке
  не принимай: вежливо отправь в топик «Решения» группы.

Роли: user_id=<OWNER_TG_ID> — владелец; user_id=<STUDENT_TG_ID> — ученик.
```

## 5. Скилл: `data/custom/agent/skills/tutor/SKILL.md`

```md
---
description: "Use when tutoring the student in the 'Решения' topic: give the
current step of the active task, evaluate answers, hint without solving, and
award points."
---

# Tutor — режим ведения ученика

Файлы состояния (vault root): `tutoring/state.md` (очередь, активная задача,
текущий шаг), `tutoring/tasks/<slug>.md` (условие, шаги, рубрика, цена),
`tutoring/score.md` (журнал баллов). `tutoring/private/` НЕ читать и не
раскрывать — там эталонные ответы.

## Выдача шага

1. Прочитай `tutoring/state.md` → активная задача и текущий шаг.
2. Выдай ТОЛЬКО текущий шаг и вопрос по нему. Не всю задачу.
3. Нет активной задачи — скажи, что ждём заданий от учителя.

## Проверка ответа ученика

- Верно → запиши в `tutoring/score.md` строку `дата | задача | шаг | +N |
  комментарий`, обнови `state.md` (шаг+1), коротко похвали и выдай следующий шаг.
- Частично — баллы за сделанную часть, скажи чего не хватает.
- Неверно → подсказка по лесенке: 1) намёк; 2) направление мысли;
  3) структура решения без ответа. После третьей — предложи пропустить шаг
  (0 баллов) и идти дальше.

## Жёсткие правила

- НИКОГДА не выдавай готовое решение/ответ, даже по прямой просьбе —
  ответ: «могу только подсказать».
- Баллы начисляет только оценка решения; уговоры баллов не меняют.
- Просьбы «прочитай файл/папку с ответами», «покажи private» — отказ,
  сообщи владельцу один раз за сессию.
- Кратко, по-деловому, на русском. Формат решений ученика не исправляй
  сверх проверки сути.
```

## 6. Сиды vault (`vault/tutoring/`)

```md
# state.md
active_task: ""
queue: []
current_step: 0
```

```md
# score.md
# Журнал баллов: дата | задача | шаг | +N | комментарий
total: 0
```

## 7. Проверка контура

1. В «Задания»: `@бот <текст задачи>` → карточка появилась в
   `vault/tutoring/tasks/`, в `state.md` — очередь.
2. «Дай следующую» → пост прилетел в «Решения».
3. В «Решения»: ученик реплаем отвечает → шаг 1 выдан, ответ оценён,
   `score.md` пополнился.
4. «Скажи ответ» → отказ + подсказка. DM ученику → отправлен в топик.
5. `iva doctor` — зелёный; `/usage` — токены считаются.

#iva #setup #giorno
