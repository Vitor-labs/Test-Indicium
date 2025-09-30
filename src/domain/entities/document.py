# src/domain/entities/document.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    """Representa um artigo de notícias."""

    id: str
    title: str
    content: str
    url: str
    published_date: datetime | None
    source_name: str
    description: str = ""
    image_url: str = ""


@dataclass
class QueryResult:
    """Resultado de uma consulta SQL."""

    data: list[tuple[str | float]]
    summary: str
    related_articles: list[Article]


@dataclass
class DataProcessingConfig:
    """Configuração para processamento de dados."""

    mixed_type_columns: list[int]
    date_format: str = "%d/%m/%Y"
    encoding: str = "latin1"
    separator: str = ";"
