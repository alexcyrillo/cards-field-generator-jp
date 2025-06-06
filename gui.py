import customtkinter as ctk
from core.card_generator import gerar_cards, romaji_para_japones
from core.utils import processar_palavras, exportar_cards_csv
from core.ui_log import log_ui
import threading
import csv
from tkinter import filedialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gerador de Cards Japonês")
        self.geometry("700x600")

        self.label = ctk.CTkLabel(self, text="Digite as palavras separadas por vírgula:")
        self.label.pack(pady=10)

        self.input = ctk.CTkTextbox(self, width=600, height=80)
        self.input.pack(pady=5)
        self.input.bind("<Return>", self._on_enter)  # Novo: bind Enter

        self.button = ctk.CTkButton(self, text="Gerar", command=self.gerar)
        self.button.pack(pady=10)

        self.result_label = ctk.CTkLabel(self, text="Resultados:")
        self.result_label.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=5)

        self.result_box = ctk.CTkTextbox(self, width=650, height=350)
        self.result_box.pack(pady=5)
        self.result_box.configure(state="disabled")

        self.cards = []
        self.palavras = []
        self.botoes = {}  # Novo: armazena referência dos botões

        self.export_btn = ctk.CTkButton(self, text="Exportar CSV", command=self.exportar_csv, state="disabled")
        self.export_btn.pack(pady=5)

    def _on_enter(self, event):
        self.gerar()
        return "break"  # Evita inserir nova linha no textbox

    def gerar(self):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", ctk.END)
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        palavras = processar_palavras(self.input.get("1.0", ctk.END))
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
            palavra_jap = romaji_para_japones(palavra)
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
        btn = ctk.CTkButton(self.button_frame, text=palavra, command=lambda i=idx: self.mostrar_card(i), fg_color=fg_color)
        btn.pack(side="left", padx=5)
        self.botoes[idx] = btn

    def _set_button_color(self, idx, color):
        btn = self.botoes.get(idx)
        if btn:
            btn.configure(fg_color=color)

    def mostrar_card(self, idx):
        card = self.cards[idx]
        # Limpa a área de resultados e exibe os campos do card selecionado
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", ctk.END)
        for campo, conteudo in card.items():
            self.result_box.insert(ctk.END, f"{campo}: {conteudo}\n\n")
        self.result_box.configure(state="disabled")

    def exportar_csv(self):
        if not self.cards:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        exportar_cards_csv(self.cards, file_path)
        log_ui(self.result_box, f"Exportado para {file_path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
