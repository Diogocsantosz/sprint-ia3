"""Contagem de tokens com tiktoken (encoding cl100k_base, mesmo dos modelos GPT-4/4o).

Usado pra medir o tamanho dos prompts versionados e o custo de cada turno no eval.
Não é o tokenizer exato do Ollama, mas serve como régua consistente de comparativo.
"""

import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def contar_tokens(texto: str) -> int:
    return len(_enc.encode(texto))
