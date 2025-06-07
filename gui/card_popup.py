import customtkinter as ctk

class CardPopup(ctk.CTkToplevel):
    def __init__(self, master, card, palavra_jap, campos, clipboard_func):
        super().__init__(master)
        self.title(palavra_jap)
        self.geometry("420x400")
        self.transient(master)
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
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
        for campo in campos:
            valor = card.get(campo, "-")
            ctk.CTkLabel(scroll_frame, text=f"{campo}:", font=("Arial", 11, "bold"), anchor="w", text_color="#ffb", fg_color="#222").pack(fill="x", anchor="w")
            linha_frame = ctk.CTkFrame(scroll_frame, fg_color="#222")
            linha_frame.pack(fill="x", anchor="w", pady=(0,5))
            # Ajuste dinâmico de altura do textbox
            lines = valor.count("\n") + 1
            max_line_length = max([len(l) for l in valor.splitlines()] or [0])
            extra_lines = max_line_length // 55
            total_lines = min(15, lines + extra_lines)
            altura = 22 * total_lines
            textbox = ctk.CTkTextbox(linha_frame, width=300, height=altura)
            textbox.insert("1.0", valor)
            textbox.configure(state="disabled")
            textbox.pack(side="left", fill="x", expand=True)
            def copiar_conteudo(txtbox=textbox):
                clipboard_func(txtbox.get("1.0", "end").strip())
            btn_copiar = ctk.CTkButton(linha_frame, text="Copiar", width=60, command=copiar_conteudo)
            btn_copiar.pack(side="left", padx=5)
        btn_fechar = ctk.CTkButton(self, text="Fechar", command=self.destroy)
        btn_fechar.pack(pady=10)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))

        # Fechar ao clicar fora do popup
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_force()
