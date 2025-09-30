# scripts/run_news_pipeline.py
"""Script para executar apenas o pipeline de notícias."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.cli.main import SARSCoVAnalysisSystem

if __name__ == "__main__":
    """Executa apenas o pipeline de notícias."""
    try:
        system = SARSCoVAnalysisSystem()
        system.setup_news_pipeline()
        print("✅ Pipeline de notícias executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no pipeline de notícias: {e}")
        sys.exit(1)
