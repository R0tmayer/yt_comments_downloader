"""
Модуль для управления файлами и генерации имен.
"""

import os
import re
from typing import List

def get_next_filename(save_folder: str) -> str:
    """Генерирует имя для следующего файла с комментариями."""
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    existing_files = [f for f in os.listdir(save_folder) if re.match(r'comments_(\d+)\.txt$', f)]
    numbers = [int(re.findall(r'comments_(\d+)\.txt$', filename)[0]) for filename in existing_files if re.findall(r'comments_(\d+)\.txt$', filename)]
    next_number = max(numbers) + 1 if numbers else 1
    return os.path.join(save_folder, f'comments_{next_number}.txt')

def save_comments_to_file(comments: List[str], filepath: str) -> bool:
    """Сохраняет список комментариев в текстовый файл."""
    if not comments:
        print("Нет комментариев для сохранения.")
        return False
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            for idx, comment in enumerate(comments, start=1):
                clean_comment = comment.replace('\n', ' ').strip()
                file.write(f"{idx}. {clean_comment}\n")
        return True
    except Exception as error:
        print(f"Ошибка сохранения файла: {error}")
        return False
