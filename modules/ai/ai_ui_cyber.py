import customtkinter as ctk
import threading
import os

class AiChatFrame(ctk.CTkFrame):
    def __init__(self, master, ai_assistant, **kwargs):
        super().__init__(master, **kwargs)
        self.ai_assistant = ai_assistant

        # --- Cyber Tokens ---
        self.font_term = ("Consolas", 14)
        self.font_head = ("Consolas", 18, "bold")
        self.bg_color = "black"
        self.text_sys = "#00FF41" # Neon Green
        self.text_usr = "#00FFFF" # Neon Cyan
        self.text_err = "#FF00FF" # Neon Pink
        
        self.configure(fg_color=self.bg_color)
        
        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- QUERY BAR (Moved to top for terminal feel?) No, keep standard layout but styled ---
        
        # HEADER (System Status Bar)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.header_frame, text="> AI_UPLINK_ESTABLISHED", 
                     font=self.font_head, text_color=self.text_sys).pack(side="left")

        # Refrescar (RELOAD_INDEX)
        self.refresh_btn = ctk.CTkButton(self.header_frame, text="[ RE-INDEX ]", width=100,
                                         font=self.font_term,
                                         fg_color="transparent", border_width=1, border_color=self.text_sys,
                                         text_color=self.text_sys, hover_color="#002200", corner_radius=0,
                                         command=self.refresh_knowledge_base)
        self.refresh_btn.pack(side="right")
        
        # Help (?)
        self.help_btn = ctk.CTkButton(self.header_frame, text="[ ? ]", width=40,
                                      font=self.font_term,
                                      fg_color="transparent", text_color="gray50", hover_color="#111", corner_radius=0,
                                      command=self.show_help_guide)
        self.help_btn.pack(side="right", padx=10)

        # MODEL SELECTOR (Digital Dropdown)
        self.model_var = ctk.StringVar(value="phi3")
        self.model_selector = ctk.CTkOptionMenu(
            self.header_frame,
            values=[
                "phi3", 
                "tinyllama", 
                "gemini-2.5-flash", 
                "gemini-2.0-flash",
                "gemini-2.5-pro"
            ], 
            width=180,
            variable=self.model_var,
            font=self.font_term,
            fg_color="black",         # Button bg
            button_color="#111",      # Arrow bg
            button_hover_color="#222",
            text_color=self.text_sys,
            dropdown_fg_color="black",
            dropdown_text_color=self.text_sys,
            dropdown_hover_color="#002200",
            corner_radius=0,
            command=self.change_model_event
        )
        self.model_selector.pack(side="right", padx=(10, 10))
        # Bezel for the dropdown
        # ctk optionmenu border support is limited in some versions, but we leave it clean black

        # --- TERMINAL OUTPUT (Chat History) ---
        self.chat_display = ctk.CTkTextbox(self, state="disabled", wrap="word", 
                                           font=self.font_term, fg_color="#050505", 
                                           text_color="white", corner_radius=0, border_color=self.text_sys, border_width=1)
        self.chat_display.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # --- INPUT LINE ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # Prompt Symbol
        ctk.CTkLabel(self.input_frame, text=">_", font=self.font_head, text_color=self.text_sys).grid(row=0, column=0, padx=(0, 5))

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="ENTER_COMMAND...", 
                                  font=self.font_term, border_width=0, corner_radius=0,
                                  fg_color="transparent", text_color=self.text_sys, 
                                  placeholder_text_color="gray30")
        
        # To simulate a bottom border, we might place a separator below, or just rely on the blinking cursor
        # Let's add a visual underline using a frame below if needed, but 'clean' is better.
        self.entry.grid(row=0, column=1, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.send_message())

        # Send Button [EXEC]
        self.send_btn = ctk.CTkButton(self.input_frame, text="[ EXEC ]", width=80,
                                      font=self.font_term,
                                      fg_color=self.text_sys, text_color="black", hover_color="#00CC33", corner_radius=0,
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=2, padx=(10, 0))

        # Initial Log
        self.log_event("SYSTEM", "Initialization Complete. Gemini-2.5-flash ready.", color=self.text_sys)

    def log_event(self, sender, message, color=None):
        """Custom logger for the chat display."""
        if not color:
            color = "white"
            
        self.chat_display.configure(state="normal")
        
        # Timestamp could be cool but cleaner without for now
        # Format: > SENDER: Message
        
        tag = f"tag_{sender}"
        self.chat_display.tag_config(tag, foreground=color)
        
        self.chat_display.insert("end", f"> {sender}: ", tag)
        self.chat_display.insert("end", f"{message}\n\n", "text_default")
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    # --- Feature Logic (Mirroring Original) ---

    def show_help_guide(self):
        help_text = (
            "// MANUAL_OVERRIDE //\n"
            "1. ACCESS TO: Tasks & Notes database.\n"
            "2. INDEXING: Required for new data ingestion.\n"
            "3. PROTOCOLS:\n"
            "   - Phi3/TinyLlama: OFFLINE MODE.\n"
            "   - Gemini 2.5: CLOUD UPLINK ACTIVE.\n"
        )
        self.log_event("HELP", help_text, color="gray70")

    def change_model_event(self, new_model):
        api_key = None
        if "gemini" in new_model:
            if not os.environ.get("GOOGLE_API_KEY"):
                # Style the dialog? Hard to style standard dialogs.
                dialog = ctk.CTkInputDialog(text="> AUTHENTICATION REQUIRED:\nENTER API KEY:", title="SECURITY PROTOCOL")
                api_key = dialog.get_input()
                if not api_key:
                    self.model_var.set("phi3") 
                    self.log_event("SYS", "Auth aborted. Reverting to Phi3.", color=self.text_err)
                    return

        self.log_event("SYS", f"Rerouting neural pathways to {new_model}...", color=self.text_sys)
        
        def _switch():
            success = self.ai_assistant.set_model(new_model, api_key=api_key)
            if success:
                self.after(0, lambda: self.log_event("SYS", f"Connection established: {new_model}", color=self.text_sys))
            else:
                self.after(0, lambda: self.log_event("ERR", f"Connection failed: {new_model}", color=self.text_err))
        
        threading.Thread(target=_switch, daemon=True).start()

    def refresh_knowledge_base(self):
        self.log_event("SYS", "Scanning local directories...", color=self.text_sys)
        def _run():
            result = self.ai_assistant.build_vector_store()
            self.after(0, lambda: self.log_event("SYS", result, color=self.text_sys))
        threading.Thread(target=_run, daemon=True).start()

    def send_message(self):
        msg = self.entry.get()
        if not msg: return
        self.entry.delete(0, "end")
        
        self.log_event("USER_01", msg, color=self.text_usr)
        self.send_btn.configure(state="disabled")
        
        def _think():
            response = self.ai_assistant.ask_question(msg)
            self.after(0, lambda: self.log_event("AI_CORE", response, color=self.text_sys))
            self.after(0, lambda: self.send_btn.configure(state="normal"))
        threading.Thread(target=_think, daemon=True).start()
