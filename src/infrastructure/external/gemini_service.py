# src/infrastructure/external_apis/gemini_service.py
import os

from google.generativeai.client import configure
from google.generativeai.embedding import embed_content
from google.generativeai.generative_models import GenerativeModel

from domain.services.llm_service import LLMService


class GeminiLLMService(LLMService):
    """Implementação do serviço LLM usando Google Gemini."""

    def __init__(
        self,
        embedding_model: str = "models/embedding-001",
        chat_model: str = "gemini-2.5-flash",
    ) -> None:
        """
        Inicializa serviço Gemini.

        Args:
            embedding_model: Modelo para embeddings
            chat_model: Modelo para chat/texto
        """
        if not (api_key := os.getenv("GOOGLE_API_KEY")):
            raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

        configure(api_key=api_key)
        self.embedding_model = embedding_model
        self.chat_model = chat_model

    def natural_to_sql(self, question: str, schema_info: dict[str, str]) -> str:
        """Converte linguagem natural para SQL."""
        return self._generate_text(f"""You are a SQL query generator for SQLite.

		Schema of the 'srag_cases' table:
        {"\n".join([f"- {col}: {dtype}" for col, dtype in schema_info.items()])}

        Translate this question into valid SQL:
		{question}

		Return only the SQL query, without explanations.
        """)

    def summarize_results(self, question: str, results: list[tuple[str]]) -> str:
        """Sumariza resultados de query."""
        return self._generate_text(f"""
        Question: {question}

		Results (list of tuples): {repr(results)}

		Write a short paragraph explaining what this data shows.
        """)

    def generate_final_answer(
        self, question: str, sql: str, summary: str, articles: list[str]
    ) -> str:
        """Gera resposta final baseada em todos os dados."""
        return self._generate_text(f"""
        You are an agent who answers questions based on tabular data and related news.

		Question: {question}

		Generated SQL: {sql}

		Data summary: {summary}

		Related news:
        {"\n".join([f"- {article}" for article in articles])}

        Provide a complete and well-structured answer.
        """)

    def generate_embedding(self, text: str) -> list[float]:
        """Gera embedding para texto."""
        return embed_content(model=self.embedding_model, content=text)["embedding"]

    def _generate_text(self, prompt: str) -> str:
        """Gera texto usando o modelo Gemini."""
        return str(
            GenerativeModel(self.chat_model).generate_content(prompt).text.strip()
        )
