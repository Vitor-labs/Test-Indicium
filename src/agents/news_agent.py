# agents/news_agent.py
from datetime import datetime, timedelta
from typing import Dict, List

import requests
from bs4 import BeautifulSoup


class SRAGNewsAgent:
    def __init__(self, news_api_key: str = None):
        self.news_api_key = news_api_key

    def get_news_from_api(
        self, query: str = "SRAG síndrome respiratória aguda grave", days: int = 7
    ) -> List[Dict]:
        """Busca notícias via NewsAPI"""
        if not self.news_api_key:
            return self.get_news_from_web_scraping(query)

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "pt",
            "sortBy": "publishedAt",
            "from": (datetime.now() - timedelta(days=days)).isoformat(),
            "apiKey": self.news_api_key,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            news_list = []
            for article in data.get("articles", [])[:10]:  # Limita a 10 notícias
                news_list.append(
                    {
                        "titulo": article["title"],
                        "descricao": article["description"],
                        "url": article["url"],
                        "data_publicacao": article["publishedAt"],
                        "fonte": article["source"]["name"],
                    }
                )
            return news_list
        except Exception as e:
            print(f"Erro ao buscar notícias via API: {e}")
            return self.get_news_from_web_scraping(query)

    def get_news_from_web_scraping(self, query: str) -> List[Dict]:
        """Busca notícias via web scraping (Google News)"""
        try:
            # Exemplo básico - você pode melhorar isso
            search_url = f"https://news.google.com/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # Esta é uma implementação simplificada
            # Em produção, você precisaria de um parser mais robusto
            news_list = []
            articles = soup.find_all("article")[:5]  # Primeiros 5 artigos

            for i, article in enumerate(articles):
                title_elem = article.find("h3") or article.find("h4")
                title = (
                    title_elem.get_text().strip() if title_elem else f"Notícia {i + 1}"
                )

                news_list.append(
                    {
                        "titulo": title,
                        "descricao": "Descrição não disponível via scraping",
                        "url": "#",
                        "data_publicacao": datetime.now().isoformat(),
                        "fonte": "Google News",
                    }
                )

            return news_list
        except Exception as e:
            print(f"Erro no web scraping: {e}")
            return [
                {
                    "titulo": "Notícias não disponíveis no momento",
                    "descricao": "Erro ao conectar com fontes de notícias",
                    "url": "#",
                    "data_publicacao": datetime.now().isoformat(),
                    "fonte": "Sistema",
                }
            ]

    def get_recent_news(self) -> List[Dict]:
        """Retorna notícias recentes sobre SRAG"""
        queries = [
            "SRAG síndrome respiratória aguda grave",
            "surto respiratório Brasil",
            "casos SRAG aumentando",
        ]

        all_news = []
        for query in queries:
            news = self.get_news_from_api(query)
            all_news.extend(news)

        # Remove duplicatas baseado no título
        seen_titles = set()
        unique_news = []
        for news in all_news:
            if news["titulo"] not in seen_titles:
                seen_titles.add(news["titulo"])
                unique_news.append(news)

        return unique_news[:10]  # Retorna as 10 mais relevantes
