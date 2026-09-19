"""Validação de escopo GoodWe.

O assistente só fala de mobilidade elétrica, recarga e produtos GoodWe.
Pedido de conselho jurídico, financeiro ou de mexer na parte elétrica é
recusado, sempre mandando a pessoa pra um profissional habilitado.
"""

from dataclasses import dataclass

RECUSA_JURIDICO = (
    "Não posso dar orientação jurídica, isso é assunto pra advogado. "
    "Se o problema envolve seus direitos como consumidor, procure um advogado "
    "ou o Procon. Posso ajudar com dúvidas técnicas sobre recarga e produtos GoodWe."
)

RECUSA_FINANCEIRO = (
    "Não posso dar recomendação financeira ou de investimento. Pra isso, "
    "procure um profissional habilitado (um planejador financeiro certificado, "
    "por exemplo). Posso ajudar com informações técnicas sobre carregadores e recarga de EVs."
)

RECUSA_ELETRICA = (
    "Não posso orientar instalação ou manutenção elétrica por conta própria. "
    "Mexer com elétrica sem qualificação é risco de vida. Procure um eletricista "
    "habilitado (norma NR-10) ou um integrador autorizado GoodWe. Se quiser, "
    "eu explico os conceitos gerais de recarga."
)

RECUSA_FORA_ESCOPO = (
    "Esse assunto fica fora do meu escopo. Posso ajudar com carregadores GoodWe, "
    "recarga de veículos elétricos e conceitos de mobilidade elétrica."
)

# categoria -> (gatilhos, mensagem de recusa)
CATEGORIAS_PROIBIDAS = {
    "juridico": (
        [
            "advogado", "processar a concessionária", "processar a concessionaria",
            "processo judicial", "indenização",
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

TERMOS_DO_ESCOPO = [
    "goodwe", "hca", "carregador", "recarga", "carregar", "veículo elétrico",
    "veiculo eletrico", "carro elétrico", "carro eletrico", "meu carro",
    "estação", "estacao", "bateria", "kwh", "kw", "corrente alternada",
    "corrente contínua", "corrente continua", "carga ac", "carga dc", "type 2",
    "tipo 2", "bidirecional", "v2g", "v2h", "sems", "energia solar",
    "fotovolta", "wallbox", "eletroposto", "meu nome",
]

SAUDACOES = {"oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "obrigado", "obrigada"}


@dataclass
class ResultadoEscopo:
    dentro_escopo: bool
    categoria: str = ""
    mensagem_recusa: str = ""


def validar_escopo(mensagem: str) -> ResultadoEscopo:
    low = mensagem.lower().strip()
    for categoria, (gatilhos, recusa) in CATEGORIAS_PROIBIDAS.items():
        for gatilho in gatilhos:
            if gatilho in low:
                return ResultadoEscopo(False, categoria, recusa)

    if low in SAUDACOES or any(termo in low for termo in TERMOS_DO_ESCOPO):
        return ResultadoEscopo(True)

    marcadores_de_pergunta = (
        "?", "quem ", "qual ", "como ", "onde ", "quando ", "por que ",
        "conte ", "explique ",
    )
    if not any(marcador in low for marcador in marcadores_de_pergunta):
        return ResultadoEscopo(True)

    return ResultadoEscopo(False, "fora_escopo", RECUSA_FORA_ESCOPO)
