"""Memória por sessão com limite de tokens (Aula 02).

O RunnableWithMessageHistory associa cada session_id ao seu histórico. O
ConversationTokenBufferMemory define o teto de tokens, e a poda remove os
turnos mais antigos quando esse limite é ultrapassado.

Essa stack saiu do pacote principal no LangChain 1.x e hoje fica no
langchain-classic. Ela foi mantida por ser a implementação pedida na Sprint 03.
"""

import warnings

from langchain_classic.memory import ConversationTokenBufferMemory
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.utils.tokens import contar_tokens

# A stack da Aula 02 está deprecated no LangChain 1.x.
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


class GerenciadorMemoria:
    def __init__(self, llm: BaseChatModel, max_tokens: int) -> None:
        self._llm = llm
        self._max_tokens = max_tokens
        self._memorias: dict[str, ConversationTokenBufferMemory] = {}

    def historico(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._memorias:
            self._memorias[session_id] = ConversationTokenBufferMemory(
                llm=self._llm,
                max_token_limit=self._max_tokens,
                return_messages=True,
            )
        return self._memorias[session_id].chat_memory

    def _tokens_historico(self, session_id: str) -> int:
        mem = self._memorias.get(session_id)
        if mem is None:
            return 0
        # O tiktoken mantém a mesma régua usada nas avaliações e evita uma
        # dependência adicional apenas para essa contagem.
        return sum(contar_tokens(str(m.content)) for m in mem.chat_memory.messages)

    def podar(self, session_id: str) -> None:
        mem = self._memorias.get(session_id)
        if mem is None:
            return
        # Remove turnos completos para não deixar uma resposta sem a pergunta.
        msgs = mem.chat_memory.messages
        while msgs and self._tokens_historico(session_id) > mem.max_token_limit:
            msgs.pop(0)
            if msgs and msgs[0].type == "ai":
                msgs.pop(0)

    def tokens_sessao(self, session_id: str) -> int:
        return self._tokens_historico(session_id)


def com_memoria(chain: Runnable, gerenciador: GerenciadorMemoria) -> RunnableWithMessageHistory:
    return RunnableWithMessageHistory(
        chain,
        gerenciador.historico,
        input_messages_key="pergunta",
        history_messages_key="history",
    )
