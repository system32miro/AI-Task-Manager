import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self):
        # Garantir que a pasta data existe
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Usar caminho absoluto para a base de dados
        db_path = os.path.abspath(os.path.join('data', 'tasks.db'))
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Cria as tabelas se não existirem"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                prioridade TEXT,
                estado TEXT,
                data_criacao TEXT,
                data_vencimento TEXT,
                data_conclusao TEXT,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def add_task(self, titulo, descricao, categoria, prioridade, data_vencimento, parent_id=None):
        """Adiciona uma nova tarefa"""
        data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO tasks (titulo, descricao, categoria, prioridade, estado, 
                             data_criacao, data_vencimento, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, categoria, prioridade, 'pendente', 
              data_criacao, data_vencimento, parent_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_tasks(self):
        """Retorna todas as tarefas"""
        self.cursor.execute('SELECT * FROM tasks')
        return self.cursor.fetchall()

    def update_task(self, task_id, **kwargs):
        """Atualiza uma tarefa existente"""
        valid_fields = ['titulo', 'descricao', 'categoria', 'prioridade', 
                       'estado', 'data_vencimento', 'data_conclusao']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in valid_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False

        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
        return True

    def delete_task(self, task_id):
        """Elimina uma tarefa"""
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_tasks_by_filter(self, **filters):
        """Retorna tarefas com base em filtros"""
        query = 'SELECT * FROM tasks WHERE 1=1'
        values = []
        
        for key, value in filters.items():
            if value is not None:
                query += f" AND {key} = ?"
                values.append(value)
        
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def get_subtasks(self, parent_id):
        """Retorna todas as subtarefas de uma tarefa"""
        self.cursor.execute('SELECT * FROM tasks WHERE parent_id = ?', (parent_id,))
        return self.cursor.fetchall()

    def has_subtasks(self, task_id):
        """Verifica se uma tarefa tem subtarefas"""
        self.cursor.execute('SELECT COUNT(*) FROM tasks WHERE parent_id = ?', (task_id,))
        return self.cursor.fetchone()[0] > 0

    def __del__(self):
        """Fecha a conexão com a base de dados"""
        self.conn.close() 