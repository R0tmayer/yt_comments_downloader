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
        self.geometry("700x600")
        self.resizable(False, False)
        self.save_folder = None
        self.configure(bg="#18181b")
        self.setup_ui()
        self.load_settings()
        self.set_status("⏸️ Готов к работе")

    def setup_ui(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')
        # Основная кнопка (фиолетовая)
        style.configure('Rounded.TButton',
                        foreground='#fff',
                        background='#6c63ff',
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=10,
                        relief='flat',
                        font=(None, 14, 'bold'))
        style.map('Rounded.TButton',
                  background=[('active', '#8577ff'), ('pressed', '#574fcf')],
                  foreground=[('disabled', '#b2b2b2')])
        style.layout('Rounded.TButton', [
            ('Button.focus', {'children': [
                ('Button.padding', {'children': [
                    ('Button.label', {'side': 'left', 'expand': 1})
                ], 'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
        # Вторичная кнопка (тёмная)
        style.configure('Folder.TButton',
                        foreground='#fff',
                        background='#23232a',
                        borderwidth=0,
                        focusthickness=0,
                        focuscolor='none',
                        padding=8,
                        relief='flat',
                        font=(None, 13))
        style.map('Folder.TButton',
                  background=[('active', '#444'), ('pressed', '#18181b')],
                  foreground=[('disabled', '#b2b2b2')])
        style.layout('Folder.TButton', [
            ('Button.focus', {'children': [
                ('Button.padding', {'children': [
                    ('Button.label', {'side': 'left', 'expand': 1})
                ], 'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
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

        # --- Новый блок выбора количества комментариев ---
        count_block = tk.Frame(
            bottom_block,
            bg="#23232a",
            highlightbackground="#444",
            highlightthickness=2,
            bd=0,
            width=650,
            height=115
        )
        count_block.pack(anchor="w", pady=(18, 0))
        count_block.pack_propagate(False)  # Отключает авто-подгонку по содержимому
        count_block.configure(relief="ridge")
        count_label = tk.Label(count_block, text="📊 Сколько комментариев скачать", font=(None, 15, "bold"), fg="#fff", bg="#23232a")
        count_label.pack(anchor="w", pady=(8, 4), padx=12)
        self.download_mode = tk.StringVar(value="all")
        radio_all = ttk.Radiobutton(count_block, text="Скачать все", variable=self.download_mode, value="all", command=self._toggle_count_entry)
        radio_all.pack(anchor="w", pady=(0, 2), padx=24)
        radio_count = ttk.Radiobutton(count_block, text="Скачать количество:", variable=self.download_mode, value="count", command=self._toggle_count_entry)
        radio_count.pack(anchor="w", pady=(0, 2), padx=24, side="left")
        self.count_entry = tk.Entry(count_block, width=10, font=(None, 15), fg="#fff", bg="#18181b", insertbackground="#fff", relief="flat", bd=0, state="disabled", highlightthickness=1, highlightbackground="#6c63ff")
        self.count_entry.pack(anchor="w", side="left", padx=(8, 0), pady=(0, 2))
        self.count_entry.insert(0, "100")

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

    def _toggle_count_entry(self):
        if self.download_mode.get() == "count":
            self.count_entry.config(state="normal")
        else:
            self.count_entry.config(state="disabled")

    def set_status(self, text: str) -> None:
        # Если текст уже содержит эмодзи в начале, не добавляем второй раз
        emoji_map = [
            "⏸️", "🔍", "🛠️", "📥", "💾", "❌", "✅", "📊"
        ]
        if any(text.strip().startswith(e) for e in emoji_map):
            self.after(0, lambda: self.status_value_label.config(text=f" {text}"))
        else:
            emoji = ""
            if "Ожидание" in text or "Готов" in text:
                emoji = "⏸️"
            elif "Ищу" in text or "Проверяю" in text:
                emoji = "🔍"
            elif "Подготавливаю" in text or "Подключаюсь" in text:
                emoji = "🛠️"
            elif "Скачиваю" in text or "Загружаю" in text:
                emoji = "📥"
            elif "Сохраняю" in text:
                emoji = "💾"
            elif "Ошибка" in text:
                emoji = "❌"
            elif "успешно" in text or "готово" in text or "Готово" in text:
                emoji = "✅"
            elif "Найдено" in text:
                emoji = "📊"
            self.after(0, lambda: self.status_value_label.config(text=f" {emoji} {text}"))

    def setup_folder_selection(self, parent=None) -> None:
        frame_parent = parent if parent is not None else self
        folder_frame = tk.Frame(frame_parent, bg="#18181b")
        folder_frame.pack(pady=8)
        folder_text_label = tk.Label(folder_frame, text="Папка для сохранения:", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        folder_text_label.pack(side="left", padx=(0, 10))
        self.folder_label = tk.Label(folder_frame, text="Не выбрана", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        self.folder_label.pack(side="left", padx=(0, 15))
        choose_folder_btn = ttk.Button(folder_frame, text="Выбрать папку", command=self.choose_folder, style='Folder.TButton')
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
        self.progress_value_label.config(text=" 0")
        self.set_status("Ищу комментарии...")
        # --- Получаем max_comments ---
        max_comments = None
        if self.download_mode.get() == "count":
            try:
                max_comments = int(self.count_entry.get())
                if max_comments <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Ошибка", "Введите корректное количество комментариев.")
                return
        threading.Thread(target=self.download_comments, args=(url, max_comments), daemon=True).start()

    def download_comments(self, url: str, max_comments: int = None) -> None:
        try:
            # Плавная смена статусов
            self.set_status("🔍 Проверяю ссылку...")
            self.after(400, lambda: self.set_status("🛠️ Подключаюсь к YouTube..."))
            self.after(800, lambda: self.set_status("📡 Загружаю страницу видео..."))
            self.after(1200, lambda: self.set_status("🔍 Ищу комментарии..."))
            # Скачиваем комментарии с обновлением статуса и прогресса
            def do_download():
                comments = download_youtube_comments(url, self.update_progress, max_comments)
                if not comments:
                    self.set_status("❌ Комментарии не найдены")
                    self.show_error("Комментарии не найдены.")
                    self.progress_value_label.config(text=" 0")
                    self.set_status("⏸️ Готов к работе")
                    return
                self.set_status("💾 Сохраняю файл...")
                filepath = get_next_filename(self.save_folder)
                if save_comments_to_file(comments, filepath):
                    self.set_status(f"✅ Готово! Файл сохранён ({len(comments)} комментариев)")
                    self.show_success(filepath, len(comments))
                    self.url_entry.delete(0, tk.END)
                    self._add_placeholder()
                else:
                    self.set_status("❌ Ошибка сохранения файла")
                    self.show_error("Ошибка сохранения файла.")
                self.progress_value_label.config(text=" 0")
                self.set_status("⏸️ Готов к работе")
            threading.Thread(target=do_download, daemon=True).start()
        except Exception as e:
            self.set_status("❌ Ошибка при скачивании")
            self.show_error(str(e))
            self.progress_value_label.config(text=" 0")
            self.set_status("⏸️ Готов к работе")

    def update_progress(self, current: int, total: int) -> None:
        self.after(0, lambda: self.progress_value_label.config(text=f" {current}"))
        self.set_status("Скачиваю комментарии...")

    def show_success(self, filepath: str, count: int = None) -> None:
        self.after(0, lambda: SuccessPopup(self, filepath, count))

    def show_error(self, msg: str) -> None:
        self.after(0, lambda: messagebox.showerror("Ошибка", msg))
