#!/usr/bin/env python3
# Scripts/check_structure.py

import os
import re
import sys

# Шаблон для верхнего уровня папок: "01_Topics", "02_References" и т.д.
FOLDER_REGEX = re.compile(r'^\d{2}_.+')

# Шаблон для файлов Markdown (имя без пробелов, только латиница, цифры, - и _)
# например: "AlphaGo_CaseStudy.md", "2025-02-14_NewFeatureReview.md"
FILE_REGEX = re.compile(r'^[A-Za-z0-9_\-]+(\.md)$')

# Допустимые расширения
ALLOWED_EXTENSIONS = {'.md', '.canvas', '.excalidraw', '.png', '.jpg', '.jpeg', '.gif'}

def check_name_and_suggest_fix(filename: str):
    """
    Проверяет имя файла/папки на пробелы, регистр и т.д.
    Возвращает (is_valid, suggestions) — булев флаг и список возможных правок.
    """
    suggestions = []
    is_valid = True

    # Если в имени есть пробелы, рекомендуем заменить на '_'
    if ' ' in filename:
        is_valid = False
        new_name = filename.replace(' ', '_')
        suggestions.append(f"Замени пробелы на подчёркивания: '{new_name}'")
    
    # Можно добавить логику для замены русских букв на латиницу, и т.п.
    # Здесь для примера пропустим.

    return is_valid, suggestions


def check_structure(base_path: str) -> list:
    """
    Обходит структуру папок, проверяет названия и возвращает список строк-сообщений об ошибках и подсказках.
    """
    issues = []

    for root, dirs, files in os.walk(base_path):
        for d in dirs:
            # Пропускаем скрытые и служебные папки (например, .git, .obsidian)
            if d.startswith('.'):
                continue

            folder_path = os.path.join(root, d)

            # Проверяем только папки верхнего уровня (root == base_path),
            # чтобы не заставлять все вложенные папки соответствовать шаблону.
            # Если хотите проверять и вложенные — меняйте логику.
            if root == base_path:
                if not FOLDER_REGEX.match(d):
                    # Проверяем, можем ли мы предложить автопоправку (например, пробелы)
                    valid, suggestions = check_name_and_suggest_fix(d)
                    # Если по основному REGEX не подошло, значит is_valid=False
                    # Но у нас может быть и случай, когда формат "03_Projects" неверен содержательно, 
                    # но формально regex проходит. 
                    # Для упрощения здесь просто сообщим, что имя папки не соответствует FOLDER_REGEX.
                    msg = f"Папка '{d}' не соответствует формату ^\\d{{2}}_.+"
                    if suggestions:
                        msg += f"\n   Возможные исправления:\n      " + "\n      ".join(suggestions)
                    issues.append(msg)

        for f in files:
            if f.startswith('.'):
                continue

            file_path = os.path.join(root, f)
            _, ext = os.path.splitext(f)

            # Проверяем расширение
            if ext.lower() not in ALLOWED_EXTENSIONS:
                issues.append(
                    f"Файл '{f}' в '{root}' имеет недопустимое расширение '{ext}'. "
                    f"Разрешённые расширения: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            else:
                # Если это markdown, проверяем имя
                if ext.lower() == '.md':
                    if not FILE_REGEX.match(f):
                        # Посмотрим, не можем ли мы предложить автопоправку
                        valid, suggestions = check_name_and_suggest_fix(f)
                        msg = (f"Файл '{f}' в '{root}' не соответствует шаблону "
                               f"^[A-Za-z0-9_\\-]+(\\.md)$")
                        if suggestions:
                            msg += f"\n   Возможные исправления:\n      " + "\n      ".join(suggestions)
                        issues.append(msg)

    return issues


def main():
    base_path = "KnowledgeBase"  # или можно передавать аргументом sys.argv
    issues = check_structure(base_path)
    if issues:
        print("Обнаружены следующие несоответствия:\n")
        for i in issues:
            print(f"- {i}\n")
        # Выходим с кодом 1, чтобы CI/CD мог пометить сборку как Failed
        sys.exit(1)
    else:
        print("Все проверки пройдены! Нарушений не обнаружено.")
        sys.exit(0)


if __name__ == "__main__":
    main()
