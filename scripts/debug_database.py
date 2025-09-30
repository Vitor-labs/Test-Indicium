# scripts/debug_database.py
"""Script para debug do banco de dados."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database.file_repository import FileDataRepository

if __name__ == "__main__":
    """Debug do repositório de banco."""
    print("🔧 Debug - Repositório de Banco de Dados")
    print("=" * 50)

    try:
        repo = FileDataRepository("../data/interim/srag_2019_2024.db")

        # Teste simples de query
        result = repo.execute_query("SELECT COUNT(*) FROM srag_cases LIMIT 1")
        print(f"📊 Total de registros: {result[0][0] if result else 'N/A'}")

        # Teste de schema
        schema_result = repo.execute_query("PRAGMA table_info(srag_cases)")
        print(f"📋 Colunas encontradas: {len(schema_result)}")

        for col in schema_result[:5]:  # Primeiras 5 colunas
            print(f"  - {col[1]} ({col[2]})")  # type: ignore

        print("✅ Debug do banco concluído!")

    except Exception as e:
        print(f"❌ Erro no debug do banco: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
