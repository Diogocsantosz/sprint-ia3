"""Conta token com tiktoken (cl100k_base).

Não é o tokenizer exato que o Ollama usa, mas serve de régua pros
comparativos: tamanho dos prompts e custo de cada turno no eval.
"""

import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


def contar_tokens(texto: str) -> int:
    return len(_enc.encode(texto))
