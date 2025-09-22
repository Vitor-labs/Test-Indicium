# agents/report_agent.py
import json
from datetime import datetime
from typing import Any, Dict

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.llms import OpenAI


class SRAGReportAgent:
    def __init__(
        self,
        db_agent: SRAGDatabaseAgent,
        news_agent: SRAGNewsAgent,
        openai_api_key: str,
    ):
        self.db_agent = db_agent
        self.news_agent = news_agent
        self.llm = OpenAI(temperature=0.3, openai_api_key=openai_api_key)

        # Define as ferramentas disponíveis para o agente
        self.tools = [
            Tool(
                name="get_srag_metrics",
                description="Obtém todas as métricas de SRAG do banco de dados",
                func=self._get_metrics_tool,
            ),
            Tool(
                name="get_srag_news",
                description="Busca notícias recentes sobre SRAG",
                func=self._get_news_tool,
            ),
            Tool(
                name="analyze_trends",
                description="Analisa tendências nos dados de SRAG",
                func=self._analyze_trends_tool,
            ),
        ]

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

    def _get_metrics_tool(self, input_text: str) -> str:
        """Ferramenta para obter métricas do banco"""
        metrics = self.db_agent.get_all_metrics()
        return json.dumps(metrics, ensure_ascii=False, indent=2)

    def _get_news_tool(self, input_text: str) -> str:
        """Ferramenta para obter notícias"""
        news = self.news_agent.get_recent_news()
        return json.dumps(news, ensure_ascii=False, indent=2)

    def _analyze_trends_tool(self, input_text: str) -> str:
        """Ferramenta para análise de tendências"""
        metrics = self.db_agent.get_all_metrics()

        analysis = {
            "tendencia_casos": "crescente"
            if metrics["taxa_aumento_casos"]["taxa_aumento"] > 0
            else "decrescente",
            "situacao_critica": metrics["taxa_mortalidade"]["taxa_mortalidade"] > 5,
            "pressao_uti": metrics["taxa_ocupacao_uti"]["taxa_ocupacao_uti"] > 80,
            "cobertura_vacinal": "baixa"
            if metrics["taxa_vacinacao"]["taxa_vacinacao"] < 70
            else "adequada",
        }

        return json.dumps(analysis, ensure_ascii=False, indent=2)

    def generate_report(self) -> Dict[str, Any]:
        """Gera o relatório completo de SRAG"""

        prompt = """
        Você é um especialista em saúde pública analisando dados de SRAG (Síndrome Respiratória Aguda Grave).
        
        Sua tarefa é gerar um relatório completo que inclua:
        
        1. MÉTRICAS PRINCIPAIS:
        - Taxa de aumento de casos
        - Taxa de mortalidade  
        - Taxa de ocupação de UTI
        - Taxa de vacinação da população
        
        2. ANÁLISE CONTEXTUAL:
        - Busque notícias recentes sobre SRAG
        - Analise as tendências dos dados
        - Forneça explicações claras sobre o cenário atual
        
        3. INTERPRETAÇÃO:
        - Explique o que cada métrica significa
        - Identifique alertas ou pontos de atenção
        - Sugira ações baseadas nos dados
        
        Use as ferramentas disponíveis para obter os dados necessários e gere um relatório estruturado e informativo.
        """

        try:
            # Executa o agente
            response = self.agent.run(prompt)

            # Obtém dados brutos para incluir no relatório
            metrics = self.db_agent.get_all_metrics()
            news = self.news_agent.get_recent_news()

            report = {
                "data_geracao": datetime.now().isoformat(),
                "analise_ia": response,
                "metricas_detalhadas": metrics,
                "noticias_relacionadas": news,
                "graficos_gerados": {
                    "casos_diarios": metrics["graficos"]["casos_diarios"],
                    "casos_mensais": metrics["graficos"]["casos_mensais"],
                },
            }

            return report

        except Exception as e:
            return {
                "erro": f"Erro ao gerar relatório: {str(e)}",
                "data_geracao": datetime.now().isoformat(),
            }
