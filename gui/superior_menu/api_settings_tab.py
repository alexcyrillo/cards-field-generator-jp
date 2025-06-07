import customtkinter as ctk

class ApiSettingsTab(ctk.CTkFrame):
    def __init__(self, master, current_model, api_key_var, model_var):
        super().__init__(master, fg_color="#222")
        ctk.CTkLabel(self, text="OpenAI API Key", font=("Arial", 13, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,2))
        api_entry = ctk.CTkEntry(self, width=540, textvariable=api_key_var, show="*")
        api_entry.pack(pady=(0,10))
        ctk.CTkLabel(self, text="Select AI Model", font=("Arial", 13, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,2))
        model_options = ["gpt-4.1-nano", "gpt-4", "gpt-3.5-turbo"]
        model_menu = ctk.CTkOptionMenu(self, variable=model_var, values=model_options)
        model_menu.pack(pady=(0,10))
        def _on_mousewheel_api(event):
            self.yview_scroll(int(-1*(event.delta/120)), "units") if hasattr(self, 'yview_scroll') else None
        self.bind("<MouseWheel>", _on_mousewheel_api)
        self.bind("<Button-4>", _on_mousewheel_api)
        self.bind("<Button-5>", _on_mousewheel_api)
