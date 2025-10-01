# src/domain/services/agent_service.py
from abc import ABC, abstractmethod

from domain.entities.document import QueryResult


class AgentService(ABC):
    """Interface para serviços de agentes inteligentes."""

    @abstractmethod
    def process_question(self, question: str) -> QueryResult:
        """
        Processa pergunta usando agente inteligente.

        Args:
            question: Pergunta em linguagem natural

        Returns:
            Resultado estruturado com dados e contexto
        """
        pass

    @abstractmethod
    def add_memory(self, question: str, answer: str) -> None:
        """
        Adiciona interação ao histórico de memória.

        Args:
            question: Pergunta feita
            answer: Resposta fornecida
        """
        pass
