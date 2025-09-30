# scripts/debug_llm.py
"""Script para debug do serviço LLM."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.external.gemini_service import GeminiLLMService

if __name__ == "__main__":
    """Debug do serviço LLM."""
    print("🔧 Debug - Serviço LLM (Gemini)")
    print("=" * 50)

    try:
        llm = GeminiLLMService()
        print("🧠 Testando geração de embedding...")
        print(
            f"📊 Dimensão do embedding: {len(llm.generate_embedding('This is a test'))}"
        )
        print("🔄 Testando conversão NL para SQL...")
        print(
            f"📝 SQL gerado: {
                llm.natural_to_sql(
                    'How many records are there?',
                    {'test_table': 'string', 'count': 'integer'},
                )
            }"
        )
        print("📋 Testando sumarização...")
        values = [("100",), ("200",), ("300",)]
        print(f"📄 Resumo: {llm.summarize_results('Test question', values)[:100]}...")
        print("✅ Debug do LLM concluído!")

    except Exception as e:
        print(f"❌ Erro no debug do LLM: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
