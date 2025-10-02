# src/infrastructure/langchain/langchain_llm_service.py
import os

from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field, SecretStr

from domain.services.llm_service import LLMService
from utils.data import LLM_READY_SCHEMA


class SQLQuery(BaseModel):
    """Structured model for SQL query generation."""

    query: str = Field(description="Valid SQL query")
    explanation: str = Field(description="Explanation of the generated query")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the query (0-1)"
    )


class DataSummary(BaseModel):
    """Structured model for data summarization."""

    summary: str = Field(description="Summary of the data")
    key_insights: list[str] = Field(description="Key insights extracted")
    data_quality: str = Field(description="Assessment of data quality")
    record_count: int = Field(description="Number of records analyzed")


class LangChainLLMService(LLMService):
    """
    LangChain implementation of LLM service with structured templates.

    Advantages over direct implementation:
    - Reusable and versionable prompt templates
    - Automatic output parsers for structuring
    - Integrated retry logic and error handling
    - Composable chains for complex workflows
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> None:
        """
        Initialize LangChain LLM service.

        Args:
            model_name: Gemini model name
            temperature: Creativity control (0-1)
            max_tokens: Maximum tokens in response
        """
        if not (api_key := os.getenv("GOOGLE_API_KEY")):
            raise ValueError("GOOGLE_API_KEY environment variable not found")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=SecretStr(api_key),
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", google_api_key=SecretStr(api_key)
        )
        self._setup_chains()

    def _setup_chains(self) -> None:
        """Configure LangChain chains with structured templates."""
        # SQL Generation Chain
        sql_parser = PydanticOutputParser(pydantic_object=SQLQuery)
        self.sql_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=f"""
					You are an expert SQL analyst for epidemiological data analysis.
					Always generate valid and optimized SQLite queries.

                    {LLM_READY_SCHEMA}

					Important rules:
					- Use only the 'srag_cases' table
					- Prefer aggregations when appropriate
					- Use LIMIT for exploratory queries
					- Consider relevant temporal filters
					- Focus on epidemiologically meaningful patterns

					The database 'srag_cases' contains SRAG (Severe Acute Respiratory
                    Syndrome) surveillance data from Brazil (2019-2024).
					"""
                ),
                HumanMessage(
                    content="""
                    Table Name 'srag_cases'

					Table schema 'srag_cases':
					{schema_info}

					Question:
                    {question}

					{format_instructions}
					"""
                ),
            ]
        )
        self.sql_chain = (
            RunnablePassthrough.assign(
                format_instructions=lambda _: sql_parser.get_format_instructions()
            )
            | self.sql_prompt
            | self.llm
            | OutputFixingParser.from_llm(parser=sql_parser, llm=self.llm)
        )
        # Data Summarization Chain
        summary_parser = PydanticOutputParser(pydantic_object=DataSummary)
        self.summary_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are an epidemiologist specialized in SRAG data analysis.
					Analyze the provided data and extract meaningful insights.

					Focus on:
					- Temporal trends
					- Geographic distributions
					- Risk groups
					- Epidemiological patterns
					- Public health implications
					"""
                ),
                HumanMessage(
                    content="""
					Original question: {question}

					Data sample (first rows): {data_sample}

					Total records: {total_records}

					{format_instructions}
					"""
                ),
            ]
        )
        self.summary_chain = (
            RunnablePassthrough.assign(
                format_instructions=lambda _: summary_parser.get_format_instructions()
            )
            | self.summary_prompt
            | self.llm
            | OutputFixingParser.from_llm(parser=summary_parser, llm=self.llm)
        )
        # Final Answer Chain
        self.final_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are a public health assistant specialized in epidemiology.
					Combine epidemiological data with relevant news information.

					Structure your response:
					1. Executive Summary
					2. Data Analysis
					3. News Context
					4. Recommendations (if applicable)
					5. Limitations and caveats

					Be precise, evidence-based, and actionable.
					"""
                ),
                HumanMessage(
                    content="""
					Question: {question}

					Data Analysis:
					{data_summary}

					Related News:
					{news_context}

					Provide a comprehensive and well-structured response.
					"""
                ),
            ]
        )
        self.final_chain = self.final_prompt | self.llm | StrOutputParser()

    def natural_to_sql(self, question: str, schema_info: dict[str, str]) -> str:
        """
        Convert natural language to SQL using structured chain.

        Advantage: Output parser ensures correct format with automatic retry.
        """
        try:
            return str(
                self.sql_chain.invoke(
                    {
                        "question": question,
                        "schema_info": "\n".join(
                            [f"- {col}: {dtype}" for col, dtype in schema_info.items()]
                        ),
                    }
                ).query
            )
        except Exception as e:
            print(f"Error in SQL generation: {e}")
            # Fallback to simple query
            return "SELECT * FROM srag_cases WHERE 1=1 LIMIT 100;"

    def summarize_results(self, question: str, results: list[tuple[str]]) -> str:
        """
        Summarize results using structured chain.

        Advantage: Structured analysis with categorized insights.
        """
        if not results:
            return "No data found for the query."

        # Prepare data sample
        data_sample = str(results[:5])  # First 5 rows
        total_records = len(results)
        try:
            result = self.summary_chain.invoke(
                {
                    "question": question,
                    "data_sample": data_sample,
                    "total_records": total_records,
                }
            )
            return (
                f"{result.summary}\n\n"
                f"Key Insights:\n{
                    '\n'.join(  # Combine structured insights
                        [f'• {insight}' for insight in result.key_insights]
                    )
                }"
                f"\n\nData Quality: {result.data_quality}"
            )
        except Exception as e:
            print(f"Error in summarization: {e}")
            return f"Found {total_records} records. Sample data: {data_sample[:200]}..."

    def generate_final_answer(
        self, question: str, sql: str, summary: str, articles: list[str]
    ) -> str:
        """Generate final answer combining data and news."""
        news_context = "\n".join([f"• {article}" for article in articles])
        try:
            return self.final_chain.invoke(
                {
                    "question": question,
                    "data_summary": summary,
                    "news_context": news_context,
                }
            )
        except Exception as e:
            print(f"Error in final answer generation: {e}")
            return f"Question: {question}\n\nSummary: {summary}\n\nNews: {news_context}"

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding using LangChain."""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768  # Default embedding size fallback
