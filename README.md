# 🚀 Productivity Dashboard (To-Do, Notes, Calendar & AI)

A modular desktop application built with Python and CustomTkinter. This project integrates a robust Task Manager, a creative Sticky Note board, a functional Calendar, and an AI Assistant into a single "Productivity Dashboard" using a unified storage engine.

**Project Type:** Paired Programming / Learning by Doing  
**Target:** Desktop (Windows/macOS)

---

## 🌟 Key Features

### 1. Unified Dashboard
* **Sidebar Navigation:** Seamless toggling between To-Do, Sticky Notes, Calendar, and AI views.
* **Modern UI:** Built with `customtkinter` for high-DPI support and a clean, system-adaptive look.
* **Themes:** Supports **Standard**, **Zen**, and **Cyberpunk** visual themes to match your workflow mood.

### 2. To-Do Module
* **Task Management:** Add tasks via keyboard (Enter) or button.
* **History Tracking:** Completed tasks move to a "Completed" history section.
* **Bulk Clear:** "Clear History" button to permanently wipe finished tasks.

### 3. Sticky Notes Module
* **Corkboard Layout:** Notes are arranged in a responsive grid.
* **Dynamic UI:** Fixed aspect ratio notes mimicking real post-its.

### 4. Calendar Module
* **Month View:** Visual overview of dates.
* **Task Integration:** View tasks directly on their due dates.

### 5. AI Assistant Module
* **Integrated Chat:** Chat interface to get help or brainstorm ideas directly within the app.
* **Context Aware:** Designed to work alongside your productivity tools.

### 6. Professional Data Persistence 💾
* **System Integration:** Saves user data to the system's **`AppData`** folder (Windows) or `Application Support` (Mac).
* **Data Safety:** Portable executable design; data stays centralized and safe.
* **Auto-Load:** Data is automatically loaded upon startup.

---

## 📂 Project Architecture

This project follows a **Modular Architecture** to facilitate scalability and code organization.

```text
/project_root
  ├── main.py                # Entry point
  ├── app_layout.py          # MainLayout (Orchestrator)
  ├── storage.py             # Shared storage engine
  │
  └── /modules
       ├── /todo
       │    ├── todo_ui.py     # View
       │    └── todo_logic.py  # Controller/Logic
       │
       ├── /notes
       │    ├── notes_ui.py    # View
       │    └── notes_logic.py # Controller/Logic
       │
       ├── /calendar
       │    ├── calendar_ui.py    # View
       │    └── calendar_logic.py # Controller/Logic
       │
       └── /ai
            ├── ai_ui.py    # View
            └── ai_logic.py # AI Service Logic
```

## 🛠️ Installation & Usage

1.  **Clone the repository** (if applicable).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python main.py
    ```

---

*Built with ❤️ using Python & CustomTkinter.*
