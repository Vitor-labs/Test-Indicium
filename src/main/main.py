# main.py
import json
from datetime import datetime

from config import Config

from agents.data_agent import SRAGDatabaseAgent
from agents.news_agent import SRAGNewsAgent
from agents.report_agent import SRAGReportAgent


def main():
    # Inicializa os agentes
    db_agent = SRAGDatabaseAgent(Config.DATABASE_PATH)
    news_agent = SRAGNewsAgent(Config.NEWS_API_KEY)
    report_agent = SRAGReportAgent(db_agent, news_agent, Config.OPENAI_API_KEY)

    print("🔄 Gerando relatório de SRAG...")

    # Gera o relatório
    report = report_agent.generate_report()

    # Salva o relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorio_srag_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ Relatório salvo em: {filename}")

    # Exibe resumo
    if "erro" not in report:
        print("\n📊 RESUMO DAS MÉTRICAS:")
        metrics = report["metricas_detalhadas"]
        print(
            f"Taxa de aumento de casos: {metrics['taxa_aumento_casos']['taxa_aumento']}%"
        )
        print(
            f"Taxa de mortalidade: {metrics['taxa_mortalidade']['taxa_mortalidade']}%"
        )
        print(
            f"Taxa de ocupação UTI: {metrics['taxa_ocupacao_uti']['taxa_ocupacao_uti']}%"
        )
        print(f"Taxa de vacinação: {metrics['taxa_vacinacao']['taxa_vacinacao']}%")

        print("\n📈 Gráficos gerados:")
        print(f"- Casos diários: {metrics['graficos']['casos_diarios']}")
        print(f"- Casos mensais: {metrics['graficos']['casos_mensais']}")

        print(f"\n📰 Notícias encontradas: {len(report['noticias_relacionadas'])}")
    else:
        print(f"❌ {report['erro']}")


if __name__ == "__main__":
    main()
