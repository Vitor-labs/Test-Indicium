# src/infrastructure/database/sqlite_repository.py
import sqlite3

from pandas import DataFrame
from sqlalchemy.types import TIMESTAMP

from domain.repositories.data_repository import DataRepository


class SQLiteDataRepository(DataRepository):
    """Implementação SQLite do repositório de dados."""

    def __init__(self, db_path: str) -> None:
        """
        Inicializa repositório SQLite.

        Args:
            db_path: Caminho para o arquivo do banco SQLite
        """
        self.db_path = db_path

    def save_csv(self, df: DataFrame, path: str) -> None:
        """Salva DataFrame como CSV."""
        df.to_csv(path, index=False, date_format="%Y-%m-%d")

    def save_parquet(self, df: DataFrame, path: str) -> None:
        """Salva DataFrame como Parquet."""
        df.to_parquet(path, index=False, compression="snappy")

    def save_to_database(self, df: DataFrame, table_name: str) -> None:
        """Salva DataFrame no banco SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False,
                dtype={
                    col: TIMESTAMP
                    for col, dtype in df.dtypes.items()
                    if dtype == "datetime64[ns]"
                },
            )

    def execute_query(self, sql: str) -> list[tuple[str]]:
        """Executa query SQL e retorna resultados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
