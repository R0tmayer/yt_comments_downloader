import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading
import os
from config import *
from settings import save_folder, load_folder
from file_manager import get_next_filename, save_comments_to_file
from downloader import download_youtube_comments, validate_youtube_url
from popup import SuccessPopup

class VideoTab(tk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, bg="#18181b")
        self.app = app
        self.pack(expand=True, fill="both")
        self._setup_ui()
        self.set_status("⏸️ Готов к работе")

    def _setup_ui(self):
        # Заголовок по центру
        title_label = tk.Label(self, text="Комментарии с видео", font=(None, 22, "bold"), fg="#fff", bg="#18181b")
        title_label.pack(anchor="center", fill="x", pady=(24, 4))
        # Верхний блок для выбора папки
        top_block = tk.Frame(self, bg="#18181b")
        top_block.pack(anchor="w", padx=40, pady=(0, 0))
        self.setup_folder_selection(top_block)
        # Блок для ввода ссылки
        url_block = tk.Frame(self, bg="#18181b")
        url_block.pack(anchor="w", padx=40, pady=(18, 0))
        url_label = tk.Label(url_block, text="Ссылка на видео", font=(None, 15), fg="#fff", bg="#18181b")
        url_label.pack(anchor="w", pady=(4, 0))
        self.url_entry = tk.Entry(url_block, width=80, font=(None, 14), fg="#fff", bg="#23232a", insertbackground="#fff", relief="solid", bd=2)
        self.url_entry.pack(anchor="w", pady=4, ipady=8)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=1-q0VFBcVDM")
        self.url_entry_placeholder = "Вставьте ссылку на видео..."
        self.url_entry.bind("<FocusIn>", self._clear_placeholder)
        self.url_entry.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()
        # --- Блок выбора количества комментариев ---
        count_block = tk.Frame(
            self,
            bg="#23232a",
            highlightbackground="#444",
            highlightthickness=2,
            bd=0,
            width=650,
            height=115
        )
        count_block.pack(anchor="w", padx=40, pady=(18, 0))
        count_block.pack_propagate(False)
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
        # Кнопки
        btn_block = tk.Frame(self, bg="#18181b")
        btn_block.pack(anchor="w", padx=40, pady=(16, 0))
        self.download_btn = ttk.Button(
            btn_block,
            text="Скачать комментарии",
            command=self.start_download,
            style='Primary.TButton')
        self.download_btn.pack(side="left")
        self.stop_btn = ttk.Button(
            btn_block,
            text="СТОП",
            style='Danger.TButton',
            command=self.stop_download,
            state="normal"
        )
        self.stop_btn.pack(side="left", padx=(16, 0))
        # Прогресс
        progress_frame = tk.Frame(self, bg="#18181b")
        progress_frame.pack(anchor="w", padx=40, pady=(16, 0))
        self.progress_label = tk.Label(progress_frame, text="Скачано комментариев:", font=(None, 13), fg="#b2b2b2", bg="#18181b")
        self.progress_label.pack(side="left")
        self.progress_value_label = tk.Label(progress_frame, text=" 0", font=(None, 13, "bold"), fg="#b2b2b2", bg="#18181b")
        self.progress_value_label.pack(side="left")
        # Статус
        status_frame = tk.Frame(self, bg="#18181b")
        status_frame.pack(anchor="w", padx=40, pady=(4, 20))
        self.status_label = tk.Label(status_frame, text="Статус: ", font=(None, 13), fg="#b2b2b2", bg="#18181b")
        self.status_label.pack(side="left")
        self.status_value_label = tk.Label(status_frame, text="", font=(None, 13, "bold"), fg="#b2b2b2", bg="#18181b")
        self.status_value_label.pack(side="left")

    def setup_folder_selection(self, parent=None) -> None:
        frame_parent = parent if parent is not None else self
        folder_frame = tk.Frame(frame_parent, bg="#18181b")
        folder_frame.pack(pady=8, fill="x")
        folder_text_label = tk.Label(folder_frame, text="Папка для сохранения:", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        folder_text_label.pack(side="left", padx=(0, 10))
        self.folder_label = tk.Label(folder_frame, text="Не выбрана", font=(None, 14), fg="#b2b2b2", bg="#18181b", anchor="w", width=35)
        self.folder_label.pack(side="left", fill="x", expand=True, padx=(0, 8))
        choose_folder_btn = ttk.Button(folder_frame, text="Выбрать", command=self.choose_folder, style='Folder.TButton')
        choose_folder_btn.pack(side="right", padx=(10, 0))
        self.load_settings()

    def load_settings(self) -> None:
        self.save_folder = load_folder()
        if self.save_folder:
            self.folder_label.config(text=self.save_folder, fg="white")

    def choose_folder(self) -> None:
        initial_dir = self.save_folder if hasattr(self, 'save_folder') and self.save_folder else "~"
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Выберите папку для сохранения")
        if folder:
            self.save_folder = folder
            self.folder_label.config(text=folder, fg="white")
            save_folder(folder)

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

    def update_progress(self, current: int, total: int) -> None:
        self.after(0, lambda: self.progress_value_label.config(text=f" {current}"))
        self.set_status("Скачиваю комментарии...")

    def _comment_iter(self, url, max_comments):
        from downloader import download_youtube_comments
        for idx, comment in enumerate(download_youtube_comments(url, yield_comments=True, max_comments=max_comments)):
            yield comment

    def show_success(self, filepath: str, count: int = None, interrupted: bool = False) -> None:
        self.after(0, lambda: SuccessPopup(self, filepath, count, interrupted))

    def show_error(self, msg: str) -> None:
        self.after(0, lambda: messagebox.showerror("Ошибка", msg)) 

    def start_download(self):
        url = self.url_entry.get().strip()
        if url == self.url_entry_placeholder:
            url = ""
        if not url:
            self.show_error("Введите ссылку на YouTube видео.")
            return
        if not hasattr(self, 'save_folder') or not self.save_folder:
            self.show_error("Выберите папку для сохранения.")
            return
        if not validate_youtube_url(url):
            self.show_error("Некорректная ссылка на YouTube.")
            return
        self.progress_value_label.config(text=" 0")
        self.set_status("Ищу комментарии...")
        self._stop_download = False
        self.stop_btn.config(state="normal")
        max_comments = None
        if self.download_mode.get() == "count":
            try:
                max_comments = int(self.count_entry.get())
                if max_comments <= 0:
                    raise ValueError
            except Exception:
                self.show_error("Введите корректное количество комментариев.")
                return
        threading.Thread(target=self.download_comments, args=(url, max_comments), daemon=True).start()

    def stop_download(self):
        self._stop_download = True
        self.stop_btn.config(state="disabled")

    def download_comments(self, url: str, max_comments: int = None) -> None:
        try:
            self.set_status("🔍 Проверяю ссылку...")
            self.after(400, lambda: self.set_status("🛠️ Подключаюсь к YouTube..."))
            self.after(800, lambda: self.set_status("📡 Загружаю страницу видео..."))
            self.after(1200, lambda: self.set_status("🔍 Ищу комментарии..."))
            def do_download():
                comments = []
                interrupted = False
                for idx, comment in enumerate(self._comment_iter(url, max_comments)):
                    if self._stop_download:
                        interrupted = True
                        break
                    comments.append(comment)
                    self.update_progress(idx + 1, 0)
                self.stop_btn.config(state="disabled")
                if not comments:
                    self.set_status("❌ Комментарии не найдены")
                    self.show_error("Комментарии не найдены.")
                    self.progress_value_label.config(text=" 0")
                    self.set_status("⏸️ Готов к работе")
                    return
                self.set_status("💾 Сохраняю файл...")
                filepath = get_next_filename(self.save_folder)
                if save_comments_to_file(comments, filepath):
                    if interrupted:
                        self.set_status(f"⏹️ Скачивание прервано пользователем ({len(comments)} комментариев)")
                        self.show_success(filepath, len(comments), interrupted=True)
                    else:
                        self.set_status(f"✅ Готово! Файл сохранён ({len(comments)} комментариев)")
                        self.show_success(filepath, len(comments))
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