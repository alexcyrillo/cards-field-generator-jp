import customtkinter as ctk
import os
from gui.superior_menu.api_settings_tab import ApiSettingsTab
from gui.superior_menu.prompts_tab import PromptsTab

class ConfigPopup(ctk.CTkToplevel):
    def __init__(self, master, prompt_entries, salvar_callback, current_model="gpt-4.1-nano"):
        super().__init__(master)
        self.title("Configurações")
        self.geometry("650x600")
        self.transient(master)
        tabview = ctk.CTkTabview(self, width=620, height=520)
        tabview.pack(padx=10, pady=10, fill="both", expand=True)
        # Variáveis compartilhadas
        env_path = os.path.join(os.path.dirname(__file__), "../../.env")
        api_key = ""
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.strip().split("=",1)[1]
        self.api_key_var = ctk.StringVar(value=api_key)
        self.model_var = ctk.StringVar(value=current_model)
        # Aba API
        tabview.add("API Settings")
        # Aba Prompts
        tabview.add("Prompts")
        # Adiciona os frames/componentes dentro das abas corretas
        api_tab = ApiSettingsTab(tabview.tab("API Settings"), current_model, self.api_key_var, self.model_var)
        api_tab.pack(fill="both", expand=True)
        self.prompt_entries = {}
        prompts_tab = PromptsTab(tabview.tab("Prompts"), self.prompt_entries)
        prompts_tab.pack(fill="both", expand=True)
        btn_save = ctk.CTkButton(self, text="Save", command=lambda: salvar_callback(self.prompt_entries, self, self.model_var.get(), self.api_key_var.get()))
        btn_save.pack(pady=10)
