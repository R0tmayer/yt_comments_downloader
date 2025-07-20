"""
Модуль для сохранения и загрузки пользовательских настроек.
"""

import json
import os
from typing import Optional
from config import SETTINGS_FILE

def save_folder(folder_path: str) -> None:
    """Сохраняет путь к папке в файл настроек."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as file:
            json.dump({'save_folder': folder_path}, file)
    except Exception as error:
        print(f"Ошибка сохранения настроек: {error}")

def load_folder() -> Optional[str]:
    """Загружает сохраненный путь к папке из файла настроек."""
    if not os.path.exists(SETTINGS_FILE):
        return None
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('save_folder')
    except Exception as error:
        print(f"Ошибка загрузки настроек: {error}")
        return None
