import ttkbootstrap as ttk
from gui import TaskManagerGUI

def main():
    root = ttk.Window(
        title="Gestor de Tarefas",
        themename="darkly",
        resizable=(True, True)
    )
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 