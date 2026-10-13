# ~/hermes-agents — изолированные hermes-агенты

Каждый агент — каталог `<имя>/` со своими compose.yml, .env (секреты, chmod 600)
и home/ (персистентный HOME агента: config.yaml, память, скиллы). Контейнер
`hermes-<имя>` — весь процесс агента; граница изоляции = контейнер (по
SECURITY.md проекта это единственная настоящая граница).

## Создать агента
    mkdir -p ~/hermes-agents/<имя>/home
    cp ~/hermes-agents/agent.compose.template.yml ~/hermes-agents/<имя>/compose.yml
    # заменить AGENT_NAME → <имя>, заполнить .env (модельный ключ, TG_BOT_TOKEN)
    chmod 600 ~/hermes-agents/<имя>/.env
    cd ~/hermes-agents/<имя> && docker compose up -d
    docker logs -f hermes-<имя>

## Образ
Собран из официального Dockerfile: `cd ~/ai-projects/hermes-agent && docker build -t hermes-agent .`

## Журнал агентов
| имя | назначение | бот | контейнер |
|---|---|---|---|
| family | семейный орг-агент | — | hermes-family |
