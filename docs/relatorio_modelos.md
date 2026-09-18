# Relatório de uso de modelos e parâmetros - Sprint 03

Comparativo entre os modelos servidos via Ollama. Rodar `python scripts/multi_provider.py` e `python evals/run_evals.py --versao lcel` com o Ollama ativo pra preencher os campos marcados com _(medir)_.

## Modelos comparados

| Modelo | Tamanho | Papel no projeto |
|--------|---------|------------------|
| `gpt-oss:120b` | 120B | modelo principal do chatbot |
| `qwen3:8b` | 8B | modelo de comparação |

## Parâmetros de geração

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| `temperature` | 0.2 | resposta factual sobre produto pede pouca criatividade; temperatura baixa reduz alucinação de specs |
| `top_p` | 0.9 | nucleus sampling padrão; com temperatura baixa, mantém a fluidez sem divagar |
| `max_tokens` (`num_predict`) | 512 | respostas curtas (máx. 3 parágrafos no prompt v2); limita custo e latência |
| memória (`max_token_limit`) | 1200 | dá uns 6 a 8 turnos de conversa; acima disso a poda remove os turnos mais antigos |

Valores lidos do `.env` (ver `.env.example`).

## Resultados

### Latência e tokens (multi-provider: 2 modelos x 2 prompts x 3 perguntas)

| Modelo | Prompt | Latência média (s) | Tokens médios de saída |
|--------|--------|--------------------|------------------------|
| gpt-oss:120b | v1 | _(medir)_ | _(medir)_ |
| gpt-oss:120b | v2 | _(medir)_ | _(medir)_ |
| qwen3:8b | v1 | _(medir)_ | _(medir)_ |
| qwen3:8b | v2 | _(medir)_ | _(medir)_ |

Dados brutos: `docs/multi_provider_resultados.json`.

### Qualidade (eval set, 13 casos)

| Modelo | Nota média (0-10) | Recusas corretas | Acurácia structured output |
|--------|-------------------|------------------|----------------------------|
| gpt-oss:120b | _(medir)_ | _(medir)_ | _(medir)_ |
| qwen3:8b | _(medir)_ | _(medir)_ | _(medir)_ |

## Conclusão

_(preencher após a rodada real: qual modelo ficou no projeto e por quê, pesando qualidade, latência e custo)_
