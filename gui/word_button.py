import customtkinter as ctk

class WordButton(ctk.CTkButton):
    def __init__(self, master, text, command, fg_color):
        super().__init__(master, text=text, command=command, fg_color=fg_color)
