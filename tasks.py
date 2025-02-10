from datetime import datetime
import json
import csv
import os
from database import Database

class TaskManager:
    def __init__(self):
        self.db = Database()

    def __del__(self):
        """Destrutor para garantir que a conexão é fechada"""
        if hasattr(self, 'db'):
            self.db.conn.close()

    def fechar_conexao(self):
        """Fecha a conexão com a base de dados"""
        if hasattr(self, 'db'):
            self.db.conn.close()

    def criar_tarefa(self, titulo, descricao, categoria, prioridade, data_vencimento, parent_id=None):
        """Cria uma nova tarefa"""
        return self.db.add_task(titulo, descricao, categoria, prioridade, data_vencimento, parent_id)

    def obter_todas_tarefas(self, incluir_subtarefas=True):
        """Retorna todas as tarefas"""
        tarefas = self.db.get_all_tasks()
        if not incluir_subtarefas:
            # Retornar apenas tarefas principais (sem parent_id)
            try:
                return [t for t in tarefas if len(t) > 9 and t[9] is None]
            except IndexError:
                # Se houver erro de índice, significa que a estrutura antiga ainda está em uso
                return tarefas
        return tarefas

    def atualizar_tarefa(self, task_id, **kwargs):
        """Atualiza uma tarefa existente"""
        if 'estado' in kwargs and kwargs['estado'] == 'concluída':
            kwargs['data_conclusao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.db.update_task(task_id, **kwargs)

    def eliminar_tarefa(self, task_id):
        """Elimina uma tarefa"""
        return self.db.delete_task(task_id)

    def filtrar_tarefas(self, **filtros):
        """Filtra tarefas com base em critérios específicos"""
        return self.db.get_tasks_by_filter(**filtros)

    def exportar_para_json(self, filename, pasta_personalizada=False):
        """Exporta todas as tarefas para um arquivo JSON"""
        try:
            tarefas = self.obter_todas_tarefas()
            dados = []
            for tarefa in tarefas:
                dados.append({
                    'id': tarefa[0],
                    'titulo': tarefa[1],
                    'descricao': tarefa[2],
                    'categoria': tarefa[3],
                    'prioridade': tarefa[4],
                    'estado': tarefa[5],
                    'data_criacao': tarefa[6],
                    'data_vencimento': tarefa[7],
                    'data_conclusao': tarefa[8]
                })
            
            if not pasta_personalizada:
                # Comportamento original - salvar na pasta data
                if not os.path.exists('data'):
                    os.makedirs('data')
                caminho_arquivo = f'data/{filename}.json'
            else:
                # Usar o caminho completo fornecido
                caminho_arquivo = filename
                
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao exportar JSON: {str(e)}")
            raise

    def exportar_para_csv(self, filename, pasta_personalizada=False):
        """Exporta todas as tarefas para um arquivo CSV"""
        try:
            tarefas = self.obter_todas_tarefas()
            headers = ['ID', 'Título', 'Descrição', 'Categoria', 'Prioridade', 
                      'Estado', 'Data Criação', 'Data Vencimento', 'Data Conclusão']
            
            if not pasta_personalizada:
                # Comportamento original - salvar na pasta data
                if not os.path.exists('data'):
                    os.makedirs('data')
                caminho_arquivo = f'data/{filename}.csv'
            else:
                # Usar o caminho completo fornecido
                caminho_arquivo = filename
            
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for tarefa in tarefas:
                    writer.writerow([
                        tarefa[0],  # ID
                        tarefa[1],  # Título
                        tarefa[2],  # Descrição
                        tarefa[3],  # Categoria
                        tarefa[4],  # Prioridade
                        tarefa[5],  # Estado
                        tarefa[6],  # Data Criação
                        tarefa[7],  # Data Vencimento
                        tarefa[8]   # Data Conclusão
                    ])
            return True
        except Exception as e:
            print(f"Erro ao exportar CSV: {str(e)}")
            raise

    def importar_de_json(self, filename, pasta_personalizada=False):
        """Importa tarefas de um arquivo JSON"""
        try:
            if not pasta_personalizada:
                filename = f'data/{filename}.json'
                
            with open(filename, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                for tarefa in dados:
                    # Verifica se a tarefa já existe pelo ID
                    tarefas_existentes = self.db.get_tasks_by_filter(id=tarefa['id'])
                    if not tarefas_existentes:
                        self.criar_tarefa(
                            titulo=tarefa['titulo'],
                            descricao=tarefa.get('descricao', ''),
                            categoria=tarefa.get('categoria', ''),
                            prioridade=tarefa.get('prioridade', 'Média'),
                            data_vencimento=tarefa.get('data_vencimento', ''),
                            parent_id=tarefa.get('parent_id')
                        )
            return True
        except FileNotFoundError:
            print("Arquivo JSON não encontrado")
            raise
        except Exception as e:
            print(f"Erro ao importar JSON: {str(e)}")
            raise

    def importar_de_csv(self, filename, pasta_personalizada=False):
        """Importa tarefas de um arquivo CSV"""
        try:
            if not pasta_personalizada:
                filename = f'data/{filename}.csv'
                
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Verifica se a tarefa já existe pelo ID
                    tarefas_existentes = self.db.get_tasks_by_filter(id=row['ID'])
                    if not tarefas_existentes:
                        self.criar_tarefa(
                            titulo=row['Título'],
                            descricao=row['Descrição'],
                            categoria=row['Categoria'],
                            prioridade=row['Prioridade'],
                            data_vencimento=row['Data Vencimento'],
                            parent_id=row.get('Parent ID')
                        )
            return True
        except FileNotFoundError:
            print("Arquivo CSV não encontrado")
            raise
        except Exception as e:
            print(f"Erro ao importar CSV: {str(e)}")
            raise

    def obter_subtarefas(self, task_id):
        """Retorna todas as subtarefas de uma tarefa"""
        return self.db.get_subtasks(task_id)

    def tem_subtarefas(self, task_id):
        """Verifica se uma tarefa tem subtarefas"""
        return self.db.has_subtasks(task_id) 