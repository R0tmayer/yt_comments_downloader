import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from file_manager import save_comments_to_file
from file_manager import get_next_filename
from downloader import download_youtube_comments
from settings import save_folder, load_folder

class ChannelTab(tk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, bg="#18181b")
        self.app = app
        self.pack(expand=True, fill="both")
        self._setup_ui()
        self._set_channel_status("⏸️ Готов к работе")

    def _setup_ui(self):
        # Заголовок по центру
        title_label = tk.Label(self, text="Комментарии с канала", font=(None, 22, "bold"), fg="#fff", bg="#18181b")
        title_label.pack(anchor="center", fill="x", pady=(24, 4))
        # Верхний блок для выбора папки
        top_block = tk.Frame(self, bg="#18181b")
        top_block.pack(anchor="w", padx=40, pady=(0, 0))
        self.setup_channel_folder_selection(top_block)
        # Блок для ввода ссылки
        url_block = tk.Frame(self, bg="#18181b")
        url_block.pack(anchor="w", padx=40, pady=(18, 0))
        url_label = tk.Label(url_block, text="Ссылка на канал", font=(None, 15), fg="#fff", bg="#18181b")
        url_label.pack(anchor="w", pady=(4, 0))
        self.channel_url_entry = tk.Entry(url_block, width=80, font=(None, 14), fg="#fff", bg="#23232a", insertbackground="#fff", relief="solid", bd=2)
        self.channel_url_entry.pack(anchor="w", pady=4, ipady=8)
        self.channel_url_entry.insert(0, "https://www.youtube.com/@ЛайфхакиПутешествий")
        self.channel_url_entry_placeholder = "Вставьте ссылку на канал..."
        self.channel_url_entry.bind("<FocusIn>", self._clear_channel_placeholder)
        self.channel_url_entry.bind("<FocusOut>", self._add_channel_placeholder)
        self._add_channel_placeholder()
        # --- Блок выбора количества видео ---
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
        count_label = tk.Label(count_block, text="📊 Сколько видео обработать", font=(None, 15, "bold"), fg="#fff", bg="#23232a")
        count_label.pack(anchor="w", pady=(8, 4), padx=12)
        self.video_download_mode = tk.StringVar(value="all")
        radio_all = ttk.Radiobutton(count_block, text="Обработать все", variable=self.video_download_mode, value="all", command=self._toggle_video_count_entry)
        radio_all.pack(anchor="w", pady=(0, 2), padx=24)
        radio_count = ttk.Radiobutton(count_block, text="Обработать количество:", variable=self.video_download_mode, value="count", command=self._toggle_video_count_entry)
        radio_count.pack(anchor="w", pady=(0, 2), padx=24, side="left")
        self.video_count_entry = tk.Entry(count_block, width=10, font=(None, 15), fg="#fff", bg="#18181b", insertbackground="#fff", relief="flat", bd=0, state="disabled", highlightthickness=1, highlightbackground="#6c63ff")
        self.video_count_entry.pack(anchor="w", side="left", padx=(8, 0), pady=(0, 2))
        self.video_count_entry.insert(0, "5")
        # Кнопки
        btn_block = tk.Frame(self, bg="#18181b")
        btn_block.pack(anchor="w", padx=40, pady=(16, 0))
        self.channel_download_btn = ttk.Button(
            btn_block,
            text="Скачать комментарии",
            command=self.start_channel_download,
            style='Primary.TButton')
        self.channel_download_btn.pack(side="left")
        self.channel_stop_btn = ttk.Button(
            btn_block,
            text="СТОП",
            style='Danger.TButton',
            command=self.stop_channel_download,
            state="normal"
        )
        self.channel_stop_btn.pack(side="left", padx=(16, 0))
        # Прогресс
        progress_block = tk.Frame(self, bg="#18181b")
        progress_block.pack(anchor="w", padx=40, pady=(16, 0))
        self.channel_progress_label = tk.Label(progress_block, text="Скачано комментариев: 0", font=(None, 13), fg="#b2b2b2", bg="#18181b", anchor="w")
        self.channel_progress_label.pack(side="left")
        # Статус
        status_block = tk.Frame(self, bg="#18181b")
        status_block.pack(anchor="w", padx=40, pady=(4, 20))
        self.channel_status_label = tk.Label(status_block, text="Статус: ", font=(None, 13), fg="#b2b2b2", bg="#18181b", anchor="w")
        self.channel_status_label.pack(side="left")
        self.status_value_label = tk.Label(status_block, text="", font=(None, 13, "bold"), fg="#b2b2b2", bg="#18181b")
        self.status_value_label.pack(side="left")

    def setup_channel_folder_selection(self, parent=None):
        frame_parent = parent if parent is not None else self
        folder_frame = tk.Frame(frame_parent, bg="#18181b")
        folder_frame.pack(pady=8, fill="x")
        folder_text_label = tk.Label(folder_frame, text="Папка для сохранения:", font=(None, 14), fg="#b2b2b2", bg="#18181b")
        folder_text_label.pack(side="left", padx=(0, 10))
        self.channel_folder_label = tk.Label(folder_frame, text="Не выбрана", font=(None, 14), fg="#b2b2b2", bg="#18181b", anchor="w", width=35)
        self.channel_folder_label.pack(side="left", fill="x", expand=True, padx=(0, 8))
        choose_folder_btn = ttk.Button(folder_frame, text="Выбрать", command=self.choose_channel_folder, style='Folder.TButton')
        choose_folder_btn.pack(side="right", padx=(10, 0))
        self.load_channel_folder()

    def load_channel_folder(self):
        self.channel_save_folder = load_folder()
        if self.channel_save_folder:
            self.channel_folder_label.config(text=self.channel_save_folder, fg="white")

    def choose_channel_folder(self) -> None:
        initial_dir = self.channel_save_folder if self.channel_save_folder else "~"
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Выберите папку для сохранения")
        if folder:
            self.channel_save_folder = folder
            self.channel_folder_label.config(text=folder, fg="white")
            save_folder(folder)

    def _toggle_video_count_entry(self):
        if self.video_download_mode.get() == "count":
            self.video_count_entry.config(state="normal")
        else:
            self.video_count_entry.config(state="disabled")

    def stop_channel_download(self):
        self._stop_channel_download = True
        self.channel_stop_btn.state(["disabled"])

    def _clear_channel_placeholder(self, event=None):
        if self.channel_url_entry.get() == self.channel_url_entry_placeholder:
            self.channel_url_entry.delete(0, tk.END)
            self.channel_url_entry.config(fg="#fff")

    def _add_channel_placeholder(self, event=None):
        if not self.channel_url_entry.get():
            self.channel_url_entry.insert(0, self.channel_url_entry_placeholder)
            self.channel_url_entry.config(fg="#b2b2b2")

    def start_channel_download(self):
        self._stop_channel_download = False  # Сброс флага всегда при новом запуске
        url = self.channel_url_entry.get().strip()
        if url == self.channel_url_entry_placeholder:
            url = ""
        if not url:
            messagebox.showerror("Ошибка", "Введите ссылку на канал.")
            return
        # Фильтр: если это ссылка на видео, показываем ошибку
        if "youtube.com/watch?v=" in url or "youtu.be/" in url:
            messagebox.showerror("Ошибка", "Введите ссылку на канал, а не на видео!")
            return
        if not hasattr(self, 'channel_save_folder') or not self.channel_save_folder:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения.")
            return
        self.channel_stop_btn.state(["!disabled"])
        self.channel_download_btn.state(["disabled"])
        self.channel_progress_label.config(text="Скачано комментариев: 0")
        self.channel_status_label.config(text="Статус: ")
        # определяем лимит видео
        max_videos = None
        if self.video_download_mode.get() == "count":
            try:
                max_videos = int(self.video_count_entry.get())
                if max_videos <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Ошибка", "Введите корректное количество видео.")
                self.channel_download_btn.state(["!disabled"])
                return
        threading.Thread(target=self._download_channel_comments, args=(url, max_videos), daemon=True).start()

    def _download_channel_comments(self, channel_url, max_videos=None):
        import requests, re
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        self._set_channel_status("⏸️ Готов к работе")
        self._set_channel_status("Ищу видео на канале...")
        video_ids = self._get_last_videos(channel_url, max_videos=max_videos)
        if not video_ids:
            self._set_channel_status("❌ Не удалось найти видео на канале")
            self.channel_download_btn.state(["!disabled"])
            self.channel_stop_btn.state(["disabled"])
            return
        created_files = []
        max_workers = min(5, len(video_ids))  # до 5 потоков
        stop_flag = self
        def process_video(idx, video_id):
            if getattr(stop_flag, '_stop_channel_download', False):
                return (idx, None, None, '⏹️ Скачивание прервано пользователем')
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            comments = []
            def progress_callback(current, total):
                self.channel_progress_label.config(text=f"Скачано комментариев: {current}")
                if getattr(stop_flag, '_stop_channel_download', False):
                    raise Exception("Остановлено пользователем")
            try:
                comments = download_youtube_comments(video_url, progress_callback)
            except Exception as e:
                return (idx, None, None, f"⏹️ Остановлено: {e}")
            if comments:
                folder = self.channel_save_folder if self.channel_save_folder else "."
                filename = get_next_filename(folder)
                save_comments_to_file(comments, filename)
                return (idx, filename, len(comments), f"💾 Сохранено: {filename}")
            else:
                return (idx, None, 0, f"❌ Нет комментариев для видео {idx+1}")
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, video_id in enumerate(video_ids):
                futures.append(executor.submit(process_video, idx, video_id))
            for f in as_completed(futures):
                idx, filename, count, status = f.result()
                self._set_channel_status(status)
                if filename:
                    created_files.append(filename)
                self.channel_progress_label.config(text="Скачано комментариев: 0")
                time.sleep(0.5)
                if getattr(self, '_stop_channel_download', False):
                    break
        if not getattr(self, '_stop_channel_download', False):
            self._set_channel_status(f"✅ Готово! Обработано {len(created_files)} видео")
            self.channel_download_btn.state(["!disabled"])
            self.channel_stop_btn.state(["disabled"])
            self.after(0, lambda: self.show_channel_success_popup(created_files, len(video_ids)))
        else:
            self.channel_download_btn.state(["!disabled"])
            self.channel_stop_btn.state(["disabled"])
            self.after(0, lambda: self.show_channel_success_popup(created_files, len(video_ids), interrupted=True))

    def _set_channel_status(self, text):
        # Добавляю эмодзи к статусам
        emoji_map = [
            "⏸️", "🔍", "🛠️", "📥", "💾", "❌", "✅", "📊", "⏹️"
        ]
        if any(text.strip().startswith(e) for e in emoji_map):
            self.channel_status_label.config(text=f"Статус: {text}")
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
            elif "прервано" in text or "Остановлено" in text:
                emoji = "⏹️"
            else:
                emoji = "ℹ️"
            self.channel_status_label.config(text=f"Статус: {emoji} {text}")

    def _get_last_videos(self, channel_url, max_videos=5):
        import requests, re
        try:
            html = requests.get(channel_url).text
            video_ids = re.findall(r'"videoId":"([\w-]{11})"', html)
            seen = set()
            unique_ids = []
            for vid in video_ids:
                if vid not in seen:
                    unique_ids.append(vid)
                    seen.add(vid)
                if max_videos is not None and len(unique_ids) >= max_videos:
                    break
            return unique_ids
        except Exception:
            return []

    def show_channel_success_popup(self, file_list, total_videos, interrupted=False):
        import tkinter as tk
        popup = tk.Toplevel(self)
        popup.title("Успех!" if not interrupted else "Обработка прервана")
        popup.geometry("500x300")
        popup.configure(bg="#18181b")
        popup.grab_set()
        popup.focus()
        if interrupted:
            msg = f"Обработка прервана пользователем!\nСоздано файлов: {len(file_list)} из {total_videos}\n\nСозданные файлы:"
        else:
            msg = f"Успешно обработано {len(file_list)} видео из {total_videos}!\n\nСозданные файлы:"
        label = tk.Label(popup, text=msg, font=(None, 14), fg="#fff", bg="#18181b")
        label.pack(pady=(20, 10))
        files_text = "\n".join([os.path.basename(f) for f in file_list])
        files_label = tk.Label(popup, text=files_text, font=(None, 12), fg="#6c63ff", bg="#18181b", justify="left")
        files_label.pack(pady=(0, 20))
        if len(file_list) < total_videos:
            warn = tk.Label(popup, text="Не для всех видео были найдены комментарии.", font=(None, 12), fg="#ffb300", bg="#18181b")
            warn.pack(pady=(0, 10))
        close_btn = tk.Button(popup, text="Закрыть", command=popup.destroy, font=(None, 12), bg="#fff", fg="#23232a", relief="flat", padx=16, pady=6)
        close_btn.pack(pady=(0, 16)) 