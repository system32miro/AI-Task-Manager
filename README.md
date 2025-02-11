# **AI Task Manager**

A modern desktop application in **Python** for **task management**, featuring an **intuitive graphical interface** and an **integrated AI assistant**.

![Task Manager](https://github.com/system32miro/gestor-tarefas-ia/raw/main/Captura%20de%20ecrã%202025-02-10%20110341.png)

---

## 🌟 **Main Features**

### **Task Management**
- ✅ Create, edit, and delete tasks
- 📋 Organize by categories (**Work, Study, Personal**)
- ⭐ Set priorities (**High, Medium, Low**)
- 🔄 Manage task statuses (**Pending, In Progress, Completed**)
- 📅 Set due dates with **integrated calendar**
- 🌳 Support for **subtasks** (task hierarchy)

### **Modern Interface**
- 🎨 Customizable themes (**darkly, cosmo, flatly, etc.**)
- 🔍 **Advanced search and filtering**
- 📊 **Detailed statistics**
- 📱 **Responsive and adaptive interface**
- 🖱️ **Context menu and keyboard shortcuts**

### **AI Assistant**
- 🤖 **Automatic task analysis**
- 💡 **Smart categorization suggestions**
- 📈 **Priority recommendations**
- 🔄 **Analysis of existing tasks**
- 💬 **Interactive chat

 for assistance and suggestions**

### **Import/Export**
- 📤 **Export tasks** to **JSON/CSV**
- 📥 **Import tasks** from **JSON/CSV**
- 💾 **Automatic backup**
- 📁 **Custom directory selection**

### **Storage**
- 🗄️ **SQLite database**
- 🔒 **Automatic persistence**
- 🔄 **Real-time synchronization**

---

## 🚀 **Installation**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/system32miro/gestor-tarefas-ia.git
   ```

2. **Navigate to the project folder:**
   ```bash
   cd gestor-tarefas-ia
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the AI API:**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

---

## 🎯 **Usage**

1. **Run the program:**
   ```bash
   python main.py
   ```

2. **Main Interface:**
   - **Left Panel:** Form to add new tasks and task list.
   - **Right Panel:** Interactive AI assistant.
   - **Bottom Buttons:** Quick actions and import/export options.

3. **Keyboard Shortcuts:**
   - `Ctrl+N`: New task
   - `Ctrl+D`: Delete selected task
   - `Ctrl+F`: Focus search
   - `F5`: Refresh task list

4. **AI Assistant:**
   - Use the chat for suggestions.
   - Available commands:
     - `/create_task [title]`
     - `/list_tasks`
     - `/help`

---

## **Project Structure**

```
gestor_tarefas/
│── main.py              # Entry point
│── gui.py               # Graphical interface
│── tasks.py             # Task management
│── database.py          # Database handling
│── ai_helper.py         # AI integration
│── requirements.txt     # Dependencies
│── README.md            # Documentation
│── .env                 # API configurations
│── data/                # Data and backups
    │── tasks.db         # SQLite database
    │── *.json           # JSON exports
    │── *.csv            # CSV exports
```

---

## 🤝 **Contributing**

Contributions are welcome! Please follow these steps:

1. **Fork the project**.
2. **Create a branch** for your feature (`git checkout -b feature/MyFeature`).
3. **Commit your changes** (`git commit -m 'Add MyFeature'`).
4. **Push to the branch** (`git push origin feature/MyFeature`).
5. **Open a Pull Request**.

---

## 📝 **License**

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 📫 **Support**

For support or questions:
1. **Open an [issue](https://github.com/system32miro/gestor-tarefas-ia/issues)**
2. **Check the [documentation](https://github.com/system32miro/gestor-tarefas-ia/wiki)**
3. **Contact the maintainers**

---

## ⭐ **Show Your Support**

If this project helped you, please **give it a star!** ⭐
