"""CLI do chatbot EV — GoodWe Brasil.

Uso:
    python main.py                      # conversa com Ollama (config do .env)
    python main.py --mock               # sem GPU: pipeline inteiro em modo simulado
    python main.py --prompt v1          # testa outra versão de system prompt
    python main.py --sessao fulano      # isola a memória por sessão
"""

import argparse

from src.assistente import AssistenteEV
from src.config import carregar_config


def main() -> None:
    ap = argparse.ArgumentParser(description="Chatbot EV — GoodWe (Sprint 03)")
    ap.add_argument("--mock", action="store_true", help="roda sem Ollama (modelo fake)")
    ap.add_argument("--prompt", default="v2", choices=["v1", "v2"])
    ap.add_argument("--sessao", default="cli")
    args = ap.parse_args()

    cfg = carregar_config()
    bot = AssistenteEV(cfg, backend="mock" if args.mock else "ollama", versao_prompt=args.prompt)

    print("Chatbot EV — GoodWe Brasil (Sprint 03)")
    print(f"backend: {'mock' if args.mock else cfg.modelo_principal} | prompt: {args.prompt} | sessão: {args.sessao}")
    print("Digite /sair pra encerrar.\n")

    while True:
        try:
            pergunta = input("você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\naté mais!")
            break

        if pergunta.lower() in ("/sair", "/exit", "/quit"):
            print("até mais!")
            break

        resp = bot.responder(pergunta, session_id=args.sessao)

        if resp.tipo == "estruturada" and resp.dados is not None:
            print(f"volt: {resp.dados.resposta}")
            print(f"  [dados] estação={resp.dados.estacao_id} | estado={resp.dados.estado_carregador} "
                  f"| {resp.dados.potencia_kw} kW | faturamento R$ {resp.dados.faturamento_periodo_brl}")
        else:
            print(f"volt: {resp.conteudo}")
        print(f"  [{resp.tipo} | {resp.tokens_turno} tokens | {resp.latencia_s}s]")


if __name__ == "__main__":
    main()
