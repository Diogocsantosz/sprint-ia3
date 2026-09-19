"""Configs do projeto. Tudo vem de variável de ambiente ou do .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    ollama_host: str
    modelo_principal: str
    modelo_comparacao: str
    modelo_groq: str
    temperatura: float
    top_p: float
    max_tokens: int
    memoria_max_tokens: int
    seed: int


def carregar_config() -> Config:
    return Config(
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        modelo_principal=os.getenv("MODELO_PRINCIPAL", "qwen3:8b"),
        modelo_comparacao=os.getenv("MODELO_COMPARACAO", "gemma3:1b"),
        modelo_groq=os.getenv("MODELO_GROQ", "openai/gpt-oss-20b"),
        temperatura=float(os.getenv("TEMPERATURA", "0.2")),
        top_p=float(os.getenv("TOP_P", "0.9")),
        max_tokens=int(os.getenv("MAX_TOKENS", "512")),
        memoria_max_tokens=int(os.getenv("MEMORIA_MAX_TOKENS", "1200")),
        seed=int(os.getenv("SEED", "42")),
    )
