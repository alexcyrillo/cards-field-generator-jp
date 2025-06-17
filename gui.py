import customtkinter as ctk
from core.card_generator import gerar_cards
from core.utils.romaji_conversor import romaji_to_japanese
from core.utils.process_word import process_words
from core.utils.export_csv import export_cards_csv
from core.ui_log import log_ui
import threading
from tkinter import filedialog
from gui.result_box import ResultBox
from gui.word_button import WordButton
from gui.card_popup import CardPopup
from gui.superior_menu.config_menu import ConfigPopup
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Cards Japonês")
        self.geometry("500x600")

        # Menu superior para configurações futuras
        self.menu_bar = ctk.CTkFrame(self, height=28)
        self.menu_bar.pack(side="top", fill="x")
        self.menu_btn = ctk.CTkButton(self.menu_bar, text="Configurações...", width=120, command=self.abrir_configuracoes)
        self.menu_btn.pack(side="left", padx=5, pady=2)

        self.label = ctk.CTkLabel(self, text="Digite as palavras separadas por vírgula:")
        self.label.pack(pady=5)

        self.input = ctk.CTkTextbox(self, width=450, height=40)
        self.input.pack(pady=5)
        self.input.bind("<Return>", self._on_enter)  # Novo: bind Enter

        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(pady=10)

        self.button = ctk.CTkButton(self.action_frame, text="Gerar", command=self.gerar)
        self.button.pack(side="left", padx=5)

        self.export_btn = ctk.CTkButton(self.action_frame, text="Exportar CSV", command=self.exportar_csv, state="disabled")
        self.export_btn.pack(side="left", padx=5)

        self.result_label = ctk.CTkLabel(self, text="Resultados:")
        self.result_label.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self, width=450, height=100)
        self.button_frame.pack(pady=5)

        self.result_box = ResultBox(self, width=450, height=200)
        self.result_box.pack(pady=5)
        self.result_box.configure(state="disabled")

        self.cards = []
        self.palavras = []
        self.botoes = {}  # Novo: armazena referência dos botões

        # Idioma e threads
        self.idioma = "pt"
        self.num_threads = 5
        self.idiomas = {"pt": "Português", "en": "English", "ja": "日本語"}
        self.trad = {
            "pt": {
                "title": "Gerador de Cards Japonês",
                "input_label": "Digite as palavras separadas por vírgula:",
                "generate": "Gerar",
                "export": "Exportar CSV",
                "results": "Resultados:",
                "config": "Configurações...",
                "progress": "Progresso:",
                "no_words": "Nenhuma palavra inserida.",
                "select_word": "Selecione uma palavra para ver os campos:"
            },
            "en": {
                "title": "Japanese Card Generator",
                "input_label": "Enter words separated by comma:",
                "generate": "Generate",
                "export": "Export CSV",
                "results": "Results:",
                "config": "Settings...",
                "progress": "Progress:"
            },
            "ja": {
                "title": "日本語カードジェネレーター",
                "input_label": "単語をカンマ区切りで入力してください：",
                "generate": "生成",
                "export": "CSVエクスポート",
                "results": "結果：",
                "config": "設定...",
                "progress": "進捗："
            }
        }
        # Idioma selector
        self.idioma_var = ctk.StringVar(value=self.idioma)
        self.idioma_menu = ctk.CTkOptionMenu(self.menu_bar, variable=self.idioma_var, values=list(self.idiomas.keys()), command=self._trocar_idioma)
        self.idioma_menu.pack(side="right", padx=5)
        # Threads selector
        self.threads_var = ctk.IntVar(value=self.num_threads)
        self.threads_label = ctk.CTkLabel(self.menu_bar, text="Threads:")
        self.threads_label.pack(side="right", padx=2)
        self.threads_entry = ctk.CTkEntry(self.menu_bar, width=40, textvariable=self.threads_var)
        self.threads_entry.pack(side="right", padx=2)
        # Barra de progresso
        self.progress_label = ctk.CTkLabel(self, text=self.trad[self.idioma]["progress"])
        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.set(0)
        self.progress_label.pack(pady=(5,0))
        self.progress.pack(pady=(0,5))

        # Paleta de cores concisa
        self.bg_color = "#181c24"
        self.fg_color = "#222"
        self.accent_color = "#2e6cf6"
        self.text_color = "#fff"
        self.button_color = "#2e6cf6"
        self.button_fg = "#fff"
        self.button_fg_disabled = "#aaa"
        # self.result_box.configure(bg_color=self.bg_color, fg_color=self.fg_color, text_color=self.text_color)
        self.configure(bg_color=self.bg_color)
        self.menu_bar.configure(fg_color=self.fg_color, bg_color=self.bg_color)
        self.action_frame.configure(fg_color=self.bg_color)
        self.button.configure(fg_color=self.button_color, text_color=self.button_fg)
        self.export_btn.configure(fg_color=self.button_color, text_color=self.button_fg_disabled)
        self.label.configure(text_color=self.text_color, fg_color=self.bg_color)
        self.result_label.configure(text_color=self.text_color, fg_color=self.bg_color)
        self.button_frame.configure(fg_color=self.bg_color)
        self.progress_label.configure(text_color=self.text_color, fg_color=self.bg_color)
        self.progress.configure(progress_color=self.accent_color, fg_color=self.fg_color)
        self.threads_label.configure(text_color=self.text_color, fg_color=self.bg_color)
        self.threads_entry.configure(fg_color=self.fg_color, text_color=self.text_color)
        self.idioma_menu.configure(fg_color=self.fg_color, text_color=self.text_color)
        self.menu_btn.configure(fg_color=self.button_color, text_color=self.button_fg)

        # Ícones e feedback visual
        # from PIL import Image, ImageTk
        # Adiciona ícone de engrenagem ao botão de configurações
        # engrenagem_path = os.path.join(os.path.dirname(__file__), "gui", "assets", "gear.png")
        # if os.path.exists(engrenagem_path):
        #     engrenagem_img = ctk.CTkImage(light_image=Image.open(engrenagem_path), size=(18, 18))
        #     self.menu_btn.configure(image=engrenagem_img, compound="left")
        # Adiciona botão limpar tudo
        self.limpar_btn = ctk.CTkButton(self.menu_bar, text="🧹", width=30, command=self._limpar_tudo, fg_color=self.fg_color, text_color=self.text_color)
        self.limpar_btn.pack(side="right", padx=2)
        # Atalhos de teclado
        self.bind("<Control-e>", lambda e: self.exportar_csv())
        self.bind("<Control-g>", lambda e: self.gerar())
        self.bind("<Escape>", lambda e: self._fechar_popups())
        # Feedback visual/spinner
        self.spinner = ctk.CTkLabel(self, text="", text_color=self.accent_color, fg_color=self.bg_color)
        self.spinner.pack(pady=(0,0))
        # Progresso com porcentagem
        self.progress_percent = ctk.CTkLabel(self, text="0%", text_color=self.text_color, fg_color=self.bg_color)
        self.progress_percent.pack(pady=(0,5))
        # Último diretório exportação
        self.last_export_dir = os.path.expanduser("~")

    def _on_enter(self, event):
        self.gerar()
        return "break"  # Evita inserir nova linha no textbox

    def gerar(self):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", ctk.END)
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        palavras = process_words(self.input.get("1.0", ctk.END))
        self.input.delete("1.0", ctk.END)
        if not palavras:
            log_ui(self.result_box, self.trad[self.idioma].get("no_words", "Nenhuma palavra inserida."))
            self.result_box.configure(state="disabled")
            return
        self.cards = []
        self.palavras = palavras
        self.botoes = {}
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.progress_label.configure(text=self.trad[self.idioma]["progress"])
        self.spinner.configure(text="⏳")
        self.button.configure(state="disabled")
        for idx, palavra in enumerate(self.palavras):
            palavra_jap = romaji_to_japanese(palavra)
            self._add_button(idx, palavra_jap, fg_color=self.button_color)
        self.export_btn.configure(state="disabled")
        self.num_threads = max(1, int(self.threads_var.get()))
        threading.Thread(target=self._gerar_cards_thread, daemon=True).start()

    def _gerar_cards_thread(self):
        total = len(self.palavras)
        for idx, palavra in enumerate(self.palavras):
            log_ui(self.result_box, f"Gerando campos para {palavra}...")
            card = gerar_cards([palavra], log_func=lambda msg: self.result_box.after(0, log_ui, self.result_box, msg), num_threads=self.num_threads)[0]
            self.cards.append(card)
            self.result_box.after(0, self._set_button_color, idx, self.accent_color)
            self.progress.after(0, self.progress.set, (idx+1)/total)
            self.progress_percent.after(0, self.progress_percent.configure, {"text": f"{int((idx+1)/total*100)}%"})
        log_ui(self.result_box, self.trad[self.idioma].get("select_word", "Selecione uma palavra para ver os campos."))
        self.result_box.configure(state="disabled")
        self.after(0, self._habilitar_export_btn)
        self.progress.after(0, self.progress.set, 1)
        self.progress_percent.after(0, self.progress_percent.configure, {"text": "100%"})
        self.spinner.after(0, self.spinner.configure, {"text": "✔️"})
        self.button.after(0, self.button.configure, {"state": "normal"})

    def _habilitar_export_btn(self):
        self.export_btn.configure(state="normal")

    def _add_button(self, idx, palavra, fg_color="red"):
        btn = WordButton(self.button_frame, text=palavra, command=lambda i=idx: self.mostrar_card(i), fg_color=fg_color)
        btn.pack(side="left", padx=5)
        self.botoes[idx] = btn

    def _set_button_color(self, idx, color):
        btn = self.botoes.get(idx)
        if btn:
            btn.configure(fg_color=color)

    def mostrar_card(self, idx):
        card = self.cards[idx]
        palavra_jap = self.botoes[idx].cget("text") if idx in self.botoes else "Palavra"
        campos = ["Kanji", "Conjugação", "Tradução", "Definição", "Exemplos de uso", "Formalidade"]
        def clipboard_func(text):
            self.clipboard_clear()
            self.clipboard_append(text)
        CardPopup(self, card, palavra_jap, campos, clipboard_func)

    def exportar_csv(self):
        if not self.cards:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialdir=self.last_export_dir)
        if not file_path:
            return
        self.last_export_dir = os.path.dirname(file_path)
        export_cards_csv(self.cards, file_path)
        log_ui(self.result_box, f"Exportado para {file_path}")

    def abrir_configuracoes(self):
        import os
        import json
        from configs.prompts import PROMPTS
        from integrations.openai_client import MODEL
        def salvar_prompts(prompt_entries, popup, selected_model, api_key):
            novo_prompts = {campo: prompt_entries[campo].get("1.0", "end").strip() for campo in PROMPTS.keys()}
            conteudo = "PROMPTS = {\n"
            for campo, valor in novo_prompts.items():
                conteudo += f'    "{campo}": {json.dumps(valor)},\n'
            conteudo += "}\n"
            path_prompts = os.path.join(os.path.dirname(__file__), "configs", "prompts.py")
            with open(path_prompts, "w", encoding="utf-8") as f:
                f.write(conteudo)
            # Salva modelo de IA e API KEY em .env
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            found_model = False
            found_key = False
            for i, line in enumerate(lines):
                if line.startswith("MODEL="):
                    lines[i] = f"MODEL={selected_model}\n"
                    found_model = True
                if line.startswith("OPENAI_API_KEY="):
                    lines[i] = f"OPENAI_API_KEY={api_key}\n"
                    found_key = True
            if not found_model:
                lines.append(f"MODEL={selected_model}\n")
            if not found_key:
                lines.append(f"OPENAI_API_KEY={api_key}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            popup.destroy()
        # Lê modelo atual e chave do .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        current_model = "gpt-4.1-nano"
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MODEL="):
                        current_model = line.strip().split("=",1)[1]
        ConfigPopup(self, {}, salvar_prompts, current_model=current_model)

    def _trocar_idioma(self, idioma):
        self.idioma = idioma
        self.title(self.trad[idioma]["title"])
        self.label.configure(text=self.trad[idioma]["input_label"])
        self.button.configure(text=self.trad[idioma]["generate"])
        self.export_btn.configure(text=self.trad[idioma]["export"])
        self.result_label.configure(text=self.trad[idioma]["results"])
        self.menu_btn.configure(text=self.trad[idioma]["config"])
        self.progress_label.configure(text=self.trad[idioma]["progress"])

    def _limpar_tudo(self):
        self.input.delete("1.0", ctk.END)
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", ctk.END)
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.cards = []
        self.palavras = []
        self.botoes = {}
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
        self.export_btn.configure(state="disabled")
        self.spinner.configure(text="")
        self.button.configure(state="normal")

    def _fechar_popups(self):
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkToplevel):
                w.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
