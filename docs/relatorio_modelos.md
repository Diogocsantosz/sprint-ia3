# Relatório de uso de modelos e parâmetros - Sprint 03

Comparativo entre dois modelos servidos localmente pelo Ollama. A rodada foi feita em 19/09/2026 com o mesmo ambiente e as mesmas perguntas. O projeto também aceita Groq como segundo provedor; a integração externa depende de `GROQ_API_KEY` e deve ser medida separadamente para não misturar resultados não executados com esta tabela.

## Modelos configurados

| Provedor | Modelo | Tamanho | Papel no projeto |
|----------|--------|---------|------------------|
| Ollama | `qwen3:8b` | 8,2B, Q4_K_M | modelo principal; melhor nota no eval |
| Ollama | `gemma3:1b` | 1B | comparação leve; menor latência |
| Groq | `llama-3.3-70b-versatile` | 70B | segundo provedor; execução opcional com chave externa |

## Parâmetros de geração

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `temperature` | 0.2 | resposta factual sobre produto pede pouca criatividade; temperatura baixa reduz alucinação de specs |
| `top_p` | 0.9 | nucleus sampling padrão; com temperatura baixa, mantém a fluidez sem divagar |
| `max_tokens` (`num_predict`) | 512 | respostas curtas (máx. 3 parágrafos no prompt v2); limita custo e latência |
| memória (`max_token_limit`) | 1200 | dá uns 6 a 8 turnos de conversa; acima disso a poda remove os turnos mais antigos |
| `seed` | 42 | torna as rodadas comparáveis e reproduzíveis |

Valores lidos do `.env` (ver `.env.example`).

## Resultados

### Latência e tokens (2 modelos x 2 prompts x 3 perguntas)

| Modelo | Prompt | Latência média (s) | Tokens médios de saída |
|--------|--------|--------------------|------------------------|
| qwen3:8b | v1 | 8,349 | 376,3 |
| qwen3:8b | v2 | 4,141 | 174,7 |
| gemma3:1b | v1 | 1,346 | 262,3 |
| gemma3:1b | v2 | 0,466 | 86,0 |

Dados brutos: `docs/multi_provider_resultados.json`.

### Qualidade (eval set, 17 casos)

| Modelo | Nota média (0-10) | Recusas corretas | Acurácia structured output |
|--------|-------------------|------------------|----------------------------|
| qwen3:8b · v1 | 9,71 | 8/8 | 100% |
| qwen3:8b · v2 | 10,00 | 8/8 | 100% |
| gemma3:1b · v1 | 8,42 | 8/8 | 0% |
| gemma3:1b · v2 | 9,01 | 8/8 | 0% |

## Conclusão

O `qwen3:8b` ficou como principal porque teve a maior nota e acertou os campos estruturados. O `gemma3:1b` foi mais rápido, mas não extraiu o identificador das estações nos dois casos estruturados. O prompt v2 foi mantido porque melhorou a nota dos dois modelos e produziu respostas mais curtas, mesmo com um system prompt maior.
