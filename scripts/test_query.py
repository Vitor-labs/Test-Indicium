# scripts/test_query.py
"""Script para testar uma query específica."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.presentation.cli.main import SARSCoVAnalysisSystem

if __name__ == "__main__":
    """Testa uma query específica."""
    if len(sys.argv) < 2:
        question = "What was the month with more cases of SARS in 2019?"
        print(f"ℹ️  Usando pergunta padrão: {question}")
    else:
        question = " ".join(sys.argv[1:])
        print(f"🔍 Testando pergunta: {question}")

    try:
        system = SARSCoVAnalysisSystem()
        answer = system.ai_query.ask_question(question)
        print(f"\n📋 Resposta:\n{answer}")
        print("\n✅ Teste concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)
