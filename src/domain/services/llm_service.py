# src/domain/services/llm_service.py
from abc import ABC, abstractmethod


class LLMService(ABC):
    """Interface para serviços de LLM."""

    @abstractmethod
    def natural_to_sql(self, question: str, schema_info: dict[str, str]) -> str:
        """Converte linguagem natural para SQL."""
        pass

    @abstractmethod
    def summarize_results(self, question: str, results: list[tuple]) -> str:
        """Sumariza resultados de query."""
        pass

    @abstractmethod
    def generate_final_answer(
        self, question: str, sql: str, summary: str, articles: list[str]
    ) -> str:
        """Gera resposta final baseada em todos os dados."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Gera embedding para texto."""
        pass
