import tkinter as tk
from tkinter import ttk
import os

class SuccessPopup(tk.Toplevel):
    """Попап-окно для отображения успешного сохранения файла."""
    def __init__(self, parent, filepath: str, count: int = None, interrupted: bool = False):
        super().__init__(parent)
        self.title("Успех!")
        self.geometry("450x160")
        self.resizable(False, False)
        self.configure(bg="#18181b")
        self.focus()
        self.grab_set()
        self.transient(parent)
        self.after_id = None
        self.setup_ui(filepath, count, interrupted)
        self.start_auto_close_timer()

    def setup_ui(self, filepath: str, count: int = None, interrupted: bool = False) -> None:
        filename = os.path.basename(filepath)
        if interrupted:
            text = f"Скачивание прервано пользователем!\n{filename}\nСкачано: {count} комментариев"
        else:
            text = f"Успешно сохранено в файл:\n{filename}"
            if count is not None:
                text += f"\nСкачано комментариев: {count}"
        label = tk.Label(self, text=text, font=(None, 14), fg="#fff", bg="#18181b")
        label.pack(pady=20)
        style = ttk.Style(self)
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
        close_btn = ttk.Button(self, text="Закрыть", command=self.close_popup, style='Rounded.TButton')
        close_btn.pack(pady=10)

    def start_auto_close_timer(self) -> None:
        self.after_id = self.after(5000, self.close_popup)

    def close_popup(self) -> None:
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.grab_release()
        self.destroy()
