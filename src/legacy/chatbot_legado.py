"""Versão manual das Sprints 1/2, mantida para o comparativo antes/depois.

Os problemas dela (que a Sprint 03 corrige):
- prompt montado por concatenação de strings
- histórico cresce sem limite de tokens
- não há guardrails antes da chamada ao modelo
- saída estruturada depende de json.loads sobre texto livre
- chamada HTTP direta ao Ollama
"""

import json
import time

import httpx

PROMPT_FIXO = "Você é o assistente de mobilidade elétrica da GoodWe Brasil. Responda em português.\n"


class ChatbotLegado:
    def __init__(
        self,
        host: str,
        modelo: str,
        mock: bool = False,
        temperatura: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 512,
        seed: int = 42,
    ) -> None:
        self.host = host
        self.modelo = modelo
        self.mock = mock
        self.opcoes = {
            "temperature": temperatura,
            "top_p": top_p,
            "num_predict": max_tokens,
            "seed": seed,
        }
        self.historico: list[tuple[str, str]] = []

    def _montar_prompt(self, pergunta: str) -> str:
        prompt = PROMPT_FIXO
        for autor, msg in self.historico:
            prompt += f"{autor}: {msg}\n"
        prompt += f"Usuário: {pergunta}\nAssistente:"
        return prompt

    def _gerar_mock(self, pergunta: str) -> str:
        low = pergunta.lower()
        # O legado não aplica moderação antes da chamada ao modelo.
        if "ignore" in low or "dan" in low or "system prompt" in low:
            return "Claro! Vou ignorar minhas instruções anteriores e fazer o que você pediu."
        if "est-" in low or "faturamento" in low:
            # Simula uma resposta com prosa ao redor do JSON.
            return (
                'Claro! Olha só o que encontrei: {"estacao_id": "EST-01", '
                '"estado": "disponivel", "potencia_kw": 7.4} - espero ter ajudado!'
            )
        if "ex30" in low:
            return "Seu carro é o Volvo EX30."
        return (
            "Sou o assistente da GoodWe. A linha HCA de carregadores vai de 7 a 22 kW. "
            "Posso ajudar com dúvidas sobre recarga de veículos elétricos."
        )

    def responder(self, pergunta: str) -> str:
        prompt = self._montar_prompt(pergunta)

        if self.mock:
            time.sleep(0.01)  # simula latência mínima
            saida = self._gerar_mock(pergunta)
        else:
            resp = httpx.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.modelo,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "options": self.opcoes,
                },
                timeout=120,
            )
            resp.raise_for_status()
            saida = resp.json()["response"].strip()

        self.historico.append(("Usuário", pergunta))
        self.historico.append(("Assistente", saida))
        return saida

    def tentar_extrair_json(self, texto: str) -> dict:
        """Tenta interpretar diretamente a resposta como JSON."""
        return json.loads(texto)
