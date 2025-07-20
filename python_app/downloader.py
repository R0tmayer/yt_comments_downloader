"""
Модуль для скачивания комментариев с YouTube.
"""


from typing import Callable, List
from youtube_comment_downloader import YoutubeCommentDownloader
from config import PROGRESS_UPDATE_INTERVAL
import re


def download_youtube_comments(url: str, progress_callback: Callable[[int, int], None] = None) -> List[str]:
    """
    Скачивает комментарии с YouTube видео.
    progress_callback: принимает (current, total)
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
