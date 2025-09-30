# scripts/debug_vector_store.py
"""Script para debug do vector store."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from src.domain.entities.document import Article
from src.infrastructure.vector_store.qdrant_repository import QdrantVectorRepository

if __name__ == "__main__":
    """Debug do repositório de vetores."""
    print("🔧 Debug - Vector Store (Qdrant)")
    print("=" * 50)

    try:
        repo = QdrantVectorRepository()

        print("📝 Adicionando artigo de teste...")
        repo.add_documents(
            [
                Article(
                    id="test_001",
                    title="Test Article",
                    content="This is a test article about COVID-19",
                    description="Test description",
                    url="https://test.com",
                    published_date=datetime.now(),
                    source_name="Test Source",
                )
            ]
        )
        # Teste de busca
        print("🔍 Testando busca...")
        results = repo.search_similar("COVID-19", limit=3)
        print(f"📊 Resultados encontrados: {len(results)}")

        for i, article in enumerate(results):
            print(f"  {i + 1}. {article.title[:50]}...")

        print("✅ Debug do vector store concluído!")

    except Exception as e:
        print(f"❌ Erro no debug do vector store: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
