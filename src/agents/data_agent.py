# agents/database_agent.py
import sqlite3
from datetime import datetime
from typing import Dict

import pandas as pd
import plotly.express as px


class SRAGDatabaseAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def calculate_case_increase_rate(self, days: int = 7) -> Dict:
        """Calcula a taxa de aumento de casos"""
        query = """
        SELECT DATE(DT_NOTIFIC) as data_notificacao, COUNT(*) as casos
        FROM srag_data 
        WHERE DT_NOTIFIC >= date('now', '-{} days')
        GROUP BY DATE(DT_NOTIFIC)
        ORDER BY data_notificacao
        """.format(days * 2)  # Pega o dobro para comparar períodos

        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        if len(df) < days:
            return {"taxa_aumento": 0, "explicacao": "Dados insuficientes"}

        # Divide em dois períodos
        meio = len(df) // 2
        periodo_anterior = df.iloc[:meio]["casos"].sum()
        periodo_atual = df.iloc[meio:]["casos"].sum()

        if periodo_anterior == 0:
            taxa = 100 if periodo_atual > 0 else 0
        else:
            taxa = ((periodo_atual - periodo_anterior) / periodo_anterior) * 100

        return {
            "taxa_aumento": round(taxa, 2),
            "casos_periodo_anterior": periodo_anterior,
            "casos_periodo_atual": periodo_atual,
            "explicacao": f"Comparação entre os últimos {days} dias vs {days} dias anteriores",
        }

    def calculate_mortality_rate(self) -> Dict:
        """Calcula a taxa de mortalidade"""
        query = """
        SELECT 
            COUNT(*) as total_casos,
            SUM(CASE WHEN EVOLUCAO = 2 THEN 1 ELSE 0 END) as obitos
        FROM srag_data 
        WHERE DT_NOTIFIC >= date('now', '-30 days')
        """

        with self.get_connection() as conn:
            result = pd.read_sql_query(query, conn).iloc[0]

        total_casos = result["total_casos"]
        obitos = result["obitos"]

        if total_casos == 0:
            taxa = 0
        else:
            taxa = (obitos / total_casos) * 100

        return {
            "taxa_mortalidade": round(taxa, 2),
            "total_casos": total_casos,
            "total_obitos": obitos,
            "explicacao": "Taxa baseada nos últimos 30 dias",
        }

    def calculate_icu_occupancy_rate(self) -> Dict:
        """Calcula a taxa de ocupação de UTI"""
        query = """
        SELECT 
            COUNT(*) as total_hospitalizados,
            SUM(CASE WHEN UTI = 1 THEN 1 ELSE 0 END) as uti_casos
        FROM srag_data 
        WHERE HOSPITAL = 1 
        AND DT_NOTIFIC >= date('now', '-30 days')
        """

        with self.get_connection() as conn:
            result = pd.read_sql_query(query, conn).iloc[0]

        total_hospitalizados = result["total_hospitalizados"]
        uti_casos = result["uti_casos"]

        if total_hospitalizados == 0:
            taxa = 0
        else:
            taxa = (uti_casos / total_hospitalizados) * 100

        return {
            "taxa_ocupacao_uti": round(taxa, 2),
            "total_hospitalizados": total_hospitalizados,
            "casos_uti": uti_casos,
            "explicacao": "Proporção de casos hospitalizados que precisaram de UTI (últimos 30 dias)",
        }

    def calculate_vaccination_rate(self) -> Dict:
        """Calcula a taxa de vacinação"""
        query_vacinados = """
        SELECT COUNT(DISTINCT NU_NOTIFIC) as vacinados
        FROM srag_data 
        WHERE VACINA_COV = 1
        AND DT_NOTIFIC >= date('now', '-30 days')
        """

        query_total = """
        SELECT COUNT(DISTINCT NU_NOTIFIC) as total
        FROM srag_data 
        WHERE DT_NOTIFIC >= date('now', '-30 days')
        """

        with self.get_connection() as conn:
            vacinados = pd.read_sql_query(query_vacinados, conn).iloc[0]["vacinados"]
            total = pd.read_sql_query(query_total, conn).iloc[0]["total"]

        if total == 0:
            taxa = 0
        else:
            taxa = (vacinados / total) * 100

        return {
            "taxa_vacinacao": round(taxa, 2),
            "total_vacinados": vacinados,
            "total_casos": total,
            "explicacao": "Proporção de casos que possuíam vacinação (últimos 30 dias)",
        }

    def generate_daily_cases_chart(self, days: int = 30) -> str:
        """Gera gráfico de casos diários dos últimos N dias"""
        query = """
        SELECT DATE(DT_NOTIFIC) as data, COUNT(*) as casos
        FROM srag_data 
        WHERE DT_NOTIFIC >= date('now', '-{} days')
        GROUP BY DATE(DT_NOTIFIC)
        ORDER BY data
        """.format(days)

        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        fig = px.line(
            df,
            x="data",
            y="casos",
            title=f"Casos Diários de SRAG - Últimos {days} dias",
            labels={"data": "Data", "casos": "Número de Casos"},
        )

        chart_path = f"daily_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        return chart_path

    def generate_monthly_cases_chart(self, months: int = 12) -> str:
        """Gera gráfico de casos mensais dos últimos N meses"""
        query = """
        SELECT 
            strftime('%Y-%m', DT_NOTIFIC) as mes,
            COUNT(*) as casos
        FROM srag_data 
        WHERE DT_NOTIFIC >= date('now', '-{} months')
        GROUP BY strftime('%Y-%m', DT_NOTIFIC)
        ORDER BY mes
        """.format(months)

        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn)

        fig = px.bar(
            df,
            x="mes",
            y="casos",
            title=f"Casos Mensais de SRAG - Últimos {months} meses",
            labels={"mes": "Mês", "casos": "Número de Casos"},
        )

        chart_path = f"monthly_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        return chart_path

    def get_all_metrics(self) -> Dict:
        """Retorna todas as métricas calculadas"""
        return {
            "taxa_aumento_casos": self.calculate_case_increase_rate(),
            "taxa_mortalidade": self.calculate_mortality_rate(),
            "taxa_ocupacao_uti": self.calculate_icu_occupancy_rate(),
            "taxa_vacinacao": self.calculate_vaccination_rate(),
            "graficos": {
                "casos_diarios": self.generate_daily_cases_chart(),
                "casos_mensais": self.generate_monthly_cases_chart(),
            },
        }
