"""BÔNUS (+1 pt): comparação de mais de um modelo x mais de um prompt.

Roda as mesmas 3 perguntas em 2 modelos (principal e comparação) com as 2
versões de system prompt, medindo latência e tokens de saída.
Resultado vai pra docs/multi_provider_resultados.json.

Uso:
    python scripts/multi_provider.py          # com Ollama de verdade
    python scripts/multi_provider.py --mock   # simulação (sem GPU)
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402

from src.chain.builder import carregar_base, carregar_prompt, criar_llm  # noqa: E402
from src.config import carregar_config  # noqa: E402
from src.utils.tokens import contar_tokens  # noqa: E402

PERGUNTAS = [
    "Quais carregadores a GoodWe oferece no Brasil?",
    "O que é carga bidirecional?",
    "Qual a diferença entre carga AC e DC?",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--modelos", nargs="+", help="modelos do Ollama que serão comparados")
    args = ap.parse_args()

    cfg = carregar_config()
    backend = "mock" if args.mock else "ollama"
    modelos_configurados = args.modelos or [cfg.modelo_principal, cfg.modelo_comparacao]
    modelos = ["mock-ev"] if args.mock else list(dict.fromkeys(modelos_configurados))

    resultados = []

    for modelo in modelos:
        for versao in ["v1", "v2"]:
            system = carregar_prompt(versao)
            prompt = ChatPromptTemplate.from_messages(
                [("system", system), ("human", "{pergunta}")]
            )
            if "{base_conhecimento}" in system:
                prompt = prompt.partial(base_conhecimento=carregar_base())
            llm = criar_llm(cfg, backend, modelo=None if args.mock else modelo)
            chain = prompt | llm | StrOutputParser()

            for pergunta in PERGUNTAS:
                t0 = time.perf_counter()
                saida = chain.invoke({"pergunta": pergunta})
                lat = round(time.perf_counter() - t0, 3)

                resultados.append({
                    "modelo": modelo,
                    "prompt": versao,
                    "pergunta": pergunta,
                    "latencia_s": lat,
                    "tokens_saida": contar_tokens(saida),
                    "tokens_system_prompt": contar_tokens(system),
                    "saida": saida[:300],
                })
                print(f"{modelo} | prompt {versao} | {lat}s | {contar_tokens(saida)} tokens | {pergunta[:40]}...")

    arq = Path(__file__).resolve().parent.parent / "docs" / "multi_provider_resultados.json"
    arq.write_text(
        json.dumps({"mock": args.mock, "resultados": resultados}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nsalvo em {arq}")


if __name__ == "__main__":
    main()
