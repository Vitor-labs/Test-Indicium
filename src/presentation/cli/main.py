# src/presentation/cli/enhanced_main.py
from dotenv import load_dotenv

from application.use_cases.data_processing_use_case import DataProcessingUseCase
from application.use_cases.enhanced_ai_query_use_case import EnhancedAIQueryUseCase
from application.use_cases.news_collection_use_case import NewsCollectionUseCase
from domain.entities.document import DataProcessingConfig
from infrastructure.database.file_repository import FileDataRepository
from infrastructure.external.news_api_repository import NewsAPIRepository
from infrastructure.langchain.langchain_agent_service import LangChainAgentService
from infrastructure.langchain.langchain_chain_service import LangChainChainService
from infrastructure.langchain.langchain_llm_service import LangChainLLMService
from infrastructure.vector_store.qdrant_repository import QdrantVectorRepository
from utils.data import COLUMN_TYPE_MATCHING, MIXED_TYPE_COLUMNS


class SARSCoVAnalysisSystem:
    """
    Sistema aprimorado com LangChain para análise SARS-CoV.

    Melhorias com LangChain:
    - Agentes inteligentes que decidem automaticamente o workflow
    - Memory entre interações para contexto contínuo
    - Chains especializadas para tarefas complexas
    - Output parsers para estruturação automática
    - Error handling e retry logic integrados
    """

    def __init__(self) -> None:
        """Inicializa sistema aprimorado com LangChain."""
        load_dotenv()

        # Repositórios (mantidos da versão anterior)
        self.data_repository = FileDataRepository("../data/interim/srag_2019_2024.db")
        self.news_repository = NewsAPIRepository()
        self.vector_repository = QdrantVectorRepository()

        # Serviços LangChain (NOVA IMPLEMENTAÇÃO)
        self.llm_service = LangChainLLMService()
        self.chain_service = LangChainChainService(self.llm_service)
        self.agent_service = LangChainAgentService(
            self.llm_service,
            self.data_repository,
            self.vector_repository,
            "../data/interim/srag_2019_2024.db",
        )
        # Casos de uso
        self.data_processing = DataProcessingUseCase(self.data_repository)
        self.news_collection = NewsCollectionUseCase(
            self.news_repository, self.vector_repository
        )
        # Schema info (seria carregado do dicionário de dados)
        self.schema_info = COLUMN_TYPE_MATCHING
        self.enhanced_ai_query = EnhancedAIQueryUseCase(
            self.agent_service, self.chain_service
        )

    def interactive_agent_mode(self) -> None:
        """
        Modo interativo aprimorado com agente inteligente.

        Vantagens:
        - Agente lembra contexto entre perguntas
        - Decisões automáticas sobre qual ferramenta usar
        - Análise epidemiológica especializada
        - Integração automática de dados e notícias
        """
        print("=== Modo Agente Inteligente ===")
        print("O agente tem acesso a:")
        print("• Banco de dados SRAG (2019-2024)")
        print("• Base de notícias relacionadas")
        print("• Ferramentas de análise epidemiológica")
        print("• Contexto temporal e histórico")
        print("\nDigite 'quit' para sair, 'history' para ver histórico")

        while True:
            question = input("\n🤖 Sua pergunta: ").strip()

            if question.lower() in ["quit", "sair", "exit"]:
                break

            if question.lower() in ["history", "historico"]:
                print(f"\n📊 {self.enhanced_ai_query.get_conversation_summary()}")
                continue

            if not question:
                continue

            print("\n🔍 Agente processando...")
            try:
                # Usar agente inteligente (padrão)
                answer = self.enhanced_ai_query.ask_question(question, use_agent=True)
                print(f"\n✅ Resposta:\n{answer}")
            except Exception as e:
                print(f"\n❌ Erro: {e}")

    def compare_approaches_mode(self) -> None:
        """
        Modo para comparar agente vs chains manuais.

        Útil para entender quando usar cada abordagem.
        """
        print("=== Comparação: Agente vs Chains Manuais ===")

        while True:
            question = input("\n📝 Pergunta para comparar: ").strip()

            if question.lower() in ["quit", "sair"]:
                break

            if not question:
                continue

            print("\n🤖 Processando com AGENTE...")
            try:
                agent_answer = self.enhanced_ai_query.ask_question(
                    question, use_agent=True
                )
                print(f"Resposta do Agente:\n{agent_answer}")
            except Exception as e:
                print(f"Erro no agente: {e}")

            print("\n⚙️ Processando com CHAINS manuais...")
            try:
                manual_answer = self.enhanced_ai_query.ask_question(
                    question, use_agent=False
                )
                print(f"Resposta Manual:\n{manual_answer}")
            except Exception as e:
                print(f"Erro nas chains: {e}")

            print("\n" + "=" * 80)

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
                print(f"\nResposta:\n{self.enhanced_ai_query.ask_question(question)}")
            except Exception as e:
                print(f"Erro ao processar pergunta: {e}")
