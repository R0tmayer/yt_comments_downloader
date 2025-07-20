"""
Модуль для скачивания комментариев с YouTube.
"""


from typing import Callable, List
import sys
import os

# Обход проблемы с dateparser
def patch_dateparser():
    """Обходит проблему с dateparser в PyInstaller."""
    try:
        import dateparser
        # Отключаем timezone_parser если он вызывает ошибки
        if hasattr(dateparser, 'timezone_parser'):
            dateparser.timezone_parser = None
    except ImportError:
        pass

# Применяем патч до импорта youtube_comment_downloader
patch_dateparser()

from youtube_comment_downloader import YoutubeCommentDownloader
from config import PROGRESS_UPDATE_INTERVAL
import re


def download_youtube_comments(url: str, progress_callback: Callable[[int, int], None] = None, max_comments: int = None) -> List[str]:
    """
    Скачивает комментарии с YouTube видео.
    progress_callback: принимает (current, total)
    max_comments: максимальное количество комментариев (или None для всех)
    """
    if not url or not validate_youtube_url(url):
        raise ValueError("Некорректная ссылка на YouTube.")
    
    downloader = YoutubeCommentDownloader()
    comments: List[str] = []
    try:
        idx = 0
        for comment in downloader.get_comments_from_url(url):
            idx += 1
            comments.append(comment['text'])
            if progress_callback and (idx % PROGRESS_UPDATE_INTERVAL == 0):
                progress_callback(idx, 0)
            if max_comments is not None and idx >= max_comments:
                break
        # Финальный вызов прогресса
        if progress_callback:
            progress_callback(idx, 0)
    except Exception as error:
        raise Exception(f"Ошибка при скачивании комментариев: {error}")
    return comments


def validate_youtube_url(url: str) -> bool:
    """Проверяет, является ли строка валидной ссылкой на YouTube."""
    youtube_patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/embed/',
        r'm\.youtube\.com/watch\?v='
    ]
    return any(re.search(pattern, url.lower()) for pattern in youtube_patterns)
