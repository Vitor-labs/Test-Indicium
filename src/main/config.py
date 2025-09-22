# config.py
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # opcional
    DATABASE_PATH = os.getenv("DATABASE_PATH", "srag_data.db")

    # Parâmetros do relatório
    DAYS_FOR_DAILY_CHART = 30
    MONTHS_FOR_MONTHLY_CHART = 12
