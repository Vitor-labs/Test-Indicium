# src/infrastructure/vector_store/qdrant_repository.py
import uuid
from datetime import datetime
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from domain.entities.document import Article
from domain.repositories.vector_repository import VectorRepository


class QdrantVectorRepository(VectorRepository):
    """Implementação Qdrant do repositório de vetores."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "sars_cov_news",
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        """
        Inicializa repositório Qdrant.

        Args:
                url: URL do servidor Qdrant
                collection_name: Nome da coleção
                embedding_model: Modelo para embeddings
        """
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = self.encoder.get_sentence_embedding_dimension() or 384
        self._create_collection()

    def _create_collection(self) -> None:
        """Cria coleção Qdrant se não existir."""
        try:
            if self.collection_name not in [
                col.name for col in self.client.get_collections().collections
            ]:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size, distance=Distance.COSINE
                    ),
                )
                print(f"Coleção criada: {self.collection_name}")
            else:
                print(f"Coleção {self.collection_name} já existe")
        except Exception as e:
            raise Exception(f"Erro ao criar coleção: {e}")

    def add_documents(self, articles: list[Article]) -> None:
        """Adiciona documentos ao repositório de vetores."""
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=self.encoder.encode(
                    f"{article.title} {article.description} {article.content}".strip()
                ).tolist(),
                payload={
                    "article_id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "description": article.description,
                    "url": article.url,
                    "source_name": article.source_name,
                    "published_date": article.published_date.isoformat()
                    if article.published_date
                    else None,
                    "image_url": article.image_url,
                },
            )
            for article in articles
        ]
        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Adicionados {len(points)} documentos ao Qdrant")
        except Exception as e:
            raise Exception(f"Erro ao adicionar documentos: {e}")

    def search_similar(self, query: str, limit: int = 5) -> list[Article]:
        """Busca documentos similares."""
        try:
            articles = []
            for result in self.client.search(
                collection_name=self.collection_name,
                query_vector=self.encoder.encode(query).tolist(),
                limit=limit,
            ):  # empty dict if payload is None
                payload: dict[str, Any] = result.payload or {}

                published_date = None
                if payload.get("published_date"):
                    published_date = (
                        datetime.fromisoformat(payload["published_date"]) or None
                    )
                articles.append(
                    Article(
                        id=payload["article_id"],
                        title=payload["title"],
                        content=payload["content"],
                        description=payload["description"],
                        url=payload["url"],
                        source_name=payload["source_name"],
                        published_date=published_date,
                        image_url=payload["image_url"],
                    )
                )
            return articles

        except Exception as e:
            raise Exception(f"Erro na busca: {e}")
