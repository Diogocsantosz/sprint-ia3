"""Demo da memória por sessão com limite de tokens (Aula 02).

Roda 5 turnos na mesma sessão e mostra o histórico sendo podado quando estoura
o teto de tokens. Com MEMORIA_MAX_TOKENS baixo (no .env ou aqui embaixo) a poda
aparece já nos primeiros turnos.

Uso: python scripts/demo_memoria.py --mock
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.assistente import AssistenteEV  # noqa: E402
from src.config import carregar_config  # noqa: E402

TURNOS = [
    "Oi! Meu nome é Ana e eu tenho um BYD Dolphin.",
    "Ele tem bateria de 60 kWh. Consigo carregar em casa com um carregador de 7 kW?",
    "O que é carga bidirecional?",
    "E carga AC, o que significa?",
    "Pra fechar: qual é o meu nome e qual o modelo do meu carro?",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--max-tokens-memoria", type=int, default=300)
    args = ap.parse_args()

    cfg = carregar_config()
    cfg.memoria_max_tokens = args.max_tokens_memoria

    bot = AssistenteEV(cfg, backend="mock" if args.mock else "ollama")
    sessao = "demo-memoria"

    print(f"memória limitada a {cfg.memoria_max_tokens} tokens\n")

    for i, turno in enumerate(TURNOS, 1):
        resp = bot.responder(turno, session_id=sessao)
        tokens_hist = bot.memoria.tokens_sessao(sessao)
        msgs = len(bot.memoria.historico(sessao).messages)
        print(f"--- turno {i} ---")
        print(f"ana: {turno}")
        print(f"volt: {resp.conteudo}")
        print(f"[histórico: {msgs} mensagens | {tokens_hist} tokens]\n")


if __name__ == "__main__":
    main()
