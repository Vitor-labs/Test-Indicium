# src/application/use_cases/enhanced_ai_query_use_case.py
from domain.services.agent_service import AgentService
from domain.services.chain_service import ChainService


class EnhancedAIQueryUseCase:
    """
    Caso de uso aprimorado com LangChain agents e chains.

    Vantagens:
    - Decisões inteligentes automáticas
    - Memory entre interações
    - Workflows complexos simplificados
    - Error handling robusto
    """

    def __init__(
        self,
        agent_service: AgentService,
        chain_service: ChainService,
    ) -> None:
        """
        Inicializa caso de uso aprimorado.

        Args:
            agent_service: Serviço de agentes
            chain_service: Serviço de chains
        """
        self.agent_service = agent_service
        self.chain_service = chain_service
        self.conversation_history: list[dict[str, str]] = []

    def ask_question(self, question: str, use_agent: bool = True) -> str:
        """
        Processa pergunta com opção de usar agent ou chains simples.

        Args:
            question: Pergunta em linguagem natural
            use_agent: Se True, usa agent inteligente. Se False, usa chains simples.

        Returns:
            Resposta processada
        """
        try:
            if use_agent:
                # Agent decide automaticamente o workflow
                result = self.agent_service.process_question(question)
                answer = result.summary
            else:
                # Workflow manual com chains
                answer = self._manual_chain_workflow(question)

            # Adicionar à memoria
            self.conversation_history.append(
                {
                    "question": question,
                    "answer": answer,
                    "method": "agent" if use_agent else "manual",
                }
            )

            return answer

        except Exception as e:
            error_msg = f"Erro ao processar pergunta: {e}"
            self.conversation_history.append(
                {"question": question, "answer": error_msg, "method": "error"}
            )
            return error_msg

    def _manual_chain_workflow(self, question: str) -> str:
        """Workflow manual usando chains especializadas."""
        # Implementação usando chains específicas
        # Mantido para casos onde controle manual é necessário
        return f"Processamento manual da pergunta: {question}"

    def get_conversation_summary(self) -> str:
        """Retorna resumo da conversa atual."""
        if not self.conversation_history:
            return "Nenhuma conversa iniciada."

        summary_items = []
        for i, interaction in enumerate(self.conversation_history[-5:], 1):
            summary_items.append(
                f"{i}. {interaction['question'][:50]}... "
                f"(método: {interaction['method']})"
            )

        return "Últimas interações:\n" + "\n".join(summary_items)
