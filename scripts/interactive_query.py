# scripts/interactive_query.py
"""Script para executar apenas o modo de consulta interativa."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.cli.main import SARSCoVAnalysisSystem

if __name__ == "__main__":
    """Executa apenas o modo interativo."""
    try:
        system = SARSCoVAnalysisSystem()
        system.interactive_query_mode()
    except Exception as e:
        print(f"❌ Erro no modo interativo: {e}")
        sys.exit(1)
