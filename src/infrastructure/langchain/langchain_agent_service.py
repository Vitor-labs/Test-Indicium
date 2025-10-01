# src/infrastructure/langchain/langchain_agent_service.py
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.sql_database import SQLDatabase

from domain.entities.document import QueryResult
from domain.repositories.data_repository import DataRepository
from domain.repositories.vector_repository import VectorRepository
from domain.services.agent_service import AgentService
from infrastructure.langchain.langchain_llm_service import LangChainLLMService


class LangChainAgentService(AgentService):
    """
    Agente inteligente que decide automaticamente qual ferramenta usar.

    Vantagens do LangChain Agent:
    - Decisões automáticas sobre SQL vs busca vetorial
    - Memory entre interações
    - Tool selection baseada no contexto
    - Reflexão e auto-correção
    """

    def __init__(
        self,
        llm_service: LangChainLLMService,
        data_repository: DataRepository,
        vector_repository: VectorRepository,
        db_path: str,
    ) -> None:
        """
        Inicializa agente LangChain.

        Args:
            llm_service: Serviço LLM
            data_repository: Repositório de dados
            vector_repository: Repositório vetorial
            db_path: Caminho do banco SQLite
        """
        self.llm = llm_service.llm
        self.data_repository = data_repository
        self.vector_repository = vector_repository
        # Database connection para SQL toolkit
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        # Memory para conversas
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history", k=10, return_messages=True
        )
        self._setup_tools()
        self._setup_agent()

    def _setup_tools(self) -> None:
        """Configura ferramentas disponíveis para o agente."""

        # SQL Toolkit - para consultas estruturadas
        sql_tools = SQLDatabaseToolkit(db=self.db, llm=self.llm).get_tools()

        def search_news_tool(query: str) -> str:  # Tool customizada para busca vetorial
            """Busca notícias relacionadas usando similaridade vetorial."""
            try:
                if not (
                    articles := self.vector_repository.search_similar(query, limit=5)
                ):
                    return "Nenhuma notícia relacionada encontrada."

                return "\n\n".join(
                    [
                        f"- {art.title}\n  Source: {art.source_name}\n  URL: {art.url}"
                        for art in articles
                    ]
                )
            except Exception as e:
                return f"Erro na busca de notícias: {e}"

        # Tool para análise epidemiológica especializada
        def epidemiological_analysis_tool(data_summary: str) -> str:
            """Análise epidemiológica especializada dos dados."""
            analysis_prompt = f"""
            As an epidemiologist, please review this SARS data summary:

			{data_summary}

			Provide:
			1. Epidemiological interpretation
			2. Possible causal factors
			3. Identified risk groups
			4. Public health recommendations
            """
            try:
                return str(
                    self.llm.invoke(
                        [{"role": "user", "content": analysis_prompt}]
                    ).content
                )
            except Exception as e:
                return f"Erro na análise epidemiológica: {e}"

        # Tool para contexto temporal
        def temporal_context_tool(question: str) -> str:
            """Adiciona contexto temporal relevante à análise."""
            context_prompt = f"""
            For this question about SARS data: {question}

			Provide relevant temporal context considering:
			- Seasonality of respiratory diseases
			- Major epidemiological events (2019-2024)
			- Impact of the COVID-19 pandemic
			- Vaccination campaigns

			Context in 2-3 paragraphs:
            """

            try:
                return str(
                    self.llm.invoke(
                        [{"role": "user", "content": context_prompt}]
                    ).content
                )
            except Exception as e:
                return f"Erro no contexto temporal: {e}"

        # Combinar todas as tools
        self.tools = sql_tools + [
            Tool(
                name="search_related_news",
                description="Searches for news related to the topic using semantic"
                "similarity. Use when you need current context on epidemics, outbreaks,"
                "or health policies.",
                func=search_news_tool,
            ),
            Tool(
                name="epidemiological_analysis",
                description="Specialized epidemiological analysis of data. Use after"
                "data acquisition for clinical and public health interpretation.",
                func=epidemiological_analysis_tool,
            ),
            Tool(
                name="temporal_context",
                description="Adds relevant temporal and historical context. Use it to"
                "understand trends and events that may have influenced the data.",
                func=temporal_context_tool,
            ),
        ]

    def _setup_agent(self) -> None:
        """Configura agente com tools e memory."""
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,  # Para debug
            max_iterations=6,  # Prevenir loops infinitos
            early_stopping_method="generate",
            agent_kwargs={
                "system_message": """
                You are an expert in epidemiology and public health data analysis.

				You have access to:
				1. SRAG database (2019-2024) via SQL
				2. Related news database via semantic search
				3. Specialized epidemiological analysis tools
				4. Temporal and historical context

				For each question:
				1. Determine if you need structured data (use SQL)
				2. Search for context in news stories if relevant
				3. Apply epidemiological analysis to the results
				4. Add temporal context when appropriate
				5. Provide comprehensive and actionable answers

				Always prioritize accuracy and clinical relevance.
                """
            },
        )

    def process_question(self, question: str) -> QueryResult:
        """
        Processa pergunta usando agente inteligente.

        O agente decide automaticamente:
        - Quais tools usar
        - Em que ordem
        - Como combinar resultados
        """
        try:
            # Agente processa a pergunta e decide workflow
            # Extrair informações do resultado
            # Buscar artigos relacionados para o QueryResult
            return QueryResult(
                data=[],  # Agent já processou e resumiu os dados
                summary=self.agent.invoke(
                    {
                        "input": question,
                        "chat_history": self.memory.chat_memory.messages,
                    }
                ).get("output", "Não foi possível processar a pergunta."),
                related_articles=self.vector_repository.search_similar(
                    question, limit=3
                ),
            )
        except Exception as e:
            return QueryResult(
                data=[], summary=f"Erro no processamento: {e}", related_articles=[]
            )

    def add_memory(self, question: str, answer: str) -> None:
        """Adiciona interação à memory (já gerenciada automaticamente)."""
        # LangChain agent já gerencia memory automaticamente
        # Este método é mantido para compatibilidade com a interface
        pass
