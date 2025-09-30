# src/domain/repositories/data_repository.py
from abc import ABC, abstractmethod

from pandas import DataFrame


class DataRepository(ABC):
    """Interface para repositório de dados."""

    @abstractmethod
    def save_csv(self, df: DataFrame, path: str) -> None:
        """Salva DataFrame como CSV."""
        pass

    @abstractmethod
    def save_parquet(self, df: DataFrame, path: str) -> None:
        """Salva DataFrame como Parquet."""
        pass

    @abstractmethod
    def save_to_database(self, df: DataFrame, table_name: str) -> None:
        """Salva DataFrame no banco de dados."""
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> list[tuple[str]]:
        """Executa query SQL e retorna resultados."""
        pass
