# src/infrastructure/langchain/langchain_chain_service.py
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from domain.services.chain_service import ChainService
from infrastructure.langchain.langchain_llm_service import LangChainLLMService


class LangChainChainService(ChainService):
    """
    Implementation of complex chains using LangChain.

    Advantages:
    - Sequential chains for multi-step workflows
    - Integrated memory for context
    - Declarative composition of pipelines
    """

    def __init__(self, llm_service: LangChainLLMService) -> None:
        """
        Initialize chain service.

        Args:
            llm_service: LangChain LLM service
        """
        self.llm = llm_service.llm
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history", return_messages=True
        )
        self._setup_chains()

    def _setup_chains(self) -> None:
        """Configure specialized chains."""

        # SQL Validation Chain - renamed to avoid conflicts
        self._sql_validation_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are a SQL expert focused on query optimization and security.
					Validate and improve SQL queries for epidemiological analysis.

					Check for:
					1. Correct syntax
					2. Performance optimization
					3. Security (SQL injection prevention)
					4. Relevance for epidemiological analysis
					5. Proper use of indexes and aggregations

					Return ONLY the corrected SQL query, no extra text.
					"""
                ),
                HumanMessage(
                    content="""
					SQL Query to validate: {sql_query}

					Database Schema: {schema_info}

					Original Question: {original_question}

					Corrected SQL query:
					"""
                ),
            ]
        )
        # Using new Runnable pattern - returns string directly
        self._sql_validation_runnable = (
            self._sql_validation_prompt | self.llm | StrOutputParser()
        )
        # Multi-step Analysis Chain
        self._analysis_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are an epidemiologist analyzing SRAG surveillance data.
					Provide statistical analysis of the provided data.
					Focus on key patterns and distributions.
					"""
                ),
                HumanMessage(
                    content="""
					Question: {question}
					Data Sample: {data}

					Statistical analysis:
					"""
                ),
            ]
        )
        self._analysis_runnable = self._analysis_prompt | self.llm | StrOutputParser()
        self._insights_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are a public health expert extracting actionable insights. Based
                    on the statistical analysis, identify key epidemiological insights.
					Provide exactly 3-5 bullet points.
					"""
                ),
                HumanMessage(
                    content="""
					Original Question: {question}
					Statistical Analysis: {analysis}

					Key epidemiological insights:
					"""
                ),
            ]
        )
        self._insights_runnable = self._insights_prompt | self.llm | StrOutputParser()
        # RAG Enhancement Chain with Memory - renamed to avoid conflicts
        self._rag_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					You are a health informatics specialist combining multiple data sources.
					Use conversation history to provide contextually relevant responses.

					Always consider:
					- Previous discussion context
					- Current epidemiological data
					- Recent news and trends
					- Continuity of analysis
					"""
                ),
                HumanMessage(
                    content="""
					Conversation History:
					{chat_history}

					Current Question: {question}

					Relevant Context:
					{context}

					Comprehensive response:
					"""
                ),
            ]
        )
        self._rag_runnable = (
            RunnablePassthrough.assign(
                chat_history=lambda _: self._format_chat_history()
            )
            | self._rag_prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_chat_history(self) -> str:
        """Format chat history for prompt inclusion."""
        if not self.memory.chat_memory.messages:
            return "No previous conversation."

        # Last 6 messages
        return "\n".join(
            [
                f"{'Human' if message.type == 'human' else 'Assistant'}: {
                    str(message.content[:200]) + '...'
                    if len(message.content) > 200
                    else message.content
                }"
                for message in self.memory.chat_memory.messages[-6:]
            ]
        )

    def sql_chain(self, question: str, schema_info: dict[str, str]) -> str:
        """Specialized chain for SQL generation and validation."""
        schema_text = "\n".join(
            [f"{col}: {dtype}" for col, dtype in schema_info.items()]
        )
        initial_sql_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
					Generate optimized SQL for epidemiological analysis.
					Return ONLY the SQL query, no explanations.
					Use table name 'srag_cases'.
					"""
                ),
                HumanMessage(
                    content="Question: {question}\nSchema: {schema_info}\n\nSQL query:"
                ),
            ]
        )
        initial_runnable = initial_sql_prompt | self.llm | StrOutputParser()
        try:
            return self._sql_validation_runnable.invoke(
                {
                    "sql_query": initial_runnable.invoke(
                        {
                            "question": question,
                            "schema_info": schema_text,
                        }
                    ),
                    "schema_info": schema_text,
                    "original_question": question,
                }
            ).strip()

        except Exception as e:
            print(f"Error in SQL chain: {e}")
            return f"SELECT * FROM srag_cases WHERE 1=1 LIMIT 100; -- Error: {e}"

    def summarization_chain(self, question: str, data: list[tuple]) -> str:
        """Chain for summarization with specialized epidemiological analysis."""

        if not data:
            return "No data available for analysis."

        # Prepare data sample to avoid token limits
        data_sample = str(data[:10])  # First 10 rows
        try:
            # Step 1: Statistical analysis
            analysis_result = self._analysis_runnable.invoke(
                {
                    "question": question,
                    "data": data_sample,
                }
            )
            # Step 2: Extract insights
            insights_result = self._insights_runnable.invoke(
                {
                    "question": question,
                    "analysis": analysis_result,
                }
            )
            return (
                f"Statistical Analysis:\n{analysis_result}\n\n"
                f"Key Insights:\n{insights_result}"
            )

        except Exception as e:
            print(f"Error in summarization chain: {e}")
            return f"Found {len(data)} records. Sample: {data_sample[:200]}..."

    def rag_chain(self, question: str, context: str) -> str:
        """RAG chain with memory for conversation continuity."""
        try:
            result = self._rag_runnable.invoke(
                {
                    "question": question,
                    "context": context,
                }
            )  # Add to memory
            self.memory.save_context({"input": question}, {"output": result})
            return result

        except Exception as e:
            print(f"Error in RAG chain: {e}")
            return f"Question: {question}\nContext: {context}\nError: {e}"
