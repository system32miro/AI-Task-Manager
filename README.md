# Gestor de Tarefas com IA

Uma aplicação desktop moderna em Python para gestão de tarefas, com interface gráfica intuitiva e assistente de IA integrado.

![Gestor de Tarefas](https://github.com/system32miro/gestor-tarefas-ia/raw/main/Captura%20de%20ecrã%202025-02-10%20110341.png)

## 🌟 Funcionalidades Principais

### Gestão de Tarefas
- ✅ Criar, editar e eliminar tarefas
- 📋 Organizar por categorias (Trabalho, Estudos, Pessoal)
- ⭐ Definir prioridades (Alta, Média, Baixa)
- 🔄 Gerir estados (Pendente, Em Progresso, Concluída)
- 📅 Definir datas de vencimento com calendário integrado
- 🌳 Suporte a subtarefas (hierarquia de tarefas)

### Interface Moderna
- 🎨 Temas personalizáveis (darkly, cosmo, flatly, etc.)
- 🔍 Pesquisa e filtros avançados
- 📊 Estatísticas detalhadas
- 📱 Interface responsiva e adaptável
- 🖱️ Menu de contexto e atalhos de teclado

### Assistente IA
- 🤖 Análise automática de novas tarefas
- 💡 Sugestões inteligentes de categorização
- 📈 Recomendações de prioridade
- 🔄 Análise de tarefas existentes
- 💬 Chat interativo para ajuda e sugestões

### Importação/Exportação
- 📤 Exportar tarefas para JSON/CSV
- 📥 Importar tarefas de JSON/CSV
- 💾 Backup automático
- 📁 Seleção personalizada de diretórios

### Armazenamento
- 🗄️ Base de dados SQLite
- 🔒 Persistência automática
- 🔄 Sincronização em tempo real

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/system32miro/gestor-tarefas-ia.git
   ```

2. Navegue até à pasta do projeto:
   ```bash
   cd gestor-tarefas-ia
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure a API da IA:
   ```bash
   cp .env.example .env
   ```
   Edite o arquivo `.env` e adicione sua chave API:
   ```
   GROQ_API_KEY=sua_chave_aqui
   ```

## 🎯 Utilização

1. Execute o programa:
   ```bash
   python main.py
   ```

2. Interface Principal:
   - Painel esquerdo: Formulário para novas tarefas e lista de tarefas
   - Painel direito: Assistente IA interativo
   - Botões inferiores: Ações rápidas e exportação/importação

3. Atalhos de Teclado:
   - `Ctrl+N`: Nova tarefa
   - `Ctrl+D`: Eliminar tarefa selecionada
   - `Ctrl+F`: Focar na pesquisa
   - `F5`: Atualizar lista de tarefas

4. Assistente IA:
   - Use o chat para pedir sugestões
   - Comandos disponíveis:
     - `/criar_tarefa [título]`
     - `/listar_tarefas`
     - `/ajuda`

## Estrutura do Projeto

```
gestor_tarefas/
│── main.py              # Ponto de entrada
│── gui.py              # Interface gráfica
│── tasks.py            # Gestão de tarefas
│── database.py         # Base de dados
│── ai_helper.py        # Integração com IA
│── requirements.txt    # Dependências
│── README.md          # Documentação
│── .env               # Configurações da API
│── data/              # Dados e backups
    │── tasks.db       # Base de dados SQLite
    │── *.json         # Exportações JSON
    │── *.csv          # Exportações CSV
```

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas alterações (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📫 Suporte

Para suporte ou dúvidas:
1. Abra uma [issue](https://github.com/system32miro/gestor-tarefas-ia/issues)
2. Consulte a [documentação](https://github.com/system32miro/gestor-tarefas-ia/wiki)
3. Entre em contacto com os mantenedores

## ⭐ Mostre seu apoio

Se este projeto te ajudou, por favor dê uma estrela! 