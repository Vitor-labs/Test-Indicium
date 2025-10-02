# src/domain/services/chain_service.py
from abc import ABC, abstractmethod


class ChainService(ABC):
    """Interface para serviços de chains LangChain."""

    @abstractmethod
    def sql_chain(self, question: str, schema_info: str) -> str:
        """Chain para conversão NL->SQL."""
        pass

    @abstractmethod
    def summarization_chain(self, question: str, data: list[tuple[str]]) -> str:
        """Chain para sumarização de dados."""
        pass

    @abstractmethod
    def rag_chain(self, question: str, context: str) -> str:
        """Chain para RAG (Retrieval-Augmented Generation)."""
        pass
