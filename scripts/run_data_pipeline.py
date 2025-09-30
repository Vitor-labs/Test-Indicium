# scripts/run_data_pipeline.py
"""Script para executar apenas o pipeline de dados."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.cli.main import SARSCoVAnalysisSystem

if __name__ == "__main__":
    try:
        system = SARSCoVAnalysisSystem()
        system.setup_data_pipeline()
        print("✅ Pipeline de dados executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no pipeline de dados: {e}")
        sys.exit(1)
