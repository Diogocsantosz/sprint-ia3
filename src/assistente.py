"""Orquestrador do chatbot: guardrails, roteamento e as chains LCEL.

Cada mensagem passa por:
1. moderação (jailbreak, injection, mensagem vazia/gigante)
2. validação de escopo GoodWe
3. roteamento: consulta de recarga vai pra chain estruturada, o resto vai
   pra conversa normal com memória
"""

import time
from dataclasses import dataclass
from typing import Optional

from src.chain.builder import chain_conversacional, chain_estruturada, criar_llm
from src.chain.memoria import GerenciadorMemoria, com_memoria
from src.config import Config
from src.guardrails.moderation import RECUSA_JAILBREAK, moderar
from src.guardrails.scope_validator import validar_escopo
from src.schemas.consulta import ConsultaRecarga
from src.utils.tokens import contar_tokens

GATILHOS_CONSULTA = [
    "estação", "estacao", "est-",
    "status do carregador", "status da estação", "status da estacao",
    "faturamento", "quanto faturei", "energia consumida",
    "custo da recarga", "quanto custou a recarga",
]


@dataclass
class RespostaAssistente:
    tipo: str  # texto | estruturada | recusa
    conteudo: str
    dados: Optional[ConsultaRecarga]
    tokens_turno: int
    latencia_s: float
    motivo: str = ""


def eh_consulta_recarga(pergunta: str) -> bool:
    low = pergunta.lower()
    return any(g in low for g in GATILHOS_CONSULTA)


class AssistenteEV:
    def __init__(self, cfg: Config, backend: str = "ollama", versao_prompt: str = "v2") -> None:
        self.cfg = cfg
        self.backend = backend
        llm_memoria = criar_llm(cfg, backend)
        self.memoria = GerenciadorMemoria(llm_memoria, cfg.memoria_max_tokens)
        self.chain_conversa = com_memoria(
            chain_conversacional(cfg, backend, versao_prompt), self.memoria
        )
        self.chain_consulta = chain_estruturada(cfg, backend)

    def responder(self, pergunta: str, session_id: str = "default") -> RespostaAssistente:
        t0 = time.perf_counter()

        veredito = moderar(pergunta)
        if not veredito.permitido:
            msg = RECUSA_JAILBREAK if veredito.tipo == "jailbreak" else (
                "Não posso processar uma mensagem vazia. Pode repetir?"
                if veredito.tipo == "vazio"
                else "Não posso processar uma mensagem tão longa. Resume pra mim, por favor?"
            )
            return self._fecha("recusa", msg, None, pergunta, t0, veredito.motivo)

        escopo = validar_escopo(pergunta)
        if not escopo.dentro_escopo:
            return self._fecha("recusa", escopo.mensagem_recusa, None, pergunta, t0, escopo.categoria)

        if eh_consulta_recarga(pergunta):
            dados = self.chain_consulta.invoke({"pergunta": pergunta})
            if isinstance(dados, ConsultaRecarga):
                return self._fecha("estruturada", dados.resposta, dados, pergunta, t0)

        texto = self.chain_conversa.invoke(
            {"pergunta": pergunta},
            config={"configurable": {"session_id": session_id}},
        )
        self.memoria.podar(session_id)
        return self._fecha("texto", texto, None, pergunta, t0)

    def _fecha(
        self,
        tipo: str,
        conteudo: str,
        dados: Optional[ConsultaRecarga],
        pergunta: str,
        t0: float,
        motivo: str = "",
    ) -> RespostaAssistente:
        return RespostaAssistente(
            tipo=tipo,
            conteudo=conteudo,
            dados=dados,
            tokens_turno=contar_tokens(pergunta) + contar_tokens(conteudo),
            latencia_s=round(time.perf_counter() - t0, 3),
            motivo=motivo,
        )
