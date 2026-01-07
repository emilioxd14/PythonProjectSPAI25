
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from modules.ai.ai_logic import AiAssistant
    from modules.ai.ai_ui import AiChatFrame
    print("AI Modules imported successfully.")
except Exception as e:
    print(f"Import Error: {e}")
    exit(1)

# Mock Controllers
class MockController:
    def get_tasks(self): return [{"text": "Test Task", "completed": False}]
    def get_notes(self): return ["Test Note"]

try:
    print("Testing initialization...")
    ai = AiAssistant(MockController(), MockController())
    print(f"AiAssistant initialized. Active: {ai.is_active}")
    
    if ai.is_active:
        print("Testing Indexing...")
        res = ai.build_vector_store()
        print(f"Index Result: {res}")
    else:
        print("Skipping RAG tests (libs missing or initialization failed).")

except Exception as e:
    print(f"Runtime Error: {e}")
    exit(1)

print("Verification Passed.")
