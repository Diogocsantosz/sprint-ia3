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
