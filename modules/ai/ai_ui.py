import customtkinter as ctk
import threading
import os

class AiChatFrame(ctk.CTkFrame):
    def __init__(self, master, ai_assistant, **kwargs):
        super().__init__(master, **kwargs)
        self.ai_assistant = ai_assistant

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="AI Assistant", 
                                        font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        # Botón de Ayuda
        self.help_btn = ctk.CTkButton(self.header_frame, text="?", width=30, height=30,
                                      fg_color="gray", hover_color="#555",
                                      command=self.show_help_guide)
        self.help_btn.pack(side="left", padx=(10, 0))

        # Botón Refrescar
        self.refresh_btn = ctk.CTkButton(self.header_frame, text="⟳ Index", width=80,
                                         command=self.refresh_knowledge_base)
        self.refresh_btn.pack(side="right")

        # --- ACTUALIZACIÓN DE MODELOS (Basada en tu script) ---
        self.model_var = ctk.StringVar(value="phi3")
        self.model_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=[
                "phi3", 
                "tinyllama", 
                "gemini-2.5-flash",    # <--- La joya de la corona
                "gemini-2.0-flash",    # <--- Opción estable
                "gemini-2.5-pro"       # <--- El más inteligente
            ], 
            width=160,
            variable=self.model_var,
            command=self.change_model_event
        )
        self.model_selector.pack(side="right", padx=(10, 10))
        # -----------------------------------------------------

        # Chat History
        self.chat_display = ctk.CTkTextbox(self, state="disabled", wrap="word", font=("Roboto", 14))
        self.chat_display.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask about your tasks or notes...")
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=80, command=self.send_message)
        self.send_btn.grid(row=0, column=1)

        self._append_message("System", "Welcome! Select 'gemini-2.5-flash' to start.")

    def show_help_guide(self):
        help_text = (
            "🤖 **GUÍA RÁPIDA DE IA**\n\n"
            "1. **Tus Datos:** Puedo leer tus Tareas y Notas.\n"
            "2. **Botón 'Index':** Úsalo al crear tareas nuevas.\n"
            "3. **Modelos:**\n"
            "   - **Phi3 / TinyLlama:** Uso local (Offline).\n"
            "   - **Gemini 2.5 Flash:** ¡Ultra rápido y conectado a Google!\n"
        )
        self._append_message("Help", help_text)

    def change_model_event(self, new_model):
        """Detecta cualquier modelo de Gemini y pide la clave."""
        api_key = None
        
        # Lógica flexible: detecta "gemini" en cualquier parte del nombre
        if "gemini" in new_model:
            if not os.environ.get("GOOGLE_API_KEY"):
                dialog = ctk.CTkInputDialog(text="Enter your Google Gemini API Key:", title="Gemini Setup")
                api_key = dialog.get_input()
                if not api_key:
                    self.model_var.set("phi3") 
                    self._append_message("System", "Gemini selection cancelled.")
                    return

        self._append_message("System", f"Switching brain to {new_model}...")
        
        def _switch():
            success = self.ai_assistant.set_model(new_model, api_key=api_key)
            if success:
                self.after(0, lambda: self._append_message("System", f"Success! Now using {new_model}."))
            else:
                self.after(0, lambda: self._append_message("System", f"Error: Could not load {new_model}."))
        
        threading.Thread(target=_switch, daemon=True).start()

    def refresh_knowledge_base(self):
        self._append_message("System", "Re-indexing data... please wait.")
        def _run():
            result = self.ai_assistant.build_vector_store()
            self.after(0, lambda: self._append_message("System", result))
        threading.Thread(target=_run, daemon=True).start()

    def send_message(self):
        msg = self.entry.get()
        if not msg: return
        self.entry.delete(0, "end")
        self._append_message("You", msg)
        self.send_btn.configure(state="disabled")
        
        def _think():
            response = self.ai_assistant.ask_question(msg)
            self.after(0, lambda: self._append_message("AI", response))
            self.after(0, lambda: self.send_btn.configure(state="normal"))
        threading.Thread(target=_think, daemon=True).start()

    def _append_message(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n[{sender}]: {text}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")