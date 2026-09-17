# Versionamento do system prompt

| Versão | Data | O que mudou | Por quê | Ganho medido |
|--------|------|-------------|---------|--------------|
| v1 | Sprint 03 (início) | Prompt simples em texto corrido, 4 frases | Baseline das Sprints 1/2, só traduzido pro projeto | nota média no eval: _ver `evals/sprint3_results.json`_ |
| v2 | Sprint 03 (atual) | XML tagging (`<papel>`, `<contexto>`, `<base_conhecimento>`, `<regras>`, `<formato_resposta>`); base de produtos embutida no prompt; regras explícitas de recusa e anti-injection; limite de tamanho de resposta | Aula 04 (context engineering): separar instrução de dados reduz alucinação e deixa o prompt auditável | _preencher após rodar `run_evals.py` e `multi_provider.py` com os modelos reais_ |

## Como medir o ganho

1. `python evals/run_evals.py --versao lcel --prompt v1` → salva nota da v1
2. `python evals/run_evals.py --versao lcel --prompt v2` → salva nota da v2
3. Comparar nota média, acurácia do structured output e recusas corretas.

## Tokens por versão (tiktoken, cl100k_base)

Medidos em `evals/sprint3_results.json` (campo `tokens_system_prompt`) — atualizar aqui depois da rodada com os modelos reais.
