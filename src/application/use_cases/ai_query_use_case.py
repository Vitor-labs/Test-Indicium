# src/application/use_cases/ai_query_use_case.py
from domain.repositories.data_repository import DataRepository
from domain.repositories.vector_repository import VectorRepository
from domain.services.llm_service import LLMService


class AIQueryUseCase:
    """Caso de uso para consultas com IA."""

    def __init__(
        self,
        data_repository: DataRepository,
        vector_repository: VectorRepository,
        llm_service: LLMService,
        schema_info: dict[str, str],
    ) -> None:
        """
        Inicializa caso de uso de consultas IA.

        Args:
            data_repository: Repositório de dados
            vector_repository: Repositório de vetores
            llm_service: Serviço de LLM
            schema_info: Informações do schema da base
        """
        self.data_repository = data_repository
        self.vector_repository = vector_repository
        self.llm_service = llm_service
        self.schema_info = schema_info

    def ask_question(self, question: str) -> str:
        """
        Processa pergunta em linguagem natural e retorna resposta.

        Args:
            question: Pergunta em linguagem natural

        Returns:
            Resposta estruturada com dados e notícias relacionadas
        """
        # 1. Converter para SQL
        sql = self.llm_service.natural_to_sql(question, self.schema_info)
        print(f"SQL gerado: {sql}")

        # 2. Executar query
        results = self.data_repository.execute_query(sql)

        # 3. Sumarizar resultados
        summary = self.llm_service.summarize_results(question, results)

        # 4. Buscar notícias relacionadas
        related_articles = self.vector_repository.search_similar(summary, limit=5)
        article_titles = [
            f"{article.id}: {article.title}" for article in related_articles
        ]

        # 5. Gerar resposta final
        final_answer = self.llm_service.generate_final_answer(
            question, sql, summary, article_titles
        )

        return final_answer
