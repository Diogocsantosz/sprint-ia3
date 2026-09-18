# Checklist de entrega - Sprint 03 (rubrica oficial)

Controle interno do grupo, baseado no documento oficial do Challenge.
Legenda: [x] feito · [ ] pendente

## A - Refactory LangChain (40 pts)

- [x] Chain LCEL end-to-end (`ChatPromptTemplate | ChatOllama | parser`) - `src/chain/builder.py`
- [x] Memória por sessão com limite de tokens (`RunnableWithMessageHistory` + `ConversationTokenBufferMemory`) - `src/chain/memoria.py`
- [x] Memória demonstrada em 3+ turnos - `scripts/demo_memoria.py` (5 turnos com poda) + caso `mem01` do eval
- [x] Structured output com schema Pydantic v2 + `field_validator` (`ConsultaRecarga`) - `src/schemas/consulta.py`, acurácia 100% no eval mock

## B - Prompt versionado + relatório de modelos (25 pts)

- [x] System prompt versionado (v1, v2) com XML tagging - `prompts/`
- [x] Tabela de versões: o que mudou e por quê - `prompts/VERCOES.md`
- [ ] Ganho medido entre versões de prompt (depende da rodada real no Ollama)
- [x] Parâmetros documentados (temperature, top_p, max_tokens) - `docs/relatorio_modelos.md`
- [ ] Comparativo de 2+ modelos preenchido (gpt-oss:120b x qwen3:8b) - tabelas com `_(medir)_`

## C - Segurança e guardrails (15 pts)

- [x] Recusa de jailbreak/prompt injection - `src/guardrails/moderation.py` (6/6 no eval)
- [x] Validação de escopo GoodWe com orientação a profissional habilitado - `src/guardrails/scope_validator.py`
- [x] Regra de não inventar specs fora da base - regra 2 do prompt v2 + `src/data/base_goodwe.json`

## D - Eval, evolução e relatório (20 pts)

- [x] Eval set reexecutado (13 casos: happy path, memória, edge cases, jailbreak, out-of-scope) - `evals/`
- [x] Relatório de evolução com a estrutura do §8 - `docs/relatorio_evolucao.md`
- [x] Tabela antes/depois (nota, tokens/turno, latência, acurácia structured output) - números do modo mock
- [ ] Substituir números mock pelos reais do Ollama na tabela antes/depois
- [x] Problemas encontrados e soluções (3 documentados, mínimo era 2)
- [x] Equipe e divisão de trabalho (nome, RM, tarefa) - seção 5 do relatório
- [ ] Exportar relatório pra PDF (máx. 5 páginas) em `docs/`

## Bônus - multi-provider (+1 pt)

- [x] Script de chamada multi-provider (2 modelos x 2 prompts) - `scripts/multi_provider.py`
- [ ] Rodada real com 2 modelos (hoje só `qwen3:8b` está baixado no Ollama)

## Condições de entrega (§10)

- [x] Credenciais fora do histórico (`.env` no `.gitignore`, nenhuma key commitada)
- [ ] Repositório público no ar: https://github.com/Diogocsantosz/sprint-ia3.git (remote + push)
- [ ] Histórico com commits regulares de cada integrante (hoje só existe 1 commit)
- [ ] `INTEGRANTES.txt` com nome, RM **e turma** de cada integrante (turma pendente)
- [ ] Relatório de evolução em PDF junto do repositório
