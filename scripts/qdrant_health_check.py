# scripts/qdrant_health_check.py
"""Script para verificar saúde do Qdrant."""

import os
import sys
import time
from datetime import datetime

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_qdrant_health(
    url: str = "http://localhost:6333", max_attempts: int = 30
) -> bool:
    """
    Verifica se o Qdrant está saudável.

    Args:
        url: URL do Qdrant
        max_attempts: Número máximo de tentativas

    Returns:
        True se saudável, False caso contrário
    """
    print(f"🏥 Verificando saúde do Qdrant em {url}...")

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Qdrant está saudável! (tentativa {attempt}/{max_attempts})")
                return True
        except requests.exceptions.RequestException:
            pass

        print(f"⏳ Tentativa {attempt}/{max_attempts} - aguardando...")
        time.sleep(2)

    print(f"❌ Qdrant não respondeu após {max_attempts} tentativas")
    return False


def get_qdrant_info(
    url: str = "http://localhost:6333",
) -> dict[str, str | list[str]]:
    """Obtém informações do Qdrant."""
    try:
        response = requests.get(f"{url}/collections", timeout=5)
        response.raise_for_status()
        if response.status_code == 200:
            collections = response.json()
            return {
                "status": "healthy",
                "collections": collections.get("result", {}).get("collections", []),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "status": "unhealthy",
                "error": f"Status code: {response.status_code}",
                "timestamp": datetime.now().isoformat(),
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def main() -> None:
    """Função principal do health check."""
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        info = get_qdrant_info()
        print("📊 Informações do Qdrant:")
        print(f"  Status: {info['status']}")
        if info["status"] == "healthy":
            print(f"  Coleções: {len(info['collections'])}")
            for collection in info["collections"]:
                print(f"    - {collection.get('name', 'N/A')}")  # type: ignore
        else:
            print(f"  Erro: {info.get('error', 'N/A')}")
        return

    if check_qdrant_health():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
