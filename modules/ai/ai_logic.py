import sys
import os

try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_core.documents import Document
    from langchain_community.llms import Ollama
    
    # --- IMPORTACIÓN DE GEMINI ---
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    _LIBS_AVAILABLE = True
except ImportError as e:
    _LIBS_AVAILABLE = False
    print(f"AI Warning: Libraries missing ({e}). AI features disabled.")

class AiAssistant:
    def __init__(self, todo_controller, notes_controller):
        self.todo_controller = todo_controller
        self.notes_controller = notes_controller
        self.vector_store = None
        self.llm = None
        self.is_active = _LIBS_AVAILABLE
        self.api_key = None
        
        # Modelo por defecto
        self.current_model = "phi3" 

        if self.is_active:
            try:
                # El traductor de texto (siempre local y rápido)
                self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
                self.set_model(self.current_model)
            except Exception as e:
                print(f"AI Warning: Failed to init AI: {e}")
                self.is_active = False

    def set_model(self, model_name, api_key=None):
        """Cambia el cerebro. Soporta Ollama (local) y Gemini (nube)."""
        if not self.is_active:
            return False

        try:
            # --- CAMBIO IMPORTANTE AQUÍ: Detectamos cualquier modelo de Gemini ---
            if "gemini" in model_name:
                # Configuración para Google Gemini
                if api_key:
                    self.api_key = api_key
                    os.environ["GOOGLE_API_KEY"] = api_key
                
                if not os.environ.get("GOOGLE_API_KEY"):
                    print("Error: No Google API Key provided.")
                    return False

                # Usamos el nombre exacto que llega del UI (ej: gemini-1.5-flash)
                self.llm = ChatGoogleGenerativeAI(model=model_name, convert_system_message_to_human=True)
                print(f"Conectado a Google {model_name}")

            else:
                # Configuración para Modelos Locales (Ollama)
                self.llm = Ollama(model=model_name)
                print(f"Conectado a Ollama local: {model_name}")

            self.current_model = model_name
            return True

        except Exception as e:
            print(f"Error changing model: {e}")
            return False

    def build_vector_store(self):
        if not self.is_active:
            return "AI unavailable."

        try:
            documents = []
            
            # 1. Indexar Tareas
            tasks = self.todo_controller.get_tasks()
            for t in tasks:
                status = "Completed" if t.get('completed') else "Pending"
                prio = t.get('priority', 'Medium')
                content = f"Task: {t['text']} | Status: {status} | Priority: {prio}"
                documents.append(Document(page_content=content, metadata={"source": "todo"}))

            # 2. Indexar Notas
            notes = self.notes_controller.get_notes()
            for n in notes:
                text = n if isinstance(n, str) else n.get('text', '')
                if text:
                    documents.append(Document(page_content=f"Note: {text}", metadata={"source": "notes"}))

            if not documents:
                return "No data to index."

            self.vector_store = Chroma.from_documents(
                documents, 
                self.embeddings,
                collection_name="my_local_knowledge"
            )
            return f"Indexed {len(documents)} items successfully."
            
        except Exception as e:
            return f"Error building index: {e}"

    def ask_question(self, query):
        if not self.is_active:
            return "Error: AI libraries missing."
        
        if not self.vector_store:
            res = self.build_vector_store()
            if "Error" in res:
                return res

        try:
            # 1. Recuperar contexto
            docs = self.vector_store.similarity_search(query, k=3)
            context_text = "\n\n".join([d.page_content for d in docs]) or "No relevant data found."

            # 2. Generar Respuesta
            if "gemini" in self.current_model:
                # Prompt natural para Gemini
                prompt = (
                    f"You are a smart personal assistant. Use the context below to answer the user's question.\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {query}"
                )
                response = self.llm.invoke(prompt)
                return response.content

            else:
                # Prompt estricto para modelos locales
                prompt = (
                    f"### Instruction:\nUse ONLY the context below to answer.\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {query}\n\n"
                    f"### Response:"
                )
                return self.llm.invoke(prompt)
            
        except Exception as e:
            return f"AI Error: {e}"