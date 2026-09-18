# Relatório de evolução do projeto - Sprint 03

**EV Challenge - GoodWe** · Prompt and Artificial Intelligence · 2SEM 2026.2
Grupo: Diogo Chiaradia Santos (RM 570246), Rafael Laprega Gontijo Magalhaes (RM 561975), Gustavo Torres de Oliveira (RM 572952) e Lucas Furquim Lima (RM 568690)

> Fonte Markdown do PDF de entrega (máx. 5 páginas). Exportar pra PDF depois de preencher os campos _(medir)_ com a rodada real no Ollama.

## 1. Resumo da evolução

Nas **Sprints 1/2** o chatbot era um script procedural: prompt montado por concatenação de strings, histórico em lista Python sem limite, chamada HTTP crua pro Ollama e "saída estruturada" feita com `json.loads` na resposta do modelo. Não tinha guardrail nenhum, nem de segurança nem de escopo.

Na **Sprint 03** o núcleo foi reconstruído em LangChain:

- **Chain LCEL** (`src/chain/builder.py`): `ChatPromptTemplate | ChatOllama | StrOutputParser` pra conversa e chain dedicada com `with_structured_output` pra consultas de recarga.
- **Memória por sessão** (`src/chain/memoria.py`): `RunnableWithMessageHistory` + `ConversationTokenBufferMemory` com teto de tokens e poda dos turnos antigos.
- **Structured output** (`src/schemas/consulta.py`): `ConsultaRecarga` em Pydantic v2 com `field_validator` (formato da estação, normalização de estado, faixa plausível de potência).
- **Context engineering** (`prompts/`): system prompt v2 com XML tagging (`<papel>`, `<contexto>`, `<base_conhecimento>`, `<regras>`, `<formato_resposta>`) e medição de tokens com tiktoken.
- **Guardrails** (`src/guardrails/`): moderação anti-jailbreak/injection e validador de escopo GoodWe com recusas que orientam a procurar profissional habilitado.

## 2. Refatoração: decisões e trade-offs

- **Roteamento por palavras-chave** entre conversa livre e consulta estruturada, em vez de classificador por LLM. Decisão: determinístico, sem latência extra e fácil de testar no eval. Trade-off: frases muito fora do padrão podem cair na conversa livre.
- **Poda da memória manual** após cada turno. No LangChain 1.x o `prune()` da `ConversationTokenBufferMemory` foi absorvido pelo `save_context`, que o `RunnableWithMessageHistory` não chama. Reimplementamos a mesma lógica (remove as mensagens mais antigas até caber no teto) contando tokens com tiktoken, porque o contador default do LangChain 1.x puxaria o pacote `transformers` inteiro só pra isso.
- **Base de conhecimento injetada como variável parcial** do template, não por replace na string: as chaves do JSON quebram o template f-string do LangChain (erro real encontrado no desenvolvimento).
- **Stack da Aula 02 mantida apesar de deprecated**: `ConversationTokenBufferMemory` e `RunnableWithMessageHistory` vivem hoje no pacote `langchain-classic`. Mantemos porque é o conteúdo do Módulo 1; a migração pra LangGraph fica pro Módulo 3.

## 3. Comparativo antes/depois

Eval set idêntico (13 casos: happy path, memória 3 turnos, edge cases, jailbreak, out-of-scope) reexecutado nas duas versões. Números abaixo da rodada em modo simulado (pipeline validado, geração determinística). **Substituir pelos números reais do Ollama antes da entrega** (`python evals/run_evals.py --versao lcel` e `--versao legado`).

| Métrica | Sprints 1/2 (manual/legado) | Sprint 03 (LCEL) |
|---------|------------------------------|------------------|
| Qualidade das respostas (nota média no eval, 0-10) | 2,31 | 10,00 _(medir real)_ |
| Tokens por turno (média) | 575,6 | 79,7 _(medir real)_ |
| Latência média por turno | _(medir)_ | _(medir)_ |
| Acurácia do structured output | 0% (parse falhava, JSON vinha misturado com prosa) | 100% _(medir real)_ |
| Recusas corretas (jailbreak + out-of-scope) | 0/6 (sem guardrails) | 6/6 |
| Tokens do system prompt | 80 (v1) | 376 (v2, com base de produtos embutida) |

Dados brutos: `evals/sprint3_results.json`.

O que salta da tabela:

1. **Tokens por turno caem ~7x**: o legado reenviava o histórico inteiro a cada turno; a memória com teto de 1200 tokens poda o passado distante.
2. **Structured output vai de 0% a 100%**: `json.loads` em texto livre quebrava sempre que o modelo misturava prosa com JSON; a chain nova valida contra o schema Pydantic.
3. **Segurança sai de zero**: o legado obedecia jailbreaks; a versão nova recusa os 6 casos de injection/fora de escopo.

## 4. Problemas encontrados e soluções

**Problema 1: JSON da base de conhecimento quebrando o template.** Ao montar o prompt v2 com replace de string, o LangChain interpretava as chaves do JSON como variáveis de template (`ValueError: Invalid format specifier`). Solução: base injetada como variável parcial do `ChatPromptTemplate`, que não reprocessa o conteúdo.

**Problema 2: `prune()` sumiu no LangChain 1.x.** A `ConversationTokenBufferMemory` do `langchain-classic` só poda dentro de `save_context`, que o `RunnableWithMessageHistory` não usa. Solução: poda manual após cada turno com contagem via tiktoken, replicando a lógica original. O eval de memória (3+ turnos) garante que funciona.

**Problema 3: padrões de jailbreak com cobertura parcial.** O eval pegou que "ignore todas as **suas** instruções" escapava da blocklist. Solução: ampliação dos padrões e caso de regressão permanente no eval set (jb01 a jb03).

## 5. Equipe e divisão de trabalho

| Integrante | RM | Tarefa principal |
|------------|-----|------------------|
| Diogo Chiaradia Santos | 570246 | chains LCEL e structured output (`builder.py`, `consulta.py`) |
| Rafael Laprega Gontijo Magalhaes | 561975 | memória por sessão e guardrails (`memoria.py`, `moderation.py`, `scope_validator.py`) |
| Gustavo Torres de Oliveira | 572952 | prompts versionados e eval set (`prompts/`, `eval_set.json`) |
| Lucas Furquim Lima | 568690 | relatórios e chamada multi-provider (`docs/`, `multi_provider.py`) |
