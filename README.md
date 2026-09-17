# EV Challenge — GoodWe · Sprint 03

Chatbot de mobilidade elétrica da GoodWe Brasil, com o núcleo conversacional refatorado em **LangChain LCEL** — chain `prompt | llm | parser`, memória por sessão com limite de tokens, saída estruturada Pydantic v2 e guardrails de escopo/segurança.

FIAP · Prompt and Artificial Intelligence · 2SEM 2026.2 · Prof. Jorge Luiz Gomes

## Estrutura

```
prompts/            system prompt versionado (v1, v2) + tabela de versões (VERSOES.md)
src/chain/          builder.py (chains LCEL) e memoria.py (sessão + limite de tokens)
src/schemas/        consulta.py — ConsultaRecarga (Pydantic v2, field_validator)
src/guardrails/     moderation.py (jailbreak/injection) e scope_validator.py (escopo GoodWe)
src/legacy/         chatbot_legado.py — versão manual das Sprints 1/2 (base do comparativo)
src/data/           base_goodwe.json — base de conhecimento de produtos
evals/              eval_set.json + run_evals.py + sprint3_results.json
scripts/            demo_memoria.py (3+ turnos) e multi_provider.py (bônus)
docs/               relatorio_modelos.md, relatorio_evolucao.md, resultados multi-provider
main.py             CLI do chatbot
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # ajuste OLLAMA_HOST e modelos
```

Sem GPU/Ollama local, tudo roda em modo simulado com `--mock` (valida o pipeline inteiro: guardrails, memória, parsing — só a geração é determinística).

## Como rodar

```powershell
python main.py --mock                                  # conversar (mock)
python main.py                                         # conversar (Ollama)
python evals/run_evals.py --versao lcel --mock         # eval da versão nova
python evals/run_evals.py --versao legado --mock       # eval da versão Sprints 1/2
python evals/run_evals.py --versao lcel --prompt v1    # mede outra versão de prompt
python scripts/demo_memoria.py --mock                  # memória em 5 turnos com poda
python scripts/multi_provider.py                       # bônus: 2 modelos x 2 prompts
```

## Notas

- `ConversationTokenBufferMemory` e `RunnableWithMessageHistory` são a stack pedida na Sprint 03 (Aula 02). No LangChain 1.x vivem no pacote `langchain-classic` e estão deprecated — a migração pra LangGraph é assunto do Módulo 3.
- Credenciais/host ficam no `.env` (gitignored). Nenhuma chave no histórico do Git.
- `src/data/base_goodwe.json` tem dados de exemplo: substituir pelas especificações oficiais da GoodWe Brasil antes da entrega.
