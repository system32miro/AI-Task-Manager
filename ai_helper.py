import os
from dotenv import load_dotenv
import groq
import json
from datetime import datetime, timedelta

# Carregar variáveis de ambiente
load_dotenv()

class AITaskAnalyzer:
    def __init__(self):
        self.client = groq.Groq(
            api_key=os.getenv('GROQ_API_KEY')
        )
        self.model = "mixtral-8x7b-32768"  # Mudando para um modelo mais estável

    def _formatar_resposta_padrao(self):
        """Retorna uma resposta padrão em caso de erro"""
        hoje = datetime.now()
        data_sugerida = (hoje + timedelta(days=7)).strftime('%Y-%m-%d')
        return {
            "prioridade": "Média",
            "categoria": "Pessoal",
            "data_vencimento": data_sugerida,
            "tarefas_similares": [],
            "justificativas": {
                "prioridade": "Definido como média por padrão",
                "categoria": "Definido como pessoal por padrão",
                "data_vencimento": "Data estimada para uma semana a partir de hoje"
            }
        }

    def _formatar_resposta_melhoria_padrao(self, tarefa):
        """Retorna uma resposta padrão de melhoria em caso de erro"""
        return {
            "melhorias_titulo": f"Considere ser mais específico no título: {tarefa['titulo']}",
            "melhorias_descricao": "Adicione mais detalhes à descrição",
            "ajustes_sugeridos": {
                "prioridade": tarefa.get('prioridade', 'Média'),
                "categoria": tarefa.get('categoria', 'Pessoal')
            },
            "subtarefas_sugeridas": ["Detalhar melhor a tarefa", "Definir prazo específico"],
            "recomendacoes": ["Adicione mais contexto", "Estabeleça métricas de conclusão"]
        }

    def analisar_tarefa(self, titulo, descricao, tarefas_existentes=None):
        """Analisa uma nova tarefa e sugere prioridade, categoria e verifica similaridades"""
        # Preparar contexto
        contexto_tarefas = ""
        if tarefas_existentes:
            contexto_tarefas = "\n".join([f"- {t['titulo']}: {t.get('descricao', '')}" for t in tarefas_existentes])

        prompt = f"""
        Você é um assistente de gestão de tarefas. Analise a seguinte tarefa e forneça recomendações.
        Responda APENAS com um objeto JSON válido, sem texto adicional.

        Tarefa:
        - Título: {titulo}
        - Descrição: {descricao}
        
        {contexto_tarefas}

        Formato da resposta (mantenha exatamente esta estrutura):
        {{
            "prioridade": "Alta|Média|Baixa",
            "categoria": "Trabalho|Estudos|Pessoal",
            "data_vencimento": "YYYY-MM-DD",
            "tarefas_similares": ["tarefa1", "tarefa2"],
            "justificativas": {{
                "prioridade": "razão da prioridade escolhida",
                "categoria": "razão da categoria escolhida",
                "data_vencimento": "razão da data escolhida"
            }}
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em análise de tarefas. Responda APENAS com JSON válido, sem texto adicional."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,  # Reduzindo a temperatura para respostas mais consistentes
                max_tokens=1000
            )

            resposta = chat_completion.choices[0].message.content.strip()
            try:
                # Tentar processar a resposta como JSON
                return json.loads(resposta)
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {str(e)}")
                print(f"Resposta recebida: {resposta}")
                return self._formatar_resposta_padrao()

        except Exception as e:
            print(f"Erro na análise da tarefa: {str(e)}")
            return self._formatar_resposta_padrao()

    def sugerir_melhorias(self, tarefa):
        """Sugere melhorias para uma tarefa existente"""
        prompt = f"""
        Você é um especialista em produtividade. Analise esta tarefa e sugira melhorias.
        Responda APENAS com um objeto JSON válido, sem texto adicional.

        Tarefa atual:
        - Título: {tarefa['titulo']}
        - Descrição: {tarefa.get('descricao', '')}
        - Prioridade: {tarefa.get('prioridade', '')}
        - Categoria: {tarefa.get('categoria', '')}

        Formato da resposta (mantenha exatamente esta estrutura):
        {{
            "melhorias_titulo": "sugestão de melhoria para o título",
            "melhorias_descricao": "sugestão de melhoria para a descrição",
            "ajustes_sugeridos": {{
                "prioridade": "Alta|Média|Baixa",
                "categoria": "Trabalho|Estudos|Pessoal"
            }},
            "subtarefas_sugeridas": ["subtarefa1", "subtarefa2"],
            "recomendacoes": ["recomendação1", "recomendação2"]
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em otimização de tarefas. Responda APENAS com JSON válido, sem texto adicional."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1000
            )

            resposta = chat_completion.choices[0].message.content.strip()
            try:
                # Tentar processar a resposta como JSON
                return json.loads(resposta)
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {str(e)}")
                print(f"Resposta recebida: {resposta}")
                return self._formatar_resposta_melhoria_padrao(tarefa)

        except Exception as e:
            print(f"Erro ao sugerir melhorias: {str(e)}")
            return self._formatar_resposta_melhoria_padrao(tarefa)

    def analisar_mensagem(self, mensagem, tarefas_atuais=None):
        """Analisa uma mensagem do utilizador e retorna uma resposta apropriada"""
        try:
            # Preparar o contexto com as tarefas atuais
            contexto = ""
            if tarefas_atuais:
                contexto = "Tarefas atuais:\n"
                for t in tarefas_atuais:
                    contexto += f"- {t['titulo']} ({t['estado']}, {t['prioridade']})\n"
            
            # Preparar o prompt para a IA
            prompt = f"""Contexto do Gestor de Tarefas:
{contexto}

Mensagem do utilizador: {mensagem}

Por favor, analise a mensagem e forneça:
1. Uma resposta útil e relevante
2. Sugestões de ações práticas quando apropriado
3. Considere o contexto das tarefas existentes

Responda em português de Portugal e mantenha um tom profissional mas amigável.
"""
            
            # Fazer a chamada à API
            client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": "Você é um assistente especializado em gestão de tarefas, focado em ajudar utilizadores a organizar e otimizar suas atividades."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                model="mixtral-8x7b-32768",
                temperature=0.1,
                max_tokens=1000
            )
            
            # Processar a resposta
            resposta_ia = chat_completion.choices[0].message.content
            
            # Tentar extrair ações sugeridas da resposta
            acoes_sugeridas = []
            linhas = resposta_ia.split('\n')
            for linha in linhas:
                if linha.strip().startswith('-') or linha.strip().startswith('*'):
                    acoes_sugeridas.append(linha.strip()[2:].strip())
            
            return {
                'resposta': resposta_ia,
                'acoes_sugeridas': acoes_sugeridas
            }
            
        except Exception as e:
            print(f"Erro ao analisar mensagem: {str(e)}")
            return {
                'resposta': "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.",
                'acoes_sugeridas': []
            } 