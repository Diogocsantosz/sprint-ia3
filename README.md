# EV Challenge - GoodWe · Sprint 03

Chatbot de mobilidade elétrica da GoodWe Brasil. Núcleo conversacional refatorado em **LangChain LCEL**: chain `prompt | llm | parser`, memória por sessão com limite de tokens, saída estruturada em Pydantic v2 e guardrails de escopo e segurança.

FIAP · Prompt and Artificial Intelligence · 2SEM 2026.2 · Prof. Jorge Luiz Gomes

## Estrutura

```
prompts/            system prompt versionado (v1, v2) + tabela de versões (VERSOES.md)
src/chain/          builder.py (chains LCEL) e memoria.py (sessão + limite de tokens)
src/schemas/        consulta.py, o ConsultaRecarga (Pydantic v2, field_validator)
src/guardrails/     moderation.py (jailbreak/injection) e scope_validator.py (escopo GoodWe)
src/legacy/         chatbot_legado.py, versão manual das Sprints 1/2 (base do comparativo)
src/data/           base_goodwe.json, base de conhecimento de produtos
evals/              eval_set.json + run_evals.py + sprint3_results.json
scripts/            demo_memoria.py (3+ turnos) e multi_provider.py (bônus com mais de um provedor)
docs/               relatórios de evolução, modelos e resultados comparativos
main.py             CLI do chatbot
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # ajuste OLLAMA_HOST e modelos
```

Para usar o segundo provedor, crie uma chave no GroqCloud e preencha
`GROQ_API_KEY` somente no `.env`. Esse arquivo não é versionado.

Sem GPU/Ollama local dá pra testar o fluxo da aplicação com `--mock`. As respostas nesse modo são fixas, então ele não serve para medir a qualidade dos prompts.

## Como rodar

```powershell
python main.py --mock                                  # conversar (mock)
python main.py                                         # conversar (Ollama)
python main.py --provider groq                         # conversar com o segundo provedor
python evals/run_evals.py --versao lcel --mock         # eval da versão nova
python evals/run_evals.py --versao legado --mock       # eval da versão Sprints 1/2
python evals/run_evals.py --versao lcel --prompt v1    # mede outra versão de prompt
python scripts/demo_memoria.py --mock                  # memória em 5 turnos com poda
python scripts/multi_provider.py                       # bônus: Ollama + Groq x 2 prompts
python evals/run_evals.py --versao lcel --provider groq # eval do segundo provedor
```

## Notas

- `ConversationTokenBufferMemory` e `RunnableWithMessageHistory` são a stack pedida na Sprint 03 (Aula 02). No LangChain 1.x elas vivem no pacote `langchain-classic` e estão deprecated. A migração pra LangGraph é assunto do Módulo 3.
- Credenciais e host ficam no `.env` (gitignored). Nenhuma chave no histórico do Git.
- A aplicação aceita Ollama local e Groq; a escolha é feita no argumento `--provider`.
- As especificações em `src/data/base_goodwe.json` foram conferidas na página e no datasheet oficiais da GoodWe Brasil em 19/09/2026.
- A aplicação não está integrada à telemetria do SEMS. Consultas de estação são estruturadas, mas status, consumo e faturamento ficam vazios para evitar dados inventados.
