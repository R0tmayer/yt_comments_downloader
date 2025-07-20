import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading
import os

from config import *
from settings import save_folder, load_folder
from file_manager import get_next_filename, save_comments_to_file
from downloader import download_youtube_comments, validate_youtube_url
from popup import SuccessPopup
from video_tab import VideoTab
from channel_tab import ChannelTab

class App(tk.Tk):
    """Главное окно приложения."""
    def __init__(self):
        super().__init__()
        self.title("YTCommentsDownloader by R0tmayer")
        self.geometry("700x600")
        self.resizable(False, False)
        self.configure(bg="#18181b")
        self.setup_ui()

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
        style.configure('Red.TButton',
            foreground='#fff',
            background='#d32f2f',
            borderwidth=0,
            focusthickness=0,
            focuscolor='none',
            padding=10,
            relief='flat',
            font=(None, 14, 'bold')
        )
        style.map('Red.TButton',
            background=[('!disabled', '#d32f2f')],
            foreground=[('!disabled', '#fff')]
        )
        style.configure('Primary.TButton',
            foreground='#fff',
            background='#6c63ff',
            borderwidth=0,
            focusthickness=0,
            focuscolor='none',
            padding=10,
            relief='flat',
            font=(None, 14, 'bold')
        )
        style.map('Primary.TButton',
            background=[('active', '#8577ff'), ('pressed', '#574fcf'), ('!disabled', '#6c63ff')],
            foreground=[('!disabled', '#fff')]
        )
        style.layout('Primary.TButton', [
            ('Button.focus', {'children': [
                ('Button.padding', {'children': [
                    ('Button.label', {'side': 'left', 'expand': 1})
                ], 'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
        style.configure('Danger.TButton',
            foreground='#fff',
            background='#d32f2f',
            borderwidth=0,
            focusthickness=0,
            focuscolor='none',
            padding=10,
            relief='flat',
            font=(None, 14, 'bold')
        )
        style.map('Danger.TButton',
            background=[('active', '#b71c1c'), ('pressed', '#b71c1c'), ('!disabled', '#d32f2f')],
            foreground=[('!disabled', '#fff')]
        )
        style.layout('Danger.TButton', [
            ('Button.focus', {'children': [
                ('Button.padding', {'children': [
                    ('Button.label', {'side': 'left', 'expand': 1})
                ], 'sticky': 'nswe'})
            ], 'sticky': 'nswe'})
        ])
        # --- Вкладки ---
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")
        # Вкладка 1
        video_tab = VideoTab(self, notebook)
        notebook.add(video_tab, text="Комментарии с видео")
        # Вкладка 2
        channel_tab = ChannelTab(self, notebook)
        notebook.add(channel_tab, text="Комментарии с канала")
        # Футер
        footer = tk.Frame(self, bg="#23232a", height=36)
        footer.pack(side="bottom", fill="x")
        sep = tk.Frame(self, bg="#444", height=2)
        sep.pack(side="bottom", fill="x")
        footer_inner = tk.Frame(footer, bg="#23232a")
        footer_inner.pack(anchor="center", pady=6)
        footer_label1 = tk.Label(footer_inner, text="2025 by ", font=(None, 13, "bold"), fg="#fff", bg="#23232a")
        footer_label1.grid(row=0, column=0)
        footer_label2 = tk.Label(footer_inner, text="R0tmayer", font=(None, 13, "bold"), fg="#6c63ff", bg="#23232a")
        footer_label2.grid(row=0, column=1)
