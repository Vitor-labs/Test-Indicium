# src/presentation/cli/main.py
from dotenv import load_dotenv

from application.use_cases.ai_query_use_case import AIQueryUseCase
from application.use_cases.data_processing_use_case import DataProcessingUseCase
from application.use_cases.news_collection_use_case import NewsCollectionUseCase
from domain.entities.document import DataProcessingConfig
from infrastructure.database.file_repository import FileDataRepository
from infrastructure.external.gemini_service import GeminiLLMService
from infrastructure.external.news_api_repository import NewsAPIRepository
from infrastructure.vector_store.qdrant_repository import QdrantVectorRepository
from utils.data import COLUMN_TYPE_MATCHING, MIXED_TYPE_COLUMNS


class SARSCoVAnalysisSystem:
    """Sistema principal de análise SARS-CoV."""

    def __init__(self) -> None:
        """Inicializa sistema com todas as dependências."""
        load_dotenv()
        # Repositórios
        self.data_repository = FileDataRepository("./data/interim/srag_2019_2024.db")
        self.news_repository = NewsAPIRepository()
        self.vector_repository = QdrantVectorRepository()
        # Serviços
        self.llm_service = GeminiLLMService()
        # Casos de uso
        self.data_processing = DataProcessingUseCase(self.data_repository)
        self.news_collection = NewsCollectionUseCase(
            self.news_repository, self.vector_repository
        )
        # Schema info (seria carregado do dicionário de dados)
        self.schema_info = COLUMN_TYPE_MATCHING
        self.ai_query = AIQueryUseCase(
            self.data_repository,
            self.vector_repository,
            self.llm_service,
            self.schema_info,
        )

    def setup_data_pipeline(self) -> None:
        """Configura pipeline de dados inicial."""
        print("\n========= Configurando Pipeline de Dados =========")
        print("1. Processando dicionário de dados (vai levar uns 2 minutos)...")
        data_dict = self.data_processing.process_pdf_dictionary(
            "./docs/dicionario-de-dados-2019-a-2025.pdf"
        )
        self.data_repository.save_csv(data_dict, "./docs/data_dict.csv")
        print("2. Baixando dados SRAG...")
        srag_data = self.data_processing.download_and_process_srag_data(
            years=list(range(19, 25)),
            config=DataProcessingConfig(
                mixed_type_columns=MIXED_TYPE_COLUMNS, dtype_mapping=self.schema_info
            ),
        )
        print("3. Salvando dados...")
        self.data_repository.save_csv(srag_data, "./data/interim/srag_2019_2024.csv")
        self.data_repository.save_parquet(
            srag_data, "./data/interim/srag_2019_2024.parquet"
        )
        self.data_repository.save_to_database(srag_data, "srag_cases")
        print("Pipeline de dados configurado com sucesso!")

    def setup_news_pipeline(self) -> None:
        """Configura pipeline de notícias."""
        print("=== Configurando Pipeline de Notícias ===")
        self.news_collection.collect_and_index_news(
            ["covid", "sars", "flu", "influenza", "infectious", "viral"]
        )
        print("Pipeline de notícias configurado com sucesso!")

    def interactive_query_mode(self) -> None:
        """Modo interativo de consultas."""
        print("=== Modo Consulta Interativa ===")
        print("Digite 'quit' para sair")

        while True:
            if (question := input("\nSua pergunta: ").strip()).lower() in [
                "quit",
                "sair",
                "exit",
            ]:
                break

            if not question:
                continue

            try:
                print(f"\nResposta:\n{self.ai_query.ask_question(question)}")
            except Exception as e:
                print(f"Erro ao processar pergunta: {e}")
