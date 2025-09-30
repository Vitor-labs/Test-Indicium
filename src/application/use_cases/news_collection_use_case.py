# src/application/use_cases/news_collection_use_case.py
from domain.repositories.news_repository import NewsRepository
from domain.repositories.vector_repository import VectorRepository


class NewsCollectionUseCase:
    """Caso de uso para coleta e indexação de notícias."""

    def __init__(
        self, news_repository: NewsRepository, vector_repository: VectorRepository
    ) -> None:
        """
        Inicializa caso de uso de coleta de notícias.

        Args:
            news_repository: Repositório de notícias
            vector_repository: Repositório de vetores
        """
        self.news_repository = news_repository
        self.vector_repository = vector_repository

    def collect_and_index_news(self, queries: list[str]) -> None:
        """
        Coleta e indexa notícias para uma lista de consultas.

        Args:
            queries: Lista de termos de busca
        """
        all_articles = []

        for query in queries:
            print(f"Coletando notícias para: {query}")
            articles = self.news_repository.fetch_articles(query)
            all_articles.extend(articles)
            print(f"Encontrados {len(articles)} artigos")

        if all_articles:
            print(f"Indexando {len(all_articles)} artigos no total...")
            self.vector_repository.add_documents(all_articles)
            print("Indexação concluída!")
        else:
            print("Nenhum artigo encontrado")
