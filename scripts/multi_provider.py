"""BÔNUS (+1 pt): comparação de provedores, modelos e prompts.

Roda as mesmas perguntas com Ollama e Groq usando as duas versões de prompt.
Resultado vai pra docs/multi_provider_resultados.json.

Uso:
    python scripts/multi_provider.py          # Ollama + Groq de verdade
    python scripts/multi_provider.py --mock   # simulação (sem GPU)
"""

import argparse
import json
import os
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
    ap.add_argument("--sem-groq", action="store_true", help="compara somente os modelos locais")
    args = ap.parse_args()

    cfg = carregar_config()
    if args.mock:
        configuracoes = [("mock", "mock-ev")]
    else:
        configuracoes = [
            ("ollama", cfg.modelo_principal),
            ("ollama", cfg.modelo_comparacao),
        ]
        if not args.sem_groq:
            if not os.getenv("GROQ_API_KEY"):
                raise SystemExit(
                    "GROQ_API_KEY não configurada. Preencha o .env ou use --sem-groq."
                )
            configuracoes.append(("groq", cfg.modelo_groq))

    resultados = []

    for provider, modelo in configuracoes:
        for versao in ["v1", "v2"]:
            system = carregar_prompt(versao)
            prompt = ChatPromptTemplate.from_messages(
                [("system", system), ("human", "{pergunta}")]
            )
            if "{base_conhecimento}" in system:
                prompt = prompt.partial(base_conhecimento=carregar_base())
            llm = criar_llm(cfg, provider, modelo=None if args.mock else modelo)
            chain = prompt | llm | StrOutputParser()

            for pergunta in PERGUNTAS:
                t0 = time.perf_counter()
                tentativas = 1
                saida = chain.invoke({"pergunta": pergunta})
                if not saida.strip():
                    tentativas += 1
                    saida = chain.invoke({"pergunta": pergunta})
                lat = round(time.perf_counter() - t0, 3)

                resultados.append({
                    "provider": provider,
                    "modelo": modelo,
                    "prompt": versao,
                    "pergunta": pergunta,
                    "latencia_s": lat,
                    "tentativas": tentativas,
                    "tokens_saida": contar_tokens(saida),
                    "tokens_system_prompt": contar_tokens(system),
                    "saida": saida[:300],
                })
                print(
                    f"{provider} | {modelo} | prompt {versao} | {lat}s | "
                    f"{contar_tokens(saida)} tokens | {pergunta[:40]}..."
                )

    arq = Path(__file__).resolve().parent.parent / "docs" / "multi_provider_resultados.json"
    arq.write_text(
        json.dumps(
            {
                "mock": args.mock,
                "providers": sorted({r["provider"] for r in resultados}),
                "resultados": resultados,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nsalvo em {arq}")


if __name__ == "__main__":
    main()