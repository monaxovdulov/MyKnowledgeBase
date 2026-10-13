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


def github_cli():
    """GitHub CLI — агенту создавать/читать репо. Per-user бинарь в ~/.local/bin.

    Авторизация ручная: `~/.local/bin/gh auth login` (интерактивная ssh-сессия,
    браузерный код) или `gh auth login --with-token` по PAT.
    """
    if not host.get_fact(File, path=f"{HOME}/.local/bin/gh"):
        server.shell(
            name="GitHub CLI install (per-user)",
            commands=[
                "cd /tmp && curl -fsSL -o gh.tgz "
                "https://github.com/cli/cli/releases/download/v2.62.0/gh_2.62.0_linux_amd64.tar.gz && "
                "tar xzf gh.tgz && mkdir -p ~/.local/bin && "
                "cp gh_2.62.0_linux_amd64/bin/gh ~/.local/bin/gh && "
                "rm -rf gh.tgz gh_2.62.0_linux_amd64"
            ],
        )
    else:
        host.noop("gh уже установлен — пропускаю установку")


devin_cli()
github_cli()
