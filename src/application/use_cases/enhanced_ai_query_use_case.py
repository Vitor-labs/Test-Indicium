# src/application/use_cases/enhanced_ai_query_use_case.py
from domain.entities.document import Article
from domain.repositories.data_repository import DataRepository
from domain.repositories.vector_repository import VectorRepository
from domain.services.agent_service import AgentService
from domain.services.chain_service import ChainService


class EnhancedAIQueryUseCase:
    """
    Enhanced use case with LangChain agents and chains.

    Advantages:
    - Automatic intelligent decisions
    - Memory between interactions
    - Simplified complex workflows
    - Robust error handling
    """

    def __init__(
        self,
        agent_service: AgentService,
        chain_service: ChainService,
        data_repository: DataRepository,
        vector_repository: VectorRepository,
        schema_info: dict[str, str],
    ) -> None:
        """
        Initialize enhanced use case.

        Args:
            agent_service: Agent service
            chain_service: Chain service
            data_repository: Data repository for SQL execution
            vector_repository: Vector repository for news search
            schema_info: Database schema information
        """
        self.agent_service = agent_service
        self.chain_service = chain_service
        self.data_repository = data_repository
        self.vector_repository = vector_repository
        self.schema_info = schema_info
        self.conversation_history: list[dict[str, str]] = []

    def ask_question(self, question: str, use_agent: bool = True) -> str:
        """
        Process question with option to use agent or simple chains.

        Args:
            question: Question in natural language
            use_agent: If True, uses intelligent agent. If False, uses simple chains.

        Returns:
            Processed response
        """
        try:
            answer = (  # Agent automatically decides the workflow
                self.agent_service.process_question(question).summary
                if use_agent
                else self._manual_chain_workflow(question)
            )  # Manual workflow with chains
            self.conversation_history.append(
                {  # Add to memory
                    "question": question,
                    "answer": answer,
                    "method": "agent" if use_agent else "manual",
                }
            )
            return answer

        except Exception as e:
            error_msg = f"Error processing question: {e}"
            self.conversation_history.append(
                {"question": question, "answer": error_msg, "method": "error"}
            )
            return error_msg

    def _manual_chain_workflow(self, question: str) -> str:
        """
        Manual workflow using specialized chains.

        TODO: try to decompose this big method into smaller fuctions

        This method provides explicit control over the processing pipeline:
        1. Generate SQL query from natural language
        2. Execute SQL query on database
        3. Summarize results with epidemiological analysis
        4. Search for related news articles
        5. Combine everything with RAG chain

        Use this when you need:
        - Full visibility into each step
        - Custom error handling per step
        - Debugging and monitoring
        - Fine-grained control over the workflow

        Args:
            question: Question in natural language

        Returns:
            Comprehensive answer combining data and news context
        """
        workflow_steps = []

        try:
            # Step 1: Generate SQL query
            workflow_steps.append("Generating SQL query...")
            sql_query = self.chain_service.sql_chain(question, self.schema_info)
            workflow_steps.append(f"SQL generated: {sql_query[:100]}...")

            # Step 2: Execute SQL query
            workflow_steps.append("Executing query on database...")
            try:
                query_results = self.data_repository.execute_query(sql_query)
                workflow_steps.append(f"Found {len(query_results)} records")
            except Exception as e:
                workflow_steps.append(f"Query execution failed: {e}")
                # Fallback: try to answer without database results
                return self._answer_without_data(question, str(e), workflow_steps)

            # Step 3: Summarize results with epidemiological analysis
            workflow_steps.append("Analyzing data...")
            if query_results:
                data_summary = self.chain_service.summarization_chain(
                    question, query_results
                )
                workflow_steps.append("Data analysis completed")
            else:
                data_summary = "No data found for the specified criteria."
                workflow_steps.append("No data to analyze")

            # Step 4: Search for related news
            workflow_steps.append("Searching related news...")
            try:
                if related_articles := self.vector_repository.search_similar(
                    query=question, limit=5
                ):
                    news_context = self._format_news_articles(related_articles)
                    workflow_steps.append(
                        f"Found {len(related_articles)} related articles"
                    )
                else:
                    news_context = "No related news articles found."
                    workflow_steps.append("No news articles found")

            except Exception as e:
                news_context = f"Could not retrieve news: {e}"
                workflow_steps.append(f"News search failed: {e}")

            # Step 5: Combine everything with RAG chain
            workflow_steps.append("Generating final answer...")

            # Prepare comprehensive context
            full_context = self._prepare_context(
                sql_query=sql_query,
                data_summary=data_summary,
                news_context=news_context,
                record_count=len(query_results) if query_results else 0,
            )

            # Use RAG chain to generate final answer with memory
            final_answer = self.chain_service.rag_chain(question, full_context)
            workflow_steps.append("Final answer generated")

            # Add workflow metadata to answer (useful for debugging)
            if self._should_include_metadata():
                metadata = "\n\n---\nWorkflow Steps:\n" + "\n".join(
                    f"• {step}" for step in workflow_steps
                )
                return f"{final_answer}{metadata}"

            return final_answer

        except Exception as e:
            return (
                f"Error in manual workflow: {e}\n\n"
                f"Completed steps:\n{'\n'.join(f'• {step}' for step in workflow_steps)}"
                f"\n\nOriginal question: {question}"
            )

    def _format_news_articles(self, articles: list[Article]) -> str:
        """
        Format news articles for context inclusion.

        Args:
            articles: List of Article entities

        Returns:
            Formatted string with article information
        """
        formatted_articles = []

        for i, article in enumerate(articles, 1):
            article_text = (
                f"{i}. {article.title}\n"
                f"   Source: {article.source_name}\n"
                f"   URL: {article.url}\n"
            )
            if article.description:
                # Limit description length
                article_text += f"   Summary: {
                    article.description[:200] + '...'
                    if len(article.description) > 200
                    else article.description
                }\n"

            if article.published_date:
                article_text += (
                    f"   Published: {article.published_date.strftime('%Y-%m-%d')}\n"
                )

            formatted_articles.append(article_text)

        return "\n".join(formatted_articles)

    def _prepare_context(
        self, sql_query: str, data_summary: str, news_context: str, record_count: int
    ) -> str:
        """
        Prepare comprehensive context for RAG chain.

        Args:
            sql_query: Generated SQL query
            data_summary: Summarized data analysis
            news_context: Related news articles
            record_count: Number of records found

        Returns:
            Formatted context string
        """
        context_parts = [
            "=== DATABASE ANALYSIS ===",
            f"SQL Query executed: {sql_query}",
            f"Records found: {record_count}",
            "",
            "Data Summary:",
            data_summary,
            "",
            "=== RELATED NEWS CONTEXT ===",
            news_context,
        ]
        # Add conversation context if available
        if self.conversation_history:
            recent_questions = [
                h["question"]
                for h in self.conversation_history[-3:]
                if h["method"] != "error"
            ]
            if recent_questions:
                context_parts.insert(0, "=== RECENT CONVERSATION ===")
                context_parts.insert(1, "Recent questions:")
                for q in recent_questions:
                    context_parts.insert(2, f"- {q}")
                context_parts.insert(3, "")

        return "\n".join(context_parts)

    def _answer_without_data(
        self, question: str, error_msg: str, workflow_steps: list[str]
    ) -> str:
        """
        Attempt to answer question without database results.

        Useful when SQL execution fails but we can still provide
        context from news and general knowledge.

        Args:
            question: Original question
            error_msg: Error message from SQL execution
            workflow_steps: Steps completed so far

        Returns:
            Answer based on available context
        """
        try:  # Try to get news context at least
            if related_articles := self.vector_repository.search_similar(
                question, limit=5
            ):
                return self.chain_service.rag_chain(
                    question,
                    f"Note: Database query failed with error: {error_msg}\n\n"
                    f"However, here is relevant information from news sources:\n\n"
                    f"{self._format_news_articles(related_articles)}",
                )
            else:
                return (
                    f"Unable to access database: {error_msg}\n"
                    f"No related news articles found.\n\n"
                    f"Please rephrase your question or contact support."
                )

        except Exception as e:
            return (
                f"Multiple errors occurred:\n"
                f"1. Database error: {error_msg}\n"
                f"2. News search error: {e}\n\n"
                f"Completed steps:\n"
                + "\n".join(f"• {step}" for step in workflow_steps)
            )

    def _should_include_metadata(self) -> bool:
        """
        Determine if workflow metadata should be included in response.

        Can be controlled by environment variable or user preference.
        Useful for debugging and transparency.

        Returns:
            True if metadata should be included
        """
        # Check if last question was asking for details/debug info
        if self.conversation_history:
            return any(
                keyword in self.conversation_history[-1].get("question", "").lower()
                for keyword in [
                    "how",
                    "explain",
                    "why",
                    "show steps",
                    "debug",
                    "details",
                ]
            )
        return False

    def get_conversation_summary(self) -> str:
        """
        Return summary of current conversation.

        Returns:
            Formatted summary of recent interactions
        """
        if not self.conversation_history:
            return "No conversation started."

        summary_parts = ["=== CONVERSATION SUMMARY ===\n"]

        # Overall stats
        total_interactions = len(self.conversation_history)
        agent_count = sum(
            1 for h in self.conversation_history if h["method"] == "agent"
        )
        manual_count = sum(
            1 for h in self.conversation_history if h["method"] == "manual"
        )
        error_count = sum(
            1 for h in self.conversation_history if h["method"] == "error"
        )
        summary_parts.append(f"Total interactions: {total_interactions}")
        summary_parts.append(f"- Agent-based: {agent_count}")
        summary_parts.append(f"- Manual workflow: {manual_count}")
        summary_parts.append(f"- Errors: {error_count}")
        summary_parts.append("\nRecent interactions (last 5):\n")

        # Recent interactions
        for i, interaction in enumerate(self.conversation_history[-5:], 1):
            question_preview = interaction["question"][:60]
            if len(interaction["question"]) > 60:
                question_preview += "..."

            answer_preview = interaction["answer"][:80]
            if len(interaction["answer"]) > 80:
                answer_preview += "..."

            summary_parts.append(
                f"{i}. Q: {question_preview}\n"
                f"   A: {answer_preview}\n"
                f"   Method: {interaction['method']}\n"
            )
        return "\n".join(summary_parts)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def export_conversation(self) -> str:
        """
        Export full conversation in a readable format.

        Returns:
            Formatted conversation export
        """
        if not self.conversation_history:
            return "No conversation to export."

        export_parts = [
            "=== CONVERSATION EXPORT ===",
            f"Total interactions: {len(self.conversation_history)}\n",
        ]
        for i, interaction in enumerate(self.conversation_history, 1):
            export_parts.append(f"\n--- Interaction {i} ---")
            export_parts.append(f"Method: {interaction['method']}")
            export_parts.append(f"\nQuestion:\n{interaction['question']}")
            export_parts.append(f"\nAnswer:\n{interaction['answer']}")
            export_parts.append("-" * 50)

        return "\n".join(export_parts)
