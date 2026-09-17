"""Validação de escopo GoodWe.

O assistente só fala de mobilidade elétrica, recarga e produtos GoodWe.
Pedidos de aconselhamento jurídico, financeiro ou de segurança elétrica são
recusados — sempre orientando a procurar profissional habilitado.
"""

from dataclasses import dataclass

RECUSA_JURIDICO = (
    "Não posso dar orientação jurídica — isso exige análise de um advogado. "
    "Se o assunto envolve seus direitos como consumidor, procure um advogado "
    "ou o Procon. Posso ajudar com dúvidas técnicas sobre recarga e produtos GoodWe."
)

RECUSA_FINANCEIRO = (
    "Não posso dar recomendação financeira ou de investimento. Para isso, "
    "procure um profissional habilitado (ex.: planejador financeiro certificado). "
    "Posso ajudar com informações técnicas sobre carregadores e recarga de EVs."
)

RECUSA_ELETRICA = (
    "Não posso orientar instalação ou manutenção elétrica por conta própria — "
    "mexer com elétrica sem qualificação é risco de vida. Procure um eletricista "
    "habilitado (norma NR-10) ou um integrador autorizado GoodWe. Posso explicar "
    "conceitos gerais sobre recarga, se quiser."
)

# categoria -> (gatilhos, mensagem de recusa)
CATEGORIAS_PROIBIDAS = {
    "juridico": (
        [
            "advogado", "processar", "processo judicial", "indenização",
            "indenizacao", "procon", "direitos do consumidor", "jurídico",
            "juridico", "entrar na justiça", "código de defesa do consumidor",
        ],
        RECUSA_JURIDICO,
    ),
    "financeiro": (
        [
            "investir em", "investimento", "comprar ações", "vale a pena investir",
            "aplicação financeira", "renda fixa", "retorno do investimento",
            "ações da goodwe", "papel na bolsa", "day trade",
        ],
        RECUSA_FINANCEIRO,
    ),
    "seguranca_eletrica": (
        [
            "fazer a fiação", "fazer a fiacao", "instalar sozinho",
            "instalação elétrica por conta", "instalacao eletrica por conta",
            "ligar o disjuntor", "emendar fio", "gambiarra elétrica",
            "gambiarra eletrica", "passar fio", "eu mesmo instalar",
            "eu mesmo instalo", "sem eletricista",
        ],
        RECUSA_ELETRICA,
    ),
}


@dataclass
class ResultadoEscopo:
    dentro_escopo: bool
    categoria: str = ""
    mensagem_recusa: str = ""


def validar_escopo(mensagem: str) -> ResultadoEscopo:
    low = mensagem.lower()
    for categoria, (gatilhos, recusa) in CATEGORIAS_PROIBIDAS.items():
        for gatilho in gatilhos:
            if gatilho in low:
                return ResultadoEscopo(False, categoria, recusa)
    return ResultadoEscopo(True)
