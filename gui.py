import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import DatePickerDialog, Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from tasks import TaskManager
from ai_helper import AITaskAnalyzer
import os
from tkinter import filedialog

class CalendarDialog(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Selecionar Data")
        
        # Configurar janela
        self.transient(parent)
        self.grab_set()
        
        # Centralizar a janela
        window_width = 300
        window_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Criar o calendário
        self.calendar = DateEntry(
            self,
            firstweekday=0,  # Segunda-feira como primeiro dia
            bootstyle="primary"
        )
        self.calendar.pack(pady=20, padx=20)
        
        # Botões
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="Confirmar",
            command=self._confirmar,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            bootstyle="danger"
        ).pack(side=LEFT, padx=5)
        
        self.selected_date = None
        
    def _confirmar(self):
        self.selected_date = self.calendar.entry.get()
        self.destroy()

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tarefas")
        
        # Configurar handler para fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Configurar janela em tela cheia
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.state('zoomed')  # Maximizar janela
        
        # Configurar tema
        self.style = ttk.Style()
        self.style.theme_use('darkly')
        
        # Criar pasta data se não existir
        if not os.path.exists('data'):
            os.makedirs('data')

        self.task_manager = TaskManager()
        
        # Inicializar o analisador de IA
        self.ai_analyzer = AITaskAnalyzer()
        
        # Variáveis
        self.var_titulo = ttk.StringVar()
        self.var_descricao = ttk.StringVar()
        self.var_categoria = ttk.StringVar()
        self.var_prioridade = ttk.StringVar()
        self.var_data_vencimento = ttk.StringVar()
        
        # Variável para controle de ordenação
        self.ordem_atual = {
            'coluna': 'ID',
            'reverso': False
        }
        
        # Configurar atalhos de teclado
        self.root.bind('<Control-n>', lambda e: self._adicionar_tarefa())  # Ctrl+N: Nova tarefa
        self.root.bind('<Control-d>', lambda e: self._eliminar_tarefa())   # Ctrl+D: Eliminar tarefa
        self.root.bind('<Control-f>', lambda e: self._focar_pesquisa())    # Ctrl+F: Focar pesquisa
        self.root.bind('<F5>', lambda e: self._atualizar_lista_tarefas())  # F5: Atualizar lista
        
        # Criar menu superior
        self.menu_bar = ttk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Menu de Opções
        self.opcoes_menu = ttk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Opções", menu=self.opcoes_menu)
        
        # Submenu de Temas
        self.tema_menu = ttk.Menu(self.opcoes_menu, tearoff=0)
        self.opcoes_menu.add_cascade(label="Temas", menu=self.tema_menu)
        for tema in ['darkly', 'cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone']:
            self.tema_menu.add_command(label=tema.capitalize(), command=lambda t=tema: self._mudar_tema(t))
        
        self.opcoes_menu.add_command(label="Estatísticas", command=self._mostrar_estatisticas)
        self.opcoes_menu.add_separator()
        self.opcoes_menu.add_command(label="Backup", command=self._fazer_backup)
        
        self._criar_widgets()
        self._atualizar_lista_tarefas()

    def _get_center_position(self):
        """Calcula a posição central da tela"""
        x = self.root.winfo_x() + (self.root.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2)
        return (x, y)

    def _selecionar_data(self):
        """Abre o seletor de data"""
        try:
            dialog = CalendarDialog(self.root)
            self.root.wait_window(dialog)
            
            if dialog.selected_date:
                self.var_data_vencimento.set(dialog.selected_date)
                
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao abrir calendário: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _focar_pesquisa(self, event=None):
        """Foca no campo de pesquisa"""
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Entry) and child.winfo_name() == 'pesquisa':
                child.focus_set()
                return

    def _ordenar_coluna(self, coluna):
        """Ordena a lista de tarefas pela coluna clicada"""
        # Inverter a ordem se clicar na mesma coluna
        if self.ordem_atual['coluna'] == coluna:
            self.ordem_atual['reverso'] = not self.ordem_atual['reverso']
        else:
            self.ordem_atual['coluna'] = coluna
            self.ordem_atual['reverso'] = False
        
        # Obter todos os itens da Treeview
        items = [(self.tree.set(item, coluna), item) for item in self.tree.get_children('')]
        
        # Ordenar itens
        items.sort(reverse=self.ordem_atual['reverso'])
        
        # Reordenar a Treeview
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Atualizar cabeçalhos para mostrar a ordem
        for col in self.tree['columns']:
            if col == coluna:
                self.tree.heading(col, text=f"{col} {'↓' if self.ordem_atual['reverso'] else '↑'}")
            else:
                self.tree.heading(col, text=col)

    def _criar_widgets(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título da aplicação
        titulo_app = ttk.Label(
            main_frame, 
            text="Gestor de Tarefas",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-primary"
        )
        titulo_app.pack(pady=10, fill=X)
        
        # Container para formulário e lista
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Container esquerdo (formulário + lista)
        left_container = ttk.Frame(content_frame)
        left_container.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Frame para entrada de dados
        input_frame = ttk.LabelFrame(
            left_container, 
            text="Nova Tarefa",
            padding=15,
            bootstyle="primary"
        )
        input_frame.pack(fill=BOTH, expand=NO, padx=(0, 10))
        
        # Campos de entrada
        ttk.Label(input_frame, text="Título:").pack(fill=X)
        ttk.Entry(
            input_frame,
            textvariable=self.var_titulo,
            width=40,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Descrição:").pack(fill=X)
        ttk.Entry(
            input_frame,
            textvariable=self.var_descricao,
            width=40,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Categoria:").pack(fill=X)
        categorias = ['Trabalho', 'Estudos', 'Pessoal']
        ttk.Combobox(
            input_frame,
            textvariable=self.var_categoria,
            values=categorias,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Prioridade:").pack(fill=X)
        prioridades = ['Alta', 'Média', 'Baixa']
        ttk.Combobox(
            input_frame,
            textvariable=self.var_prioridade,
            values=prioridades,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        # Campo de data com botão de calendário
        data_frame = ttk.Frame(input_frame)
        data_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(data_frame, text="Data Vencimento:").pack(side=LEFT)
        ttk.Entry(
            data_frame,
            textvariable=self.var_data_vencimento,
            bootstyle="primary",
            width=15
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            data_frame,
            text="📅",
            command=self._selecionar_data,
            bootstyle="primary-outline",
            width=3
        ).pack(side=LEFT)
        
        # Botões de ação
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Adicionar Tarefa",
            command=self._adicionar_tarefa,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Limpar Campos",
            command=self._limpar_campos,
            bootstyle="secondary"
        ).pack(side=LEFT)
        
        # Frame para lista de tarefas
        list_frame = ttk.LabelFrame(
            left_container,
            text="Tarefas",
            padding=15,
            bootstyle="primary"
        )
        list_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Frame para pesquisa e filtros
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        # Campo de pesquisa
        ttk.Label(
            search_frame,
            text="Pesquisar:",
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        
        self.var_pesquisa = ttk.StringVar()
        self.var_pesquisa.trace('w', lambda *args: self._filtrar_tarefas())
        ttk.Entry(
            search_frame,
            textvariable=self.var_pesquisa,
            bootstyle="primary",
            width=30
        ).pack(side=LEFT, padx=5)
        
        # Filtros
        ttk.Label(
            search_frame,
            text="Filtrar por:",
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        
        # Filtro de Estado
        self.var_filtro_estado = ttk.StringVar(value="Todos")
        ttk.Combobox(
            search_frame,
            textvariable=self.var_filtro_estado,
            values=["Todos", "Pendente", "Em Progresso", "Concluída"],
            width=15,
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        self.var_filtro_estado.trace('w', lambda *args: self._filtrar_tarefas())
        
        # Filtro de Prioridade
        self.var_filtro_prioridade = ttk.StringVar(value="Todas")
        ttk.Combobox(
            search_frame,
            textvariable=self.var_filtro_prioridade,
            values=["Todas", "Alta", "Média", "Baixa"],
            width=15,
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        self.var_filtro_prioridade.trace('w', lambda *args: self._filtrar_tarefas())
        
        # Treeview com estilo moderno
        self.tree = ttk.Treeview(
            list_frame,
            columns=('ID', 'Título', 'Categoria', 'Prioridade', 'Estado', 'Vencimento'),
            show='headings',
            bootstyle="primary"
        )
        
        # Configurar colunas
        self.tree.heading('ID', text='ID')
        self.tree.heading('Título', text='Título')
        self.tree.heading('Categoria', text='Categoria')
        self.tree.heading('Prioridade', text='Prioridade')
        self.tree.heading('Estado', text='Estado')
        self.tree.heading('Vencimento', text='Vencimento')
        
        self.tree.column('ID', width=50)
        self.tree.column('Título', width=200)
        self.tree.column('Categoria', width=100)
        self.tree.column('Prioridade', width=100)
        self.tree.column('Estado', width=100)
        self.tree.column('Vencimento', width=120)
        
        # Scrollbar para a Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Container direito (chat)
        chat_container = ttk.Frame(content_frame)
        chat_container.pack(side=RIGHT, fill=BOTH, expand=NO, padx=(10, 0))

        # Frame do chat
        chat_frame = ttk.LabelFrame(
            chat_container,
            text="Assistente IA",
            padding=15,
            bootstyle="primary",
            width=400  # Largura fixa para o chat
        )
        chat_frame.pack(fill=BOTH, expand=YES)
        chat_frame.pack_propagate(False)  # Manter largura fixa

        # Área de mensagens do chat
        self.chat_area = ttk.Text(
            chat_frame,
            wrap='word',
            state='disabled',
            width=40,
            height=20,
            font=("Helvetica", 10)
        )
        self.chat_area.pack(fill=BOTH, expand=YES, pady=(0, 10))

        # Scrollbar para a área de chat
        chat_scrollbar = ttk.Scrollbar(self.chat_area, orient=VERTICAL, command=self.chat_area.yview)
        self.chat_area.configure(yscrollcommand=chat_scrollbar.set)
        chat_scrollbar.pack(side=RIGHT, fill=Y)

        # Frame para entrada de mensagem
        message_frame = ttk.Frame(chat_frame)
        message_frame.pack(fill=X, pady=(5, 0))

        # Campo de entrada de mensagem
        self.message_var = ttk.StringVar()
        self.message_entry = ttk.Entry(
            message_frame,
            textvariable=self.message_var,
            bootstyle="primary"
        )
        self.message_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))

        # Botão de enviar
        self.send_button = ttk.Button(
            message_frame,
            text="Enviar",
            command=self._enviar_mensagem,
            bootstyle="primary",
            width=10
        )
        self.send_button.pack(side=RIGHT)

        # Indicador de digitação
        self.typing_label = ttk.Label(
            chat_frame,
            text="",
            font=("Helvetica", 8),
            bootstyle="secondary"
        )
        self.typing_label.pack(fill=X, pady=(5, 0))

        # Binding para Enter no campo de mensagem
        self.message_entry.bind('<Return>', lambda e: self._enviar_mensagem())

        # Mensagem de boas-vindas
        self._adicionar_mensagem_sistema("Olá! Sou o seu assistente de gestão de tarefas. Como posso ajudar?")

        # Frame para botões de estado (novo posicionamento)
        estado_frame = ttk.LabelFrame(
            main_frame,
            text="Ações da Tarefa",
            padding=15,
            bootstyle="primary"
        )
        estado_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))

        # Container para centralizar os botões
        button_container = ttk.Frame(estado_frame)
        button_container.pack(expand=YES, pady=5)
        
        # Ajustar o tamanho dos botões e espaçamento
        btn_width = 25  # Aumentar largura dos botões
        btn_padx = 10   # Aumentar espaçamento horizontal
        
        ttk.Button(
            button_container,
            text="Marcar como Pendente",
            command=lambda: self._mudar_estado('pendente'),
            bootstyle="secondary",
            width=btn_width
        ).pack(side=LEFT, padx=btn_padx)
        
        ttk.Button(
            button_container,
            text="Marcar como Em Progresso",
            command=lambda: self._mudar_estado('em progresso'),
            bootstyle="warning",
            width=btn_width
        ).pack(side=LEFT, padx=btn_padx)
        
        ttk.Button(
            button_container,
            text="Marcar como Concluída",
            command=lambda: self._mudar_estado('concluída'),
            bootstyle="success",
            width=btn_width
        ).pack(side=LEFT, padx=btn_padx)
        
        ttk.Button(
            button_container,
            text="Eliminar Tarefa",
            command=self._eliminar_tarefa,
            bootstyle="danger",
            width=btn_width
        ).pack(side=LEFT, padx=btn_padx)

        # Ajustar o frame de exportação/importação também
        export_frame = ttk.LabelFrame(
            main_frame,
            text="Exportar/Importar",
            padding=15,
            bootstyle="primary"
        )
        export_frame.pack(side=BOTTOM, fill=X, pady=(10, 0))

        # Container para centralizar os botões de exportação
        export_container = ttk.Frame(export_frame)
        export_container.pack(expand=YES, pady=5)
        
        # Ajustar o tamanho dos botões de exportação
        export_btn_width = 20
        export_btn_padx = 10
        
        ttk.Button(
            export_container,
            text="Exportar JSON",
            command=self._exportar_json,
            bootstyle="info-outline",
            width=export_btn_width
        ).pack(side=LEFT, padx=export_btn_padx)
        
        ttk.Button(
            export_container,
            text="Exportar CSV",
            command=self._exportar_csv,
            bootstyle="info-outline",
            width=export_btn_width
        ).pack(side=LEFT, padx=export_btn_padx)
        
        ttk.Button(
            export_container,
            text="Importar JSON",
            command=self._importar_json,
            bootstyle="warning-outline",
            width=export_btn_width
        ).pack(side=LEFT, padx=export_btn_padx)
        
        ttk.Button(
            export_container,
            text="Importar CSV",
            command=self._importar_csv,
            bootstyle="warning-outline",
            width=export_btn_width
        ).pack(side=LEFT, padx=export_btn_padx)

        # Configurar cabeçalhos clicáveis para ordenação
        for col in ('ID', 'Título', 'Categoria', 'Prioridade', 'Estado', 'Vencimento'):
            self.tree.heading(col, text=col, command=lambda c=col: self._ordenar_coluna(c))

    def _adicionar_tarefa(self):
        titulo = self.var_titulo.get()
        if not titulo:
            Messagebox.show_error(
                title="Erro",
                message="O título é obrigatório!",
                parent=self.root,
                position=self._get_center_position()
            )
            return
        
        try:
            # Analisar a tarefa com IA antes de adicionar
            analise = self.ai_analyzer.analisar_tarefa(
                titulo=titulo,
                descricao=self.var_descricao.get(),
                tarefas_existentes=[{
                    'titulo': t[1],
                    'descricao': t[2]
                } for t in self.task_manager.obter_todas_tarefas()]
            )
            
            if analise:
                # Mostrar sugestões ao utilizador
                resposta = self._mostrar_sugestoes_ia(analise)
                if resposta == "Yes":
                    # Usar sugestões da IA
                    self.var_categoria.set(analise['categoria'])
                    self.var_prioridade.set(analise['prioridade'])
                    self.var_data_vencimento.set(analise['data_vencimento'])
            
            # Criar a tarefa
            self.task_manager.criar_tarefa(
                titulo=titulo,
                descricao=self.var_descricao.get(),
                categoria=self.var_categoria.get(),
                prioridade=self.var_prioridade.get(),
                data_vencimento=self.var_data_vencimento.get()
            )
            
            self._limpar_campos()
            self._atualizar_lista_tarefas()
            Messagebox.show_info(
                title="Sucesso",
                message="Tarefa adicionada com sucesso!",
                parent=self.root,
                position=self._get_center_position()
            )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao adicionar tarefa: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _mostrar_sugestoes_ia(self, analise):
        """Mostra uma janela com as sugestões da IA"""
        # Criar janela de diálogo
        dialog = ttk.Toplevel(self.root)
        dialog.title("Sugestões da IA")
        
        # Centralizar a janela
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        dialog.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        mensagem = f"""A IA sugere:

Prioridade: {analise['prioridade']}
Razão: {analise['justificativas']['prioridade']}

Categoria: {analise['categoria']}
Razão: {analise['justificativas']['categoria']}

Data Vencimento: {analise['data_vencimento']}
Razão: {analise['justificativas']['data_vencimento']}
"""
        
        if analise['tarefas_similares']:
            mensagem += "\nTarefas similares encontradas:\n"
            for tarefa in analise['tarefas_similares']:
                mensagem += f"- {tarefa}\n"
        
        # Adicionar texto com scroll
        text_widget = ttk.Text(dialog, wrap='word', width=60, height=15)
        text_widget.insert('1.0', mensagem)
        text_widget.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Frame para botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def aplicar():
            dialog.result = "Yes"
            dialog.destroy()
            
        def cancelar():
            dialog.result = "No"
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Aplicar Sugestões", command=aplicar, bootstyle="success").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=cancelar, bootstyle="secondary").pack(side='left', padx=5)
        
        # Tornar a janela modal
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        return getattr(dialog, 'result', 'No')

    def _limpar_campos(self):
        self.var_titulo.set("")
        self.var_descricao.set("")
        self.var_categoria.set("")
        self.var_prioridade.set("")
        self.var_data_vencimento.set("")

    def _atualizar_lista_tarefas(self):
        """Atualiza a lista de tarefas com indentação para subtarefas"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Primeiro adicionar tarefas principais
        tarefas_principais = self.task_manager.obter_todas_tarefas(incluir_subtarefas=False)
        for tarefa in tarefas_principais:
            item = self._inserir_tarefa(tarefa)
            # Adicionar subtarefas
            self._adicionar_subtarefas_recursivamente(tarefa[0], item)
    
    def _adicionar_subtarefas_recursivamente(self, parent_id, parent_item):
        """Adiciona subtarefas recursivamente"""
        subtarefas = self.task_manager.obter_subtarefas(parent_id)
        for subtarefa in subtarefas:
            item = self._inserir_tarefa(subtarefa, parent_item)
            # Recursivamente adicionar sub-subtarefas
            self._adicionar_subtarefas_recursivamente(subtarefa[0], item)
    
    def _inserir_tarefa(self, tarefa, parent=''):
        """Insere uma tarefa na Treeview"""
        tags = ()
        if tarefa[4] == 'Alta':
            tags = ('alta',)
        elif tarefa[4] == 'Média':
            tags = ('media',)
        elif tarefa[4] == 'Baixa':
            tags = ('baixa',)
            
        return self.tree.insert(parent, 'end', values=(
            tarefa[0],  # ID
            tarefa[1],  # Título
            tarefa[3],  # Categoria
            tarefa[4],  # Prioridade
            tarefa[5],  # Estado
            tarefa[7]   # Data Vencimento
        ), tags=tags)

    def _mostrar_menu_contexto(self, event):
        """Mostra o menu de contexto"""
        item = self.tree.identify_row(event.y)
        if item:
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _analisar_tarefa_selecionada(self):
        """Analisa a tarefa selecionada com IA"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Obter dados da tarefa selecionada
        valores = self.tree.item(selected_item)['values']
        task_id = valores[0]
        
        # Obter tarefa completa do banco de dados
        tarefas = self.task_manager.filtrar_tarefas(id=task_id)
        if not tarefas:
            return
        
        tarefa = {
            'titulo': tarefas[0][1],
            'descricao': tarefas[0][2],
            'categoria': tarefas[0][3],
            'prioridade': tarefas[0][4]
        }
        
        # Obter sugestões da IA
        sugestoes = self.ai_analyzer.sugerir_melhorias(tarefa)
        if sugestoes:
            self._mostrar_sugestoes_melhoria(sugestoes, task_id)

    def _mostrar_sugestoes_melhoria(self, sugestoes, task_id):
        """Mostra uma janela com sugestões de melhoria"""
        # Criar janela de diálogo
        dialog = ttk.Toplevel(self.root)
        dialog.title("Análise da IA")
        
        # Centralizar a janela
        window_width = 500
        window_height = 400
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        dialog.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        mensagem = f"""Sugestões de Melhoria:

Título: {sugestoes.get('melhorias_titulo', '')}
Descrição: {sugestoes.get('melhorias_descricao', '')}

Ajustes Sugeridos:
- Prioridade: {sugestoes.get('ajustes_sugeridos', {}).get('prioridade', 'Não especificada')}
- Categoria: {sugestoes.get('ajustes_sugeridos', {}).get('categoria', 'Não especificada')}

Subtarefas Sugeridas:"""
        
        for subtarefa in sugestoes.get('subtarefas_sugeridas', []):
            mensagem += f"\n- {subtarefa}"
        
        mensagem += "\n\nRecomendações Adicionais:"
        for rec in sugestoes.get('recomendacoes', []):
            mensagem += f"\n- {rec}"
        
        # Adicionar texto com scroll
        text_widget = ttk.Text(dialog, wrap='word', width=60, height=15)
        text_widget.insert('1.0', mensagem)
        text_widget.pack(padx=20, pady=20, fill='both', expand=True)
        
        # Frame para botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def aplicar():
            dialog.result = "Yes"
            dialog.destroy()
            
        def cancelar():
            dialog.result = "No"
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Aplicar Sugestões", command=aplicar, bootstyle="success").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=cancelar, bootstyle="secondary").pack(side='left', padx=5)
        
        # Tornar a janela modal
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        if getattr(dialog, 'result', 'No') == "Yes":
            # Aplicar ajustes sugeridos
            ajustes = sugestoes.get('ajustes_sugeridos', {})
            if ajustes:
                self.task_manager.atualizar_tarefa(
                    task_id,
                    prioridade=ajustes.get('prioridade'),
                    categoria=ajustes.get('categoria')
                )
            self._atualizar_lista_tarefas()
            
            # Perguntar sobre criação de subtarefas
            subtarefas = sugestoes.get('subtarefas_sugeridas', [])
            if subtarefas:
                if Messagebox.show_question(
                    title="Subtarefas",
                    message="Deseja criar as subtarefas sugeridas?",
                    parent=self.root,
                    position=self._get_center_position()
                ) == "Yes":
                    for subtarefa in subtarefas:
                        self.task_manager.criar_tarefa(
                            titulo=subtarefa,
                            descricao="",
                            categoria=ajustes.get('categoria', 'Pessoal'),
                            prioridade=ajustes.get('prioridade', 'Média'),
                            data_vencimento="",
                            parent_id=task_id
                        )
                    self._atualizar_lista_tarefas()

    def _mudar_estado(self, novo_estado):
        """Muda o estado da tarefa selecionada"""
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_warning(
                title="Aviso",
                message="Por favor, selecione uma tarefa para mudar o estado!",
                parent=self.root,
                position=self._get_center_position()
            )
            return
        
        task_id = self.tree.item(selected_item)['values'][0]
        try:
            self.task_manager.atualizar_tarefa(task_id, estado=novo_estado)
            self._atualizar_lista_tarefas()
            Messagebox.show_info(
                title="Sucesso",
                message=f"Estado da tarefa alterado para '{novo_estado}'!",
                parent=self.root,
                position=self._get_center_position()
            )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao atualizar estado da tarefa: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _eliminar_tarefa(self):
        """Elimina a tarefa selecionada"""
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_warning(
                title="Aviso",
                message="Por favor, selecione uma tarefa para eliminar!",
                parent=self.root,
                position=self._get_center_position()
            )
            return
        
        task_id = self.tree.item(selected_item)['values'][0]
        task_titulo = self.tree.item(selected_item)['values'][1]
        
        resposta = Messagebox.show_question(
            title="Confirmar Eliminação",
            message=f"Tem certeza que deseja eliminar a tarefa:\n'{task_titulo}'?",
            parent=self.root,
            position=self._get_center_position()
        )
        
        if resposta == "Yes":  # Só elimina se a resposta for "Yes"
            try:
                if self.task_manager.eliminar_tarefa(task_id):
                    self._atualizar_lista_tarefas()
                    Messagebox.show_info(
                        title="Sucesso",
                        message="Tarefa eliminada com sucesso!",
                        parent=self.root,
                        position=self._get_center_position()
                    )
                else:
                    Messagebox.show_error(
                        title="Erro",
                        message="Não foi possível eliminar a tarefa.",
                        parent=self.root,
                        position=self._get_center_position()
                    )
            except Exception as e:
                Messagebox.show_error(
                    title="Erro",
                    message=f"Erro ao eliminar tarefa: {str(e)}",
                    parent=self.root,
                    position=self._get_center_position()
                )

    def _exportar_json(self):
        """Função para exportar para JSON com seleção de pasta"""
        try:
            # Abrir diálogo para selecionar pasta
            pasta_destino = filedialog.askdirectory(
                title="Selecionar pasta para exportar JSON",
                initialdir=os.path.expanduser("~/Desktop")  # Começa no ambiente de trabalho
            )
            
            if pasta_destino:  # Se uma pasta foi selecionada
                caminho_completo = os.path.join(pasta_destino, "tarefas.json")
                self.task_manager.exportar_para_json(caminho_completo, pasta_personalizada=True)
                
                Messagebox.show_info(
                    title="Sucesso",
                    message=f"Tarefas exportadas com sucesso para:\n{caminho_completo}",
                    parent=self.root,
                    position=self._get_center_position()
                )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao exportar tarefas: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _exportar_csv(self):
        """Função para exportar para CSV com seleção de pasta"""
        try:
            # Abrir diálogo para selecionar pasta
            pasta_destino = filedialog.askdirectory(
                title="Selecionar pasta para exportar CSV",
                initialdir=os.path.expanduser("~/Desktop")  # Começa no ambiente de trabalho
            )
            
            if pasta_destino:  # Se uma pasta foi selecionada
                caminho_completo = os.path.join(pasta_destino, "tarefas.csv")
                self.task_manager.exportar_para_csv(caminho_completo, pasta_personalizada=True)
                
                Messagebox.show_info(
                    title="Sucesso",
                    message=f"Tarefas exportadas com sucesso para:\n{caminho_completo}",
                    parent=self.root,
                    position=self._get_center_position()
                )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao exportar tarefas: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _importar_json(self):
        """Função para importar de JSON com seleção de arquivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Selecionar arquivo JSON para importar",
                initialdir=os.path.expanduser("~/Desktop"),
                filetypes=[("Arquivos JSON", "*.json")]
            )
            
            if filename:  # Se um arquivo foi selecionado
                if self.task_manager.importar_de_json(filename, pasta_personalizada=True):
                    self._atualizar_lista_tarefas()
                    Messagebox.show_info(
                        title="Sucesso",
                        message="Tarefas importadas com sucesso!",
                        parent=self.root,
                        position=self._get_center_position()
                    )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao importar tarefas: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _importar_csv(self):
        """Função para importar de CSV com seleção de arquivo"""
        try:
            filename = filedialog.askopenfilename(
                title="Selecionar arquivo CSV para importar",
                initialdir=os.path.expanduser("~/Desktop"),
                filetypes=[("Arquivos CSV", "*.csv")]
            )
            
            if filename:  # Se um arquivo foi selecionado
                if self.task_manager.importar_de_csv(filename, pasta_personalizada=True):
                    self._atualizar_lista_tarefas()
                    Messagebox.show_info(
                        title="Sucesso",
                        message="Tarefas importadas com sucesso!",
                        parent=self.root,
                        position=self._get_center_position()
                    )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao importar tarefas: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _filtrar_tarefas(self):
        """Filtra as tarefas com base nos critérios de pesquisa e filtros"""
        # Limpar a lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obter todas as tarefas
        tarefas = self.task_manager.obter_todas_tarefas()
        termo_pesquisa = self.var_pesquisa.get().lower()
        estado_filtro = self.var_filtro_estado.get()
        prioridade_filtro = self.var_filtro_prioridade.get()
        
        for tarefa in tarefas:
            # Aplicar filtros
            if estado_filtro != "Todos" and tarefa[5].lower() != estado_filtro.lower():
                continue
            if prioridade_filtro != "Todas" and tarefa[4] != prioridade_filtro:
                continue
            
            # Aplicar pesquisa
            if termo_pesquisa and termo_pesquisa not in tarefa[1].lower():  # Pesquisa por título
                continue
                
            # Definir estilo baseado na prioridade
            tags = ()
            if tarefa[4] == 'Alta':
                tags = ('alta',)
            elif tarefa[4] == 'Média':
                tags = ('media',)
            elif tarefa[4] == 'Baixa':
                tags = ('baixa',)
                
            self.tree.insert('', 'end', values=(
                tarefa[0],  # ID
                tarefa[1],  # Título
                tarefa[3],  # Categoria
                tarefa[4],  # Prioridade
                tarefa[5],  # Estado
                tarefa[7]   # Data Vencimento
            ), tags=tags)

    def _mudar_tema(self, tema):
        """Muda o tema da aplicação"""
        self.style.theme_use(tema)
        Messagebox.show_info(
            title="Tema Alterado",
            message=f"Tema alterado para {tema.capitalize()}",
            parent=self.root,
            position=self._get_center_position()
        )
        
    def _mostrar_estatisticas(self):
        """Mostra estatísticas das tarefas"""
        tarefas = self.task_manager.obter_todas_tarefas()
        total = len(tarefas)
        
        # Contadores
        pendentes = sum(1 for t in tarefas if t[5].lower() == 'pendente')
        em_progresso = sum(1 for t in tarefas if t[5].lower() == 'em progresso')
        concluidas = sum(1 for t in tarefas if t[5].lower() == 'concluída')
        
        # Prioridades
        alta = sum(1 for t in tarefas if t[4] == 'Alta')
        media = sum(1 for t in tarefas if t[4] == 'Média')
        baixa = sum(1 for t in tarefas if t[4] == 'Baixa')
        
        # Categorias
        categorias = {}
        for t in tarefas:
            cat = t[3]
            categorias[cat] = categorias.get(cat, 0) + 1
        
        # Criar janela de estatísticas
        stats_window = ttk.Toplevel(self.root)
        stats_window.title("Estatísticas")
        stats_window.geometry("400x500")
        
        # Centralizar a janela
        window_width = 400
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        stats_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Frame principal
        main_frame = ttk.Frame(stats_window, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Título
        ttk.Label(
            main_frame,
            text="Estatísticas das Tarefas",
            font=("Helvetica", 16, "bold"),
            bootstyle="inverse-primary"
        ).pack(pady=(0, 20))
        
        # Total de tarefas
        ttk.Label(
            main_frame,
            text=f"Total de Tarefas: {total}",
            font=("Helvetica", 12)
        ).pack(pady=5)
        
        # Estados
        ttk.Label(
            main_frame,
            text="\nEstados:",
            font=("Helvetica", 12, "bold")
        ).pack()
        ttk.Label(main_frame, text=f"Pendentes: {pendentes}").pack()
        ttk.Label(main_frame, text=f"Em Progresso: {em_progresso}").pack()
        ttk.Label(main_frame, text=f"Concluídas: {concluidas}").pack()
        
        # Prioridades
        ttk.Label(
            main_frame,
            text="\nPrioridades:",
            font=("Helvetica", 12, "bold")
        ).pack()
        ttk.Label(main_frame, text=f"Alta: {alta}").pack()
        ttk.Label(main_frame, text=f"Média: {media}").pack()
        ttk.Label(main_frame, text=f"Baixa: {baixa}").pack()
        
        # Categorias
        ttk.Label(
            main_frame,
            text="\nCategorias:",
            font=("Helvetica", 12, "bold")
        ).pack()
        for cat, count in categorias.items():
            if cat:  # Só mostrar se a categoria não estiver vazia
                ttk.Label(main_frame, text=f"{cat}: {count}").pack()
        
        # Botão de fechar
        ttk.Button(
            main_frame,
            text="Fechar",
            command=stats_window.destroy,
            bootstyle="secondary"
        ).pack(pady=20)
        
    def _fazer_backup(self):
        """Realiza backup automático das tarefas"""
        try:
            # Criar pasta de backup se não existir
            backup_dir = os.path.join(os.path.expanduser("~"), "TaskManagerBackup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Nome do arquivo com data/hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup JSON
            json_backup = os.path.join(backup_dir, f"backup_{timestamp}.json")
            self.task_manager.exportar_para_json(json_backup, pasta_personalizada=True)
            
            # Backup CSV
            csv_backup = os.path.join(backup_dir, f"backup_{timestamp}.csv")
            self.task_manager.exportar_para_csv(csv_backup, pasta_personalizada=True)
            
            Messagebox.show_info(
                title="Backup Realizado",
                message=f"Backup realizado com sucesso em:\n{backup_dir}",
                parent=self.root,
                position=self._get_center_position()
            )
        except Exception as e:
            Messagebox.show_error(
                title="Erro",
                message=f"Erro ao realizar backup: {str(e)}",
                parent=self.root,
                position=self._get_center_position()
            )

    def _adicionar_subtarefa(self):
        """Adiciona uma subtarefa à tarefa selecionada"""
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_warning(
                title="Aviso",
                message="Por favor, selecione uma tarefa para adicionar uma subtarefa!",
                parent=self.root,
                position=self._get_center_position()
            )
            return
        
        parent_id = self.tree.item(selected_item)['values'][0]
        parent_titulo = self.tree.item(selected_item)['values'][1]
        
        # Criar janela de subtarefa
        subtask_window = ttk.Toplevel(self.root)
        subtask_window.title(f"Nova Subtarefa para: {parent_titulo}")
        subtask_window.geometry("400x500")
        
        # Centralizar a janela
        window_width = 400
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        subtask_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Frame principal
        main_frame = ttk.Frame(subtask_window, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Variáveis
        var_titulo = ttk.StringVar()
        var_descricao = ttk.StringVar()
        var_categoria = ttk.StringVar()
        var_prioridade = ttk.StringVar()
        var_data_vencimento = ttk.StringVar()
        
        # Campos
        ttk.Label(main_frame, text="Título:").pack(fill=X)
        ttk.Entry(
            main_frame,
            textvariable=var_titulo,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Descrição:").pack(fill=X)
        ttk.Entry(
            main_frame,
            textvariable=var_descricao,
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Categoria:").pack(fill=X)
        ttk.Combobox(
            main_frame,
            textvariable=var_categoria,
            values=['Trabalho', 'Estudos', 'Pessoal'],
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Prioridade:").pack(fill=X)
        ttk.Combobox(
            main_frame,
            textvariable=var_prioridade,
            values=['Alta', 'Média', 'Baixa'],
            bootstyle="primary"
        ).pack(fill=X, pady=(0, 10))
        
        # Data
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(data_frame, text="Data Vencimento:").pack(side=LEFT)
        ttk.Entry(
            data_frame,
            textvariable=var_data_vencimento,
            bootstyle="primary",
            width=15
        ).pack(side=LEFT, padx=5)
        
        def selecionar_data():
            dialog = CalendarDialog(subtask_window)
            subtask_window.wait_window(dialog)
            if dialog.selected_date:
                var_data_vencimento.set(dialog.selected_date)
        
        ttk.Button(
            data_frame,
            text="📅",
            command=selecionar_data,
            bootstyle="primary-outline",
            width=3
        ).pack(side=LEFT)
        
        def adicionar():
            if not var_titulo.get():
                Messagebox.show_error(
                    title="Erro",
                    message="O título é obrigatório!",
                    parent=subtask_window
                )
                return
            
            try:
                self.task_manager.criar_tarefa(
                    titulo=var_titulo.get(),
                    descricao=var_descricao.get(),
                    categoria=var_categoria.get(),
                    prioridade=var_prioridade.get(),
                    data_vencimento=var_data_vencimento.get(),
                    parent_id=parent_id
                )
                self._atualizar_lista_tarefas()
                subtask_window.destroy()
                Messagebox.show_info(
                    title="Sucesso",
                    message="Subtarefa adicionada com sucesso!",
                    parent=self.root,
                    position=self._get_center_position()
                )
            except Exception as e:
                Messagebox.show_error(
                    title="Erro",
                    message=f"Erro ao adicionar subtarefa: {str(e)}",
                    parent=subtask_window
                )
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=20)
        
        ttk.Button(
            btn_frame,
            text="Adicionar",
            command=adicionar,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=subtask_window.destroy,
            bootstyle="secondary"
        ).pack(side=LEFT)

    def _on_closing(self):
        """Handler para quando a janela é fechada"""
        try:
            # Fechar conexão com a base de dados
            self.task_manager.fechar_conexao()
        finally:
            # Destruir a janela mesmo se houver erro ao fechar a conexão
            self.root.destroy()

    def _adicionar_mensagem_sistema(self, mensagem):
        """Adiciona uma mensagem do sistema ao chat"""
        self.chat_area.configure(state='normal')
        self.chat_area.insert('end', f"🤖 Assistente: {mensagem}\n\n")
        self.chat_area.see('end')
        self.chat_area.configure(state='disabled')

    def _adicionar_mensagem_usuario(self, mensagem):
        """Adiciona uma mensagem do utilizador ao chat"""
        self.chat_area.configure(state='normal')
        self.chat_area.insert('end', f"👤 Você: {mensagem}\n\n")
        self.chat_area.see('end')
        self.chat_area.configure(state='disabled')

    def _mostrar_digitando(self):
        """Mostra indicador de digitação"""
        self.typing_label.configure(text="IA está a escrever...")

    def _esconder_digitando(self):
        """Esconde indicador de digitação"""
        self.typing_label.configure(text="")

    def _processar_comando_ia(self, comando):
        """Processa comandos específicos da IA"""
        if comando.startswith("/criar_tarefa"):
            # Extrair informações da tarefa do comando
            try:
                _, titulo = comando.split(" ", 1)
                self.var_titulo.set(titulo)
                self._adicionar_tarefa()
                return "Tarefa criada com sucesso!"
            except Exception as e:
                return f"Erro ao criar tarefa: {str(e)}"
        
        elif comando.startswith("/listar_tarefas"):
            # Listar todas as tarefas
            tarefas = self.task_manager.obter_todas_tarefas()
            if not tarefas:
                return "Não há tarefas registadas."
            
            resposta = "Tarefas atuais:\n"
            for t in tarefas:
                resposta += f"- {t[1]} ({t[5]})\n"
            return resposta
        
        elif comando.startswith("/ajuda"):
            return """Comandos disponíveis:
- /criar_tarefa [título]
- /listar_tarefas
- /ajuda

Você também pode:
- Perguntar sobre tarefas específicas
- Pedir sugestões de organização
- Solicitar análise de prioridades
- Pedir ajuda com prazos
- Solicitar decomposição de tarefas
"""
        return None

    def _enviar_mensagem(self):
        """Processa o envio de mensagem do utilizador"""
        mensagem = self.message_var.get().strip()
        if not mensagem:
            return
        
        # Limpar campo de mensagem
        self.message_var.set("")
        
        # Adicionar mensagem do utilizador ao chat
        self._adicionar_mensagem_usuario(mensagem)
        
        # Verificar se é um comando
        if mensagem.startswith("/"):
            resposta = self._processar_comando_ia(mensagem)
            if resposta:
                self._adicionar_mensagem_sistema(resposta)
                return
        
        # Processar mensagem normal
        self._mostrar_digitando()
        
        try:
            # Analisar a mensagem e gerar resposta
            analise = self.ai_analyzer.analisar_mensagem(
                mensagem=mensagem,
                tarefas_atuais=[{
                    'titulo': t[1],
                    'descricao': t[2],
                    'estado': t[5],
                    'prioridade': t[4]
                } for t in self.task_manager.obter_todas_tarefas()]
            )
            
            # Processar a resposta
            if isinstance(analise, dict):
                resposta = analise.get('resposta', 'Desculpe, não consegui processar sua solicitação.')
                
                # Verificar se há ações sugeridas
                acoes = analise.get('acoes_sugeridas', [])
                if acoes:
                    resposta += "\n\nAções sugeridas:"
                    for acao in acoes:
                        resposta += f"\n- {acao}"
            else:
                resposta = "Desculpe, ocorreu um erro ao processar sua mensagem."
            
            self._adicionar_mensagem_sistema(resposta)
            
        except Exception as e:
            self._adicionar_mensagem_sistema(
                "Desculpe, ocorreu um erro ao processar sua mensagem. "
                "Por favor, tente novamente mais tarde."
            )
            print(f"Erro ao processar mensagem: {str(e)}")
        
        finally:
            self._esconder_digitando() 