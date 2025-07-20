"""
Модуль для отображения попап-окна с результатом операции.
"""

import customtkinter as ctk
import os

class SuccessPopup(ctk.CTkToplevel):
    """Попап-окно для отображения успешного сохранения файла."""
    def __init__(self, parent, filepath: str):
        super().__init__(parent)
        self.title("Успех!")
        self.geometry("450x120")
        self.resizable(False, False)
        self.focus()
        self.grab_set()
        self.transient(parent)
        self.after_id = None
        self.setup_ui(filepath)
        self.start_auto_close_timer()

    def setup_ui(self, filepath: str) -> None:
        filename = os.path.basename(filepath)
        label = ctk.CTkLabel(self, text=f"Успешно сохранено в файл:\n{filename}", font=ctk.CTkFont(size=14))
        label.pack(pady=20)
        close_btn = ctk.CTkButton(self, text="Закрыть", command=self.close_popup)
        close_btn.pack(pady=10)

    def start_auto_close_timer(self) -> None:
        self.after_id = self.after(5000, self.close_popup)

    def close_popup(self) -> None:
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.grab_release()
        self.destroy()
