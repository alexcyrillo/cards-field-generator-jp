import customtkinter as ctk
import os
import json
from configs.prompts import PROMPTS

class ConfigPopup(ctk.CTkToplevel):
    def __init__(self, master, prompt_entries, salvar_callback, current_model="gpt-4.1-nano"):
        super().__init__(master)
        self.title("Configurações")
        self.geometry("650x600")
        self.transient(master)
        tabview = ctk.CTkTabview(self, width=620, height=520)
        tabview.pack(padx=10, pady=10, fill="both", expand=True)
        # Aba API
        api_tab = tabview.add("API Settings")
        api_tab.configure(fg_color="#222")
        ctk.CTkLabel(api_tab, text="OpenAI API Key", font=("Arial", 13, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,2))
        import os
        env_path = os.path.join(os.path.dirname(__file__), "../../.env")
        api_key = ""
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.strip().split("=",1)[1]
        self.api_key_var = ctk.StringVar(value=api_key)
        api_entry = ctk.CTkEntry(api_tab, width=540, textvariable=self.api_key_var, show="*")
        api_entry.pack(pady=(0,10))
        ctk.CTkLabel(api_tab, text="Select AI Model", font=("Arial", 13, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,2))
        self.model_var = ctk.StringVar(value=current_model)
        model_options = ["gpt-4.1-nano", "gpt-4", "gpt-3.5-turbo"]
        model_menu = ctk.CTkOptionMenu(api_tab, variable=self.model_var, values=model_options)
        model_menu.pack(pady=(0,10))
        # Aba Prompts com rolagem
        prompts_tab = tabview.add("Prompts")
        prompts_tab.configure(fg_color="#222")
        # Adiciona frame com canvas e scrollbar para rolagem
        prompts_frame = ctk.CTkFrame(prompts_tab)
        prompts_frame.pack(fill="both", expand=True)
        prompts_canvas = ctk.CTkCanvas(prompts_frame, bg="#222", highlightthickness=0)
        prompts_scrollbar = ctk.CTkScrollbar(prompts_frame, orientation="vertical", command=prompts_canvas.yview)
        prompts_scrollable = ctk.CTkFrame(prompts_canvas, fg_color="#222")
        prompts_scrollable.bind(
            "<Configure>",
            lambda e: prompts_canvas.configure(scrollregion=prompts_canvas.bbox("all"))
        )
        prompts_canvas.create_window((0, 0), window=prompts_scrollable, anchor="nw")
        prompts_canvas.configure(yscrollcommand=prompts_scrollbar.set)
        prompts_canvas.pack(side="left", fill="both", expand=True)
        prompts_scrollbar.pack(side="right", fill="y")
        self.prompt_entries = {}
        ctk.CTkLabel(prompts_scrollable, text="Edit Field Prompts", font=("Arial", 14, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,10))
        for field, value in PROMPTS.items():
            ctk.CTkLabel(prompts_scrollable, text=f"{field}:", font=("Arial", 11, "bold"), anchor="w", text_color="#ffb", fg_color="#222").pack(fill="x", anchor="w")
            lines = value.count("\n") + 1
            max_line_length = max([len(l) for l in value.splitlines()] or [0])
            extra_lines = max_line_length // 55
            total_lines = min(15, lines + extra_lines)
            height = 22 * total_lines  # 22px por linha
            entry = ctk.CTkTextbox(prompts_scrollable, width=540, height=height)
            entry.insert("1.0", value)
            entry.pack(fill="x", anchor="w", pady=(0,10))
            self.prompt_entries[field] = entry
        btn_save = ctk.CTkButton(self, text="Save", command=lambda: salvar_callback(self.prompt_entries, self, self.model_var.get(), self.api_key_var.get()))
        btn_save.pack(pady=10)
        # Scroll do mouse para canvas
        def _on_mousewheel_prompts(event):
            prompts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        prompts_canvas.bind("<MouseWheel>", _on_mousewheel_prompts)
        prompts_canvas.bind("<Button-4>", lambda event: prompts_canvas.yview_scroll(-1, "units"))
        prompts_canvas.bind("<Button-5>", lambda event: prompts_canvas.yview_scroll(1, "units"))

        # Scroll para API tab (Entry e OptionMenu)
        def _on_mousewheel_api(event):
            api_tab.yview_scroll(int(-1*(event.delta/120)), "units") if hasattr(api_tab, 'yview_scroll') else None
        api_tab.bind("<MouseWheel>", _on_mousewheel_api)
        api_tab.bind("<Button-4>", _on_mousewheel_api)
        api_tab.bind("<Button-5>", _on_mousewheel_api)
