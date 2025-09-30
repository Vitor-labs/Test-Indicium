# src/domain/repositories/vector_repository.py
from abc import ABC, abstractmethod

from domain.entities.document import Article


class VectorRepository(ABC):
    """Interface para repositório de vetores."""

    @abstractmethod
    def add_documents(self, articles: list[Article]) -> None:
        """Adiciona documentos ao repositório de vetores."""
        pass

    @abstractmethod
    def search_similar(self, query: str, limit: int = 5) -> list[Article]:
        """Busca documentos similares."""
        pass
