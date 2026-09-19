# Relatório de uso de modelos e parâmetros - Sprint 03

Comparativo entre três modelos, dois servidos localmente pelo Ollama e um pelo Groq. A rodada foi feita em 19/09/2026 com as mesmas três perguntas e as duas versões de prompt.

## Modelos configurados

| Provedor | Modelo | Tamanho | Papel no projeto |
|----------|--------|---------|------------------|
| Ollama | `qwen3:8b` | 8,2B, Q4_K_M | modelo principal local |
| Ollama | `gemma3:1b` | 1B | comparação leve; menor latência |
| Groq | `openai/gpt-oss-20b` | 20B | segundo provedor; comparação por API |

## Parâmetros de geração

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `temperature` | 0.2 | resposta factual sobre produto pede pouca criatividade; temperatura baixa reduz alucinação de specs |
| `top_p` | 0.9 | nucleus sampling padrão; com temperatura baixa, mantém a fluidez sem divagar |
| `max_tokens` (`num_predict`) | 512 | respostas curtas (máx. 3 parágrafos no prompt v2); limita custo e latência |
| memória (`max_token_limit`) | 1200 | dá uns 6 a 8 turnos de conversa; acima disso a poda remove os turnos mais antigos |
| `seed` | 42 | torna as rodadas comparáveis e reproduzíveis |
| `reasoning_effort` (Groq) | low | preserva o limite de saída para a resposta final |

Valores lidos do `.env` (ver `.env.example`).

## Resultados

### Latência e tokens (3 modelos x 2 prompts x 3 perguntas)

| Provedor | Modelo | Prompt | Latência média (s) | Tokens médios de saída |
|----------|--------|--------|--------------------|------------------------|
| Ollama | qwen3:8b | v1 | 7,753 | 365,0 |
| Ollama | qwen3:8b | v2 | 4,378 | 193,7 |
| Ollama | gemma3:1b | v1 | 1,155 | 231,7 |
| Ollama | gemma3:1b | v2 | 0,631 | 119,7 |
| Groq | openai/gpt-oss-20b | v1 | 0,938 | 553,0 |
| Groq | openai/gpt-oss-20b | v2 | 0,651 | 216,7 |

Dados brutos: `docs/multi_provider_resultados.json`.

### Qualidade (eval set, 17 casos)

| Provedor | Modelo e prompt | Nota média (0-10) | Recusas corretas | Acurácia structured output |
|----------|-----------------|-------------------|------------------|----------------------------|
| Ollama | qwen3:8b · v1 | 9,71 | 8/8 | 100% |
| Ollama | qwen3:8b · v2 | 10,00 | 8/8 | 100% |
| Ollama | gemma3:1b · v1 | 8,42 | 8/8 | 0% |
| Ollama | gemma3:1b · v2 | 9,01 | 8/8 | 0% |
| Groq | openai/gpt-oss-20b · v1 | 9,71 | 8/8 | 100% |
| Groq | openai/gpt-oss-20b · v2 | 10,00 | 8/8 | 100% |

## Conclusão

O `qwen3:8b` continua como principal porque roda localmente, alcançou nota 10 e acertou os campos estruturados. O `openai/gpt-oss-20b` também chegou a 10 e teve a menor latência na comparação de prompts, mas depende de conexão e chave externa. O `gemma3:1b` é leve, porém falhou na extração dos identificadores de estação. Nos três modelos, o prompt v2 produziu respostas mais curtas.

