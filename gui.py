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
        self.geometry("500x600")

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

        self.result_box = ctk.CTkTextbox(self, width=450, height=200)
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
        palavra_jap = self.botoes[idx].cget("text") if idx in self.botoes else "Palavra"
        popup = ctk.CTkToplevel(self)
        popup.title(palavra_jap)
        popup.geometry("420x400")
        popup.transient(self)
        # Frame principal
        frame = ctk.CTkFrame(popup)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        # Canvas e Scrollbar
        canvas = ctk.CTkCanvas(frame, bg="#222", highlightthickness=0, width=400, height=340)
        scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
        scroll_frame = ctk.CTkFrame(canvas, fg_color="#222")
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # Exibe campos do card, exceto 'Palavra', com botão de copiar ao lado e altura ajustada
        for campo in ["Kanji", "Conjugação", "Tradução", "Definição", "Exemplos de uso", "Formalidade"]:
            valor = card.get(campo, "-")
            ctk.CTkLabel(scroll_frame, text=f"{campo}:", font=("Arial", 11, "bold"), anchor="w", text_color="#ffb", fg_color="#222").pack(fill="x", anchor="w")
            linha_frame = ctk.CTkFrame(scroll_frame, fg_color="#222")
            linha_frame.pack(fill="x", anchor="w", pady=(0,5))
            # Calcula altura dinâmica
            num_linhas = valor.count("\n") + max(1, len(valor) // 55)
            altura = min(200, 20 + num_linhas * 18)  # Limite máximo para não ficar gigante
            textbox = ctk.CTkTextbox(linha_frame, width=300, height=altura)
            textbox.insert("1.0", valor)
            textbox.configure(state="disabled")
            textbox.pack(side="left", fill="x", expand=True)
            def copiar_conteudo(txtbox=textbox):
                self.clipboard_clear()
                self.clipboard_append(txtbox.get("1.0", "end").strip())
            btn_copiar = ctk.CTkButton(linha_frame, text="Copiar", width=60, command=copiar_conteudo)
            btn_copiar.pack(side="left", padx=5)
        # Fechar
        btn_fechar = ctk.CTkButton(popup, text="Fechar", command=popup.destroy)
        btn_fechar.pack(pady=10)
        # Scroll mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

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
