import customtkinter as ctk

class ResultBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
