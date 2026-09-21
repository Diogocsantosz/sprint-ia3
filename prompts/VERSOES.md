# Versionamento do system prompt

| Versão | Data | O que mudou | Por quê | Ganho medido |
|--------|------|-------------|---------|--------------|
| v1 | Sprint 03 (início) | Prompt simples em texto corrido, 4 frases | Referência inicial para comparar a refatoração | qwen3:8b: 9,71; gemma3:1b: 8,42; gpt-oss-20b: 9,71 |
| v2 | Sprint 03 (atual) | XML tagging, base oficial embutida, regras de recusa e limite de resposta | Separar instruções dos dados e reduzir respostas sem apoio na base | qwen3:8b: 10,00; gemma3:1b: 9,01; gpt-oss-20b: 10,00 |

## Como medir o ganho

1. `python evals/run_evals.py --versao lcel --prompt v1` salva a nota da v1.
2. `python evals/run_evals.py --versao lcel --prompt v2` salva a nota da v2.
3. A comparação usa nota média, acurácia do structured output e recusas corretas.

## Tokens por versão (tiktoken, cl100k_base)

O prompt v1 tem 80 tokens e o v2 tem 382 tokens na contagem `cl100k_base`. Mesmo com uma entrada maior, o v2 reduziu a média por turno: de 164,6 para 113,2 tokens no qwen3:8b, de 145,4 para 91,3 no gemma3:1b e de 205,7 para 112,8 no gpt-oss-20b. Os dados brutos estão em `evals/sprint3_results.json`.

 ## Versão adotada

  A versão v2 foi escolhida como prompt de produção por apresentar respostas
  mais curtas, melhor organização do contexto e maior nota nas avaliações.
