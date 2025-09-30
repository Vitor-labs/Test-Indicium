# src/domain/repositories/news_repository.py
from abc import ABC, abstractmethod

from domain.entities.document import Article


class NewsRepository(ABC):
    """Interface para repositório de notícias."""

    @abstractmethod
    def fetch_articles(self, query: str, days_back: int = 29) -> list[Article]:
        """Busca artigos por query."""
        pass
