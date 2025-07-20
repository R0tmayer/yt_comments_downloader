"""
Главное окно приложения с пользовательским интерфейсом.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading

from config import *
from settings import save_folder, load_folder
from file_manager import get_next_filename, save_comments_to_file
from downloader import download_youtube_comments, validate_youtube_url
from popup import SuccessPopup

ctk.set_appearance_mode(APPEARANCE_MODE)
ctk.set_default_color_theme(COLOR_THEME)

class App(ctk.CTk):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.title("YTCommentsDownloader by R0tmayer")
        self.geometry("800x500")
        self.resizable(False, False)
        self.save_folder = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Интерфейс с градиентом, увеличенным окном и сбалансированными размерами."""
        # Градиентный фон через CTkFrame (имитация)
        self.configure(fg_color=("#18181b", "#23232a"))
        container = ctk.CTkFrame(self, fg_color=("#18181b", "#23232a"))
        container.pack(expand=True, fill="both")
        # Заголовок по центру с градиентом для Rotmayer
        title_frame = ctk.CTkFrame(container, fg_color=("#18181b", "#23232a"))
        title_frame.pack(pady=(32, 10))
        title_label = ctk.CTkLabel(title_frame, text="YTCommentsDownloader by ", font=ctk.CTkFont(size=22, weight="bold"), text_color="#fff")
        title_label.pack(side="left")
        rotmayer_label = ctk.CTkLabel(title_frame, text="R0tmayer", font=ctk.CTkFont(size=22, weight="bold"), text_color=("#6c63ff", "#48c6ef"))
        rotmayer_label.pack(side="left", padx=(2, 0))
        # Статус по центру
        self.status_label = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#fff")
        self.status_label.pack(pady=(0, 20))
        # Верхний блок для выбора папки (secondary)
        top_block = ctk.CTkFrame(container, fg_color=("#18181b", "#23232a"))
        top_block.pack(anchor="w", padx=40, pady=(0, 0))
        self.setup_folder_selection(top_block)
        # Нижний блок для ввода ссылки и кнопки (primary)
        bottom_block = ctk.CTkFrame(container, fg_color=("#18181b", "#23232a"))
        bottom_block.pack(anchor="w", padx=40, pady=(40, 0))
        url_label = ctk.CTkLabel(bottom_block, text="Ссылка на видео", font=ctk.CTkFont(size=15), text_color="#fff")
        url_label.pack(anchor="w", pady=(0, 8))
        self.url_entry = ctk.CTkEntry(bottom_block, width=720, height=40, font=ctk.CTkFont(size=14), fg_color="#23232a", border_color="#444", border_width=2, text_color="#fff", corner_radius=14)
        self.url_entry.pack(anchor="w", pady=4)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=pMt4JZeZ0r4")
        self.url_entry.configure(placeholder_text="Вставьте ссылку на видео...", placeholder_text_color="#b2b2b2")
        self.download_btn = ctk.CTkButton(
            bottom_block,
            text="Скачать комментарии",
            command=self.start_download,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#fff",
            hover_color="#e5e5e5",
            text_color="#23232a",
            border_color="#444",
            border_width=2,
            corner_radius=12
        )
        self.download_btn.pack(anchor="w", pady=(16, 0))
        # Прогресс: обычный и жирный текст
        progress_frame = ctk.CTkFrame(container, fg_color=("#18181b", "#23232a"))
        progress_frame.pack(anchor="w", padx=52, pady=(16, 0))
        self.progress_label = ctk.CTkLabel(progress_frame, text="Скачано комментариев:", font=ctk.CTkFont(size=13), text_color="#b2b2b2")
        self.progress_label.pack(side="left")
        self.progress_value_label = ctk.CTkLabel(progress_frame, text=" 0", font=ctk.CTkFont(size=13, weight="bold"), text_color="#b2b2b2")
        self.progress_value_label.pack(side="left")
        # Статус: обычный и жирный текст
        status_frame = ctk.CTkFrame(container, fg_color=("#18181b", "#23232a"))
        status_frame.pack(anchor="w", padx=52, pady=(4, 20))
        self.status_label = ctk.CTkLabel(status_frame, text="Статус: ", font=ctk.CTkFont(size=13), text_color="#b2b2b2")
        self.status_label.pack(side="left")
        self.status_value_label = ctk.CTkLabel(status_frame, text="Готов к работе", font=ctk.CTkFont(size=13, weight="bold"), text_color="#b2b2b2")
        self.status_value_label.pack(side="left")

    def set_status(self, text: str) -> None:
        emoji = ""
        if "Ожидание" in text or "Готов" in text:
            emoji = "⏸️"
        elif "Ищу" in text:
            emoji = "🔎"
        elif "Подготавливаю" in text:
            emoji = "🛠️"
        elif "Скачиваю" in text:
            emoji = "⬇️"
        elif "Сохраняю" in text:
            emoji = "💾"
        elif "Ошибка" in text:
            emoji = "❌"
        elif "успешно" in text or "готово" in text:
            emoji = "✅"
        self.after(0, lambda: self.status_value_label.configure(text=f" {emoji} {text}"))

    def setup_folder_selection(self, parent=None) -> None:
        frame_parent = parent if parent is not None else self
        folder_frame = ctk.CTkFrame(frame_parent, fg_color=("#18181b", "#23232a"))
        folder_frame.pack(pady=8)
        folder_text_label = ctk.CTkLabel(folder_frame, text="Папка для сохранения:", font=ctk.CTkFont(size=14), text_color="#b2b2b2")
        folder_text_label.pack(side="left", padx=(0, 10))
        self.folder_label = ctk.CTkLabel(folder_frame, text="Не выбрана", font=ctk.CTkFont(size=14), text_color="#b2b2b2")
        self.folder_label.pack(side="left", padx=(0, 15))
        choose_folder_btn = ctk.CTkButton(folder_frame, text="Выбрать папку", command=self.choose_folder, width=140, height=32, font=ctk.CTkFont(size=13), fg_color="#23232a", text_color="#b2b2b2", hover_color="#444", border_color="#444", border_width=1, corner_radius=8)
        choose_folder_btn.pack(side="left", padx=(10, 0))

    def load_settings(self) -> None:
        """Загружает сохраненные настройки."""
        self.save_folder = load_folder()
        if self.save_folder:
            self.folder_label.configure(text=self.save_folder, text_color="white")

    def choose_folder(self) -> None:
        """Открывает диалог выбора папки."""
        initial_dir = self.save_folder if self.save_folder else "~"
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Выберите папку для сохранения")
        if folder:
            self.save_folder = folder
            self.folder_label.configure(text=folder, text_color="white")
            save_folder(folder)

    def start_download(self) -> None:
        """Запускает процесс скачивания комментариев."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите ссылку на YouTube видео.")
            return
        if not self.save_folder:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения.")
            return
        if not validate_youtube_url(url):
            messagebox.showerror("Ошибка", "Некорректная ссылка на YouTube.")
            return
        self.download_btn.configure(state="disabled")
        self.progress_value_label.configure(text=" 0")
        self.set_status("Ищу комментарии...")
        threading.Thread(target=self.download_comments, args=(url,), daemon=True).start()

    def download_comments(self, url: str) -> None:
        """Скачивает комментарии и сохраняет их в файл."""
        try:
            self.set_status("Подготавливаю к скачиванию...")
            comments = download_youtube_comments(url, self.update_progress)
            if not comments:
                self.set_status("")
                self.show_error("Комментарии не найдены.")
                return
            self.set_status("Сохраняю файл...")
            filepath = get_next_filename(self.save_folder)
            if save_comments_to_file(comments, filepath):
                self.set_status("")
                self.show_success(filepath)
                self.url_entry.delete(0, "end")
            else:
                self.set_status("")
                self.show_error("Ошибка сохранения файла.")
        except Exception as e:
            self.set_status("")
            self.show_error(str(e))
        finally:
            self.download_btn.configure(state="normal")
            self.progress_value_label.configure(text=" 0")
            self.set_status("Готов к работе")

    def update_progress(self, current: int, total: int) -> None:
        self.after(0, lambda: self.progress_value_label.configure(text=f" {current}"))
        self.set_status("Скачиваю комментарии...")

    def show_success(self, filepath: str) -> None:
        """Показывает окно успешного сохранения."""
        self.after(0, lambda: SuccessPopup(self, filepath))

    def show_error(self, msg: str) -> None:
        """Показывает окно ошибки."""
        self.after(0, lambda: messagebox.showerror("Ошибка", msg))
