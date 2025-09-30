# src/infrastructure/external_apis/news_api_repository.py
import os
from datetime import datetime, timedelta

from httpx import HTTPStatusError, get

from domain.entities.document import Article
from domain.repositories.news_repository import NewsRepository


class NewsAPIRepository(NewsRepository):
    """Implementação da News API para repositório de notícias."""

    def __init__(self) -> None:
        """Inicializa repositório da News API."""
        self.base_url = "https://newsapi.org/v2/everything"
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NEWS_API_KEY não encontrada nas variáveis de ambiente")

    def fetch_articles(self, query: str, days_back: int = 29) -> list[Article]:
        """
        Busca artigos da News API.

        Args:
            query: Termo de busca
            days_back: Número de dias para buscar (máximo 29)

        Returns:
            Lista de artigos encontrados
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(days=min(days_back, 29))

        try:
            response = get(
                self.base_url,
                params={
                    "q": query,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "sortBy": "relevancy",
                    "apiKey": self.api_key,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data["status"] != "ok":
                raise Exception(f"API Error: {data.get('message', 'Unknown error')}")

            return self._convert_to_articles(data["articles"])

        except HTTPStatusError as e:
            raise Exception(f"Request failed: {e}")

    def _convert_to_articles(self, raw_articles: list[dict[str, str]]) -> list[Article]:
        """Converte dados brutos da API para entidades Article."""
        articles = []
        for article in raw_articles:
            if not article.get("content") or article["content"] == "[Removed]":
                continue

            published_date = None
            if date_str := article.get("publishedAt"):
                try:
                    published_date = datetime.fromisoformat(
                        date_str.replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            articles.append(
                Article(
                    id=f"news_{hash(article['url'])}",
                    title=article.get("title", ""),
                    content=article.get("content", ""),
                    description=article.get("description", ""),
                    url=article.get("url", ""),
                    published_date=published_date,
                    source_name=article.get("source", {}).get("name", ""),
                    image_url=article.get("urlToImage", ""),
                )
            )
        return articles
