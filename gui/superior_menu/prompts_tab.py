import customtkinter as ctk
from configs.prompts import PROMPTS

class PromptsTab(ctk.CTkFrame):
    def __init__(self, master, prompt_entries):
        super().__init__(master, fg_color="#222")
        prompts_frame = ctk.CTkFrame(self)
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
        ctk.CTkLabel(prompts_scrollable, text="Edit Field Prompts", font=("Arial", 14, "bold"), text_color="#fff", fg_color="#222").pack(pady=(10,10))
        for field, value in PROMPTS.items():
            ctk.CTkLabel(prompts_scrollable, text=f"{field}:", font=("Arial", 11, "bold"), anchor="w", text_color="#ffb", fg_color="#222").pack(fill="x", anchor="w")
            lines = value.count("\n") + 1
            max_line_length = max([len(l) for l in value.splitlines()] or [0])
            extra_lines = max_line_length // 55
            total_lines = min(15, lines + extra_lines)
            height = 22 * total_lines
            entry = ctk.CTkTextbox(prompts_scrollable, width=540, height=height)
            entry.insert("1.0", value)
            entry.pack(fill="x", anchor="w", pady=(0,10))
            prompt_entries[field] = entry
        def _on_mousewheel_prompts(event):
            prompts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        prompts_canvas.bind("<MouseWheel>", _on_mousewheel_prompts)
        prompts_canvas.bind("<Button-4>", lambda event: prompts_canvas.yview_scroll(-1, "units"))
        prompts_canvas.bind("<Button-5>", lambda event: prompts_canvas.yview_scroll(1, "units"))
