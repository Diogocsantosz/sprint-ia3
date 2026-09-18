"""Monta as chains LCEL do chatbot.

São duas: a conversacional (prompt | llm | parser de texto, com memória por fora)
e a estruturada (prompt | llm -> ConsultaRecarga validado).

backend="ollama" bate no ChatOllama de verdade. backend="mock" usa um modelinho
determinístico só pra rodar o pipeline sem GPU.
"""

import json
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from src.config import Config
from src.schemas.consulta import ConsultaRecarga

PASTA_PROMPTS = Path(__file__).resolve().parent.parent.parent / "prompts"
ARQUIVO_BASE = Path(__file__).resolve().parent.parent / "data" / "base_goodwe.json"

PROMPT_EXTRACAO = """Você extrai dados de uma consulta de recarga de veículo elétrico.
Responda SOMENTE com um JSON válido seguindo este schema:
{instrucoes}

Se algum dado numérico não for mencionado, invente valores plausíveis de uma
estação típica da GoodWe (7 a 22 kW). estacao_id no formato EST-XX."""


def carregar_prompt(versao: str) -> str:
    arq = PASTA_PROMPTS / f"system_prompt_{versao}.md"
    return arq.read_text(encoding="utf-8")


def carregar_base() -> str:
    dados = json.loads(ARQUIVO_BASE.read_text(encoding="utf-8"))
    dados.pop("_aviso", None)
    return json.dumps(dados, ensure_ascii=False, indent=2)


class MockEVChat(BaseChatModel):
    """Modelo fake que responde conforme as palavras da conversa.

    Não substitui modelo de verdade. Serve pra validar o pipeline
    (guardrails, memória, parsing) em máquina sem Ollama.
    """

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: object = None,
        **kwargs: object,
    ) -> ChatResult:
        # roteia pela última mensagem do usuário; olhar o histórico inteiro faz
        # o system prompt (que cita "bidirecional" na base) sequestrar o roteio
        historico = " ".join(str(m.content) for m in messages).lower()
        ultima = ""
        for m in reversed(messages):
            if m.type == "human":
                ultima = str(m.content).lower()
                break

        if "extrai dados de uma consulta" in historico:
            saida = json.dumps(
                {
                    "estacao_id": "EST-01",
                    "estado_carregador": "disponivel",
                    "potencia_kw": 7.4,
                    "energia_kwh": 32.5,
                    "custo_estimado_brl": 58.9,
                    "faturamento_periodo_brl": 412.3,
                    "resposta": "A estação EST-01 está disponível, com potência de 7,4 kW. No período ela entregou 32,5 kWh e o faturamento foi de R$ 412,30.",
                },
                ensure_ascii=False,
            )
        elif ("meu carro" in ultima or "meu nome" in ultima) and "ex30" in historico:
            saida = "Seu carro é o Volvo EX30, com bateria de 69 kWh."
        elif ("meu carro" in ultima or "meu nome" in ultima) and "dolphin" in historico:
            # caso do demo_memoria.py: Ana + BYD Dolphin de 60 kWh
            saida = "Pelo que você me contou: seu nome é Ana e seu carro é o BYD Dolphin, com bateria de 60 kWh."
        elif "bidirecional" in ultima:
            saida = (
                "Um carregador bidirecional deixa a energia fluir nos dois sentidos: "
                "além de carregar o carro, devolve energia da bateria pra casa (V2H) "
                "ou pra rede (V2G). É a base dos projetos de veículo-como-bateria."
            )
        elif ("ac" in ultima and "dc" in ultima) or "diferença" in ultima:
            saida = (
                "Carga AC usa corrente alternada (3,7 a 22 kW), é a do dia a dia, "
                "em casa e no trabalho. Carga DC é corrente contínua, acima de 50 kW, "
                "a carga rápida de eletropostos e rodovias."
            )
        elif "carregador" in ultima or "carregadores" in ultima or "kw" in ultima:
            saida = (
                "No Brasil a GoodWe trabalha com a linha HCA de carregadores AC: "
                "HCA 7kW (monofásico, residencial), HCA 11kW e HCA 22kW (trifásicos, "
                "pra condomínios e frotas). Todos com conector Type 2. "
                "Só afirmo o que consta na base oficial. Se quiser um modelo que "
                "não está aqui, recomendo o suporte GoodWe."
            )
        else:
            saida = (
                "Sou o assistente de mobilidade elétrica da GoodWe. Posso ajudar com "
                "carregadores, recarga de EVs e conceitos como carga AC/DC e "
                "bidirecional. Só respondo com base nos dados oficiais da GoodWe."
            )

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=saida))])

    @property
    def _llm_type(self) -> str:
        return "mock-ev"


def criar_llm(cfg: Config, backend: str, modelo: str | None = None) -> BaseChatModel:
    if backend == "mock":
        return MockEVChat()

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=modelo or cfg.modelo_principal,
        base_url=cfg.ollama_host,
        temperature=cfg.temperatura,
        top_p=cfg.top_p,
        num_predict=cfg.max_tokens,
    )


def chain_conversacional(cfg: Config, backend: str, versao_prompt: str) -> Runnable:
    system = carregar_prompt(versao_prompt)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            MessagesPlaceholder("history"),
            ("human", "{pergunta}"),
        ]
    )
    # a base vai como variável parcial: se der replace direto na string,
    # as chaves do JSON quebram o template f-string (quebramos a cara com isso)
    if "{base_conhecimento}" in system:
        prompt = prompt.partial(base_conhecimento=carregar_base())
    llm = criar_llm(cfg, backend)
    return prompt | llm | StrOutputParser()


def chain_estruturada(cfg: Config, backend: str) -> Runnable:
    parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PROMPT_EXTRACAO),
            ("human", "{pergunta}"),
        ]
    ).partial(instrucoes=parser.get_format_instructions())

    llm = criar_llm(cfg, backend)

    if backend == "ollama":
        # structured output nativo do Ollama (format=json + schema)
        return prompt | llm.with_structured_output(ConsultaRecarga)

    return prompt | llm | parser
