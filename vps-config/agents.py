"""Агенты на сервере — отдельный модуль от базового deploy.py.

Сюда складываются установки всех агентов, которые Roman хочет на giorno:
сейчас — Devin CLI; дальше — hermes-профили и прочие.

Запуск с винды: pyinfra inventory.py agents.py
На сервере локально: pyinfra @local agents.py (или руками по шагам).
"""
from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.operations import server

DEVUSER = "devuser"
HOME = f"/home/{DEVUSER}"


def devin_cli():
    """Devin CLI — локальный агент в терминале, ставится per-user в ~/.local/bin.

    Установка idempotent: бинарь уже есть → skip. Авторизация (`devin`) —
    ручной одноразовый шаг: браузерная ссылка или вставка токена.
    """
    if not host.get_fact(File, path=f"{HOME}/.local/bin/devin"):
        server.shell(
            name="Devin CLI install (per-user)",
            commands=[
                "curl -fsSL https://cli.devin.ai/install.sh | bash"
            ],
        )
    else:
        host.noop("devin cli уже установлен — пропускаю установку")


devin_cli()
