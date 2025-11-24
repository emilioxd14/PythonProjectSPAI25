# 🚀 Productivity Dashboard (To-Do & Sticky Notes)

A modular desktop application built with Python and CustomTkinter. This project integrates a robust Task Manager and a creative Sticky Note board into a single "Productivity Dashboard" using a unified storage engine.

**Project Type:** Paired Programming / Learning by Doing  
**Target:** Desktop (Windows/macOS)

---

## 🌟 Key Features

### 1. Unified Dashboard
* **Sidebar Navigation:** seamless toggling between the To-Do view and Sticky Notes view without opening multiple windows.
* **Modern UI:** Built with `customtkinter` for high-DPI support and a clean, system-adaptive look.

### 2. To-Do Module
* **Task Management:** Add tasks via keyboard (Enter) or button.
* **History Tracking:** Completed tasks are not deleted immediately; they move to a "Completed" history section for review.
* **Bulk Clear:** "Clear History" button to permanently wipe finished tasks.

### 3. Sticky Notes Module
* **Corkboard Layout:** Notes are arranged in a responsive 3-column grid.
* **Dynamic UI:** Notes maintain a fixed square aspect ratio to mimic real post-it notes.

### 4. Professional Data Persistence 💾
* **System Integration:** Unlike basic scripts that save files in the code folder, this app saves user data to the system's **`AppData`** folder (Windows) or `Application Support` (Mac).
* **Data Safety:** Users can move the `.exe` anywhere (Desktop, USB stick), and their data remains safe and centralized.
* **Auto-Load:** Data is automatically loaded upon application startup.

---

## 📂 Project Architecture

This project follows a **Modular Architecture** to facilitate teamwork and avoid code conflicts.

```text
/project_root
  ├── main.py                # Entry point (Simple)
  ├── layout_manager.py      # MainLayout (Orchestrator)
  ├── storage.py             # Shared storage engine
  │
  └── /modules
       ├── /todo
       │    ├── todo_ui.py     # View
       │    └── todo_logic.py  # Model & Controller combined
       │
       └── /notes
            ├── notes_ui.py    # View
            └── notes_logic.py # Model & Controller combined
