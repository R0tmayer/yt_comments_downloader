"""
Главное окно приложения с пользовательским интерфейсом (tkinter).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading

from config import *
from settings import save_folder, load_folder
from file_manager import get_next_filename, save_comments_to_file
from downloader import download_youtube_comments, validate_youtube_url
from popup import SuccessPopup

class App(tk.Tk):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.title("YTCommentsDownloader by R0tmayer")
        self.geometry("800x500")
        self.resizable(False, False)
        self.save_folder = None
        self.configure(bg="#18181b")
        self.setup_ui()
        self.load_settings()
        self.set_status("Готов к работе")

    def setup_ui(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Rounded.TButton',
                        foreground='#23232a',
                        background='#fff',
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor='none',
                        padding=6,
                        relief='flat')
        style.map('Rounded.TButton',
                  background=[('active', '#e5e5e5')])
        style.configure('Folder.TButton',
                        foreground='#b2b2b2',
                        background='#23232a',
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=4,
                        relief='flat')
        style.map('Folder.TButton',
                  background=[('active', '#444')],
                  foreground=[('active', '#fff')])
        # Контейнер
        container = tk.Frame(self, bg="#18181b")
        container.pack(expand=True, fill="both")
        # Заголовок
        title_frame = tk.Frame(container, bg="#18181b")
        title_frame.pack(pady=(32, 10))
        title_font = font.Font(size=22, weight="bold")
        title_label = tk.Label(title_frame, text="YTCommentsDownloader by ", font=title_font, fg="#fff", bg="#18181b")
        title_label.pack(side="left")
        rotmayer_label = tk.Label(title_frame, text="R0tmayer", font=title_font, fg="#6c63ff", bg="#18181b")
        rotmayer_label.pack(side="left", padx=(2, 0))
        # Статус по центру
        self.status_label = tk.Label(container, text="", font=(None, 13, "bold"), fg="#fff", bg="#18181b")
        self.status_label.pack(pady=(0, 20))
        # Верхний блок для выбора папки
        top_block = tk.Frame(container, bg="#18181b")
        top_block.pack(anchor="w", padx=40, pady=(0, 0))
        self.setup_folder_selection(top_block)
        # Нижний блок для ввода ссылки и кнопки
        bottom_block = tk.Frame(container, bg="#18181b")
        bottom_block.pack(anchor="w", padx=40, pady=(40, 0))
        url_label = tk.Label(bottom_block, text="Ссылка на видео", font=(None, 15), fg="#fff", bg="#18181b")
        url_label.pack(anchor="w", pady=(0, 8))
        self.url_entry = tk.Entry(bottom_block, width=80, font=(None, 14), fg="#fff", bg="#23232a", insertbackground="#fff", relief="solid", bd=2)
        self.url_entry.pack(anchor="w", pady=4, ipady=8)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=pMt4JZeZ0r4")
        self.url_entry_placeholder = "Вставьте ссылку на видео..."
        self.url_entry.bind("<FocusIn>", self._clear_placeholder)
        self.url_entry.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()
        self.download_btn = ttk.Button(
            bottom_block,
            text="Скачать комментарии",
            command=self.start_download,
            style='Rounded.TButton')
        self.download_btn.pack(anchor="w", pady=(16, 0))
        # Прогресс
        progress_frame = tk.Frame(container, bg="#18181b")
        progress_frame.pack(anchor="w", padx=40, pady=(16, 0))
        self.progress_label = tk.Label(progress_frame, text="Скачано комментариев:", font=(None, 13), fg="#b2b2b2", bg="#18181b")
        self.progress_label.pack(side="left")
        self.progress_value_label = tk.Label(progress_frame, text=" 0", font=(None, 13, "bold"), fg="#b2b2b2", bg="#18181b")
        self.progress_value_label.pack(side="left")
        # Статус
        status_frame = tk.Frame(container, bg="#18181b")
        status_frame.pack(anchor="w", padx=40, pady=(4, 20))
        self.status_label = tk.Label(status_frame, text="Статус: ", font=(None, 13), fg="#b2b2b2", bg="#18181b")
        self.status_label.pack(side="left")
        self.status_value_label = tk.Label(status_frame, text="", font=(None, 13, "bold"), fg="#b2b2b2", bg="#18181b")
        self.status_value_label.pack(side="left")

    def _clear_placeholder(self, event=None):
        if self.url_entry.get() == self.url_entry_placeholder:
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg="#fff")

    def _add_placeholder(self, event=None):
        if not self.url_entry.get():
            self.url_entry.insert(0, self.url_entry_placeholder)
            self.url_entry.config(fg="#b2b2b2")

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
        self.after(0, lambda: self.status_value_label.config(text=f" {emoji} {text}"))

    def setup_folder_selection(self, parent=None) -> None:
        frame_parent = parent if parent is not None else self
        folder_frame = tk.Frame(frame_parent, bg="#18181b")
        folder_frame.pack(pady=8)
        folder_text_label = tk.Label(folder_frame, text="Папка для сохранения:", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        folder_text_label.pack(side="left", padx=(0, 10))
        self.folder_label = tk.Label(folder_frame, text="Не выбрана", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        self.folder_label.pack(side="left", padx=(0, 15))
        choose_folder_btn = ttk.Button(folder_frame, text="Выбрать папку", command=self.choose_folder, style='Rounded.TButton')
        choose_folder_btn.pack(side="left", padx=(10, 0))

    def load_settings(self) -> None:
        self.save_folder = load_folder()
        if self.save_folder:
            self.folder_label.config(text=self.save_folder, fg="white")

    def choose_folder(self) -> None:
        initial_dir = self.save_folder if self.save_folder else "~"
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Выберите папку для сохранения")
        if folder:
            self.save_folder = folder
            self.folder_label.config(text=folder, fg="white")
            save_folder(folder)

    def start_download(self) -> None:
        url = self.url_entry.get().strip()
        if url == self.url_entry_placeholder:
            url = ""
        if not url:
            messagebox.showerror("Ошибка", "Введите ссылку на YouTube видео.")
            return
        if not self.save_folder:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения.")
            return
        if not validate_youtube_url(url):
            messagebox.showerror("Ошибка", "Некорректная ссылка на YouTube.")
            return
        self.download_btn.state(["disabled"])
        self.progress_value_label.config(text=" 0")
        self.set_status("Ищу комментарии...")
        threading.Thread(target=self.download_comments, args=(url,), daemon=True).start()

    def download_comments(self, url: str) -> None:
        try:
            self.set_status("Подготавливаю к скачиванию...")
            comments = download_youtube_comments(url, None)  # Не обновляем прогресс на этапе подготовки
            if not comments:
                self.set_status("")
                self.show_error("Комментарии не найдены.")
                return
            self.set_status("Скачиваю комментарии...")
            # Теперь запускаем скачивание с обновлением прогресса
            comments = download_youtube_comments(url, self.update_progress)
            self.set_status("Сохраняю файл...")
            filepath = get_next_filename(self.save_folder)
            if save_comments_to_file(comments, filepath):
                self.set_status("")
                self.show_success(filepath)
                self.url_entry.delete(0, tk.END)
                self._add_placeholder()
            else:
                self.set_status("")
                self.show_error("Ошибка сохранения файла.")
        except Exception as e:
            self.set_status("")
            self.show_error(str(e))
        finally:
            self.download_btn.state(["!disabled"])
            self.progress_value_label.config(text=" 0")
            self.set_status("Готов к работе")

    def update_progress(self, current: int, total: int) -> None:
        self.after(0, lambda: self.progress_value_label.config(text=f" {current}"))
        self.set_status("Скачиваю комментарии...")

    def show_success(self, filepath: str) -> None:
        self.after(0, lambda: SuccessPopup(self, filepath))

    def show_error(self, msg: str) -> None:
        self.after(0, lambda: messagebox.showerror("Ошибка", msg))
