import customtkinter as ctk
from core.card_generator import gerar_cards
from core.utils.romaji import romaji_to_japanese
from core.utils.process_word import process_words
from core.utils.export_csv import export_cards_csv
from core.ui_log import log_ui
import threading
from tkinter import filedialog
from gui.result_box import ResultBox
from gui.word_button import WordButton
from gui.card_popup import CardPopup
from gui.superior_menu.config_menu import ConfigPopup

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



    def _on_enter(self, event):
        self.gerar()
        return "break"  # Evita inserir nova linha no textbox

    def gerar(self):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", ctk.END)
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        palavras = process_words(self.input.get("1.0", ctk.END))
        self.input.delete("1.0", ctk.END)  # Novo: limpa o campo de escrita
        if not palavras:
            log_ui(self.result_box, "Nenhuma palavra inserida.")
            self.result_box.configure(state="disabled")
            return
        self.cards = []
        self.palavras = palavras
        self.botoes = {}
        # Cria os botões antes de gerar os cards, todos vermelhos, já em japonês
        for idx, palavra in enumerate(self.palavras):
            palavra_jap = romaji_to_japanese(palavra)
            self._add_button(idx, palavra_jap, fg_color="red")
        self.export_btn.configure(state="disabled")
        threading.Thread(target=self._gerar_cards_thread, daemon=True).start()

    def _gerar_cards_thread(self):
        for idx, palavra in enumerate(self.palavras):
            self.result_box.after(0, log_ui, self.result_box, f"Gerando campos para {palavra}...")
            card = gerar_cards([palavra], log_func=lambda msg: self.result_box.after(0, log_ui, self.result_box, msg))[0]
            self.cards.append(card)
            self.result_box.after(0, self._set_button_color, idx, "blue")
        self.result_box.after(0, log_ui, self.result_box, "Selecione uma palavra para ver os campos.")
        self.result_box.after(0, self.result_box.configure, {"state": "disabled"})
        self.result_box.after(0, self._habilitar_export_btn)

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
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
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

if __name__ == "__main__":
    app = App()
    app.mainloop()
