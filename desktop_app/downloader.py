"""
Модуль для скачивания комментариев с YouTube.
"""


from typing import Callable, List
import requests
import re
import json
from config import PROGRESS_UPDATE_INTERVAL


def download_youtube_comments(url: str, progress_callback: Callable[[int, int], None] = None) -> List[str]:
    """
    Скачивает комментарии с YouTube видео.
    progress_callback: принимает (current, total)
    """
    if not url or not validate_youtube_url(url):
        raise ValueError("Некорректная ссылка на YouTube.")
    
    try:
        # Извлекаем video_id из URL
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Не удалось извлечь ID видео из ссылки.")
        
        # Получаем комментарии через YouTube Data API v3
        comments = get_comments_from_api(video_id, progress_callback)
        return comments
        
    except Exception as error:
        raise Exception(f"Ошибка при скачивании комментариев: {error}")


def extract_video_id(url: str) -> str:
    """Извлекает ID видео из YouTube URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def get_comments_from_api(video_id: str, progress_callback: Callable[[int, int], None] = None) -> List[str]:
    """Получает комментарии через YouTube Data API v3."""
    # Используем простой подход без API ключа - парсим страницу
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Ищем данные комментариев в JSON
        comments = []
        
        # Ищем ytInitialData в HTML
        yt_initial_data_match = re.search(r'var ytInitialData = ({.*?});', response.text)
        if yt_initial_data_match:
            try:
                data = json.loads(yt_initial_data_match.group(1))
                comments = extract_comments_from_data(data, progress_callback)
            except json.JSONDecodeError:
                pass
        
        # Если не нашли комментарии в ytInitialData, пробуем другой подход
        if not comments:
            comments = extract_comments_from_html(response.text, progress_callback)
        
        return comments
        
    except requests.RequestException as e:
        raise Exception(f"Ошибка при загрузке страницы: {e}")


def extract_comments_from_data(data: dict, progress_callback: Callable[[int, int], None] = None) -> List[str]:
    """Извлекает комментарии из ytInitialData."""
    comments = []
    
    def extract_from_dict(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "commentText" and isinstance(value, dict) and "simpleText" in value:
                    comment_text = value["simpleText"]
                    if comment_text and len(comment_text.strip()) > 0:
                        comments.append(comment_text)
                        if progress_callback and len(comments) % PROGRESS_UPDATE_INTERVAL == 0:
                            progress_callback(len(comments), 0)
                elif key == "text" and isinstance(value, dict) and "simpleText" in value:
                    comment_text = value["simpleText"]
                    if comment_text and len(comment_text.strip()) > 0:
                        comments.append(comment_text)
                        if progress_callback and len(comments) % PROGRESS_UPDATE_INTERVAL == 0:
                            progress_callback(len(comments), 0)
                else:
                    extract_from_dict(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                extract_from_dict(item, f"{path}[{i}]")
    
    extract_from_dict(data)
    return comments


def extract_comments_from_html(html: str, progress_callback: Callable[[int, int], None] = None) -> List[str]:
    """Извлекает комментарии из HTML страницы."""
    comments = []
    
    # Ищем комментарии в различных форматах
    patterns = [
        r'"commentText":\s*{\s*"simpleText":\s*"([^"]+)"',
        r'"text":\s*{\s*"simpleText":\s*"([^"]+)"',
        r'"contentText":\s*{\s*"simpleText":\s*"([^"]+)"'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            # Декодируем Unicode escape sequences
            comment = match.encode('utf-8').decode('unicode_escape')
            if comment and len(comment.strip()) > 0:
                comments.append(comment)
                if progress_callback and len(comments) % PROGRESS_UPDATE_INTERVAL == 0:
                    progress_callback(len(comments), 0)
    
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
