## Context

O prompt publicado `ricardo-sass/bug_to_user_story_v2`, executado com `gpt-4o-mini` e avaliado por `gpt-4o`, atingiu `Helpfulness` 0,85, `Clarity` 0,88 e `Precision` 0,81, mas ficou com `F1-Score` 0,72 e `Correctness` 0,76. Como `Correctness` é a média de `F1-Score` e `Precision`, o principal caminho de correção é aumentar recall e F1 sem introduzir alucinações que reduzam a precisão.

O dataset protegido contém cinco casos simples, sete médios e três complexos. As referências simples acrescentam comportamentos esperados usuais; as médias incluem prevenção, contexto e critérios técnicos; as complexas cobrem todas as dimensões, soluções recomendadas, tarefas e métricas. O prompt atual instrui respostas curtas e bloqueia soluções não informadas, criando um desalinhamento sistemático com esse padrão de referência.

O fluxo afetado permanece:

`prompts/bug_to_user_story_v2.yml` local → `src/push_prompts.py` → LangSmith Hub → dataset `MBA-eval` → LLM gerador → LLM avaliador → métricas no terminal e traces no LangSmith.

O YAML e os testes locais não dependem de rede. Publicação e avaliação dependem de credenciais, rede e consumo dos modelos configurados, e devem preservar compatibilidade tanto com OpenAI quanto com Google.

## Goals / Non-Goals

**Goals:**

- Elevar `F1-Score` e `Correctness` para pelo menos 0,8, preservando todas as demais métricas e a média geral no mesmo patamar.
- Ensinar o modelo a cobrir todos os fatos e todas as dimensões relevantes do relato antes de redigir a resposta.
- Aproximar estrutura, profundidade e vocabulário das referências conforme a complexidade do bug.
- Equilibrar recall e precisão por meio de uma distinção explícita entre fatos observados, resultados esperados inferíveis e recomendações técnicas.
- Manter o contrato YAML, a única variável `{bug_report}`, as técnicas obrigatórias e a proteção contra injeção de prompt.

**Non-Goals:**

- Alterar `datasets/bug_to_user_story.jsonl`, `src/evaluate.py`, `src/metrics.py` ou `src/utils.py`.
- Trocar modelos, provedores, limiar de aprovação ou fórmula das métricas para obter aprovação artificial.
- Criar nova versão, nova dependência ou novo formato de integração com o LangSmith.
- Declarar notas futuras ou aprovação sem uma execução externa real.

## Decisions

### 1. Otimizar para cobertura com uma matriz interna por complexidade

O `system_prompt` instruirá o modelo a montar silenciosamente uma matriz com ator, objetivo, passos, ambiente, valores, mensagens, endpoints, comportamento observado, comportamento esperado, causa informada, impacto, severidade, erros, limites e dimensões técnicas. Antes da resposta, cada item relevante deverá aparecer na User Story, nos critérios ou no contexto.

Para bugs simples, a saída continuará curta, mas cobrirá o resultado principal e sinais usuais de conclusão ou bloqueio diretamente implicados pela interação. Para bugs médios, serão esperados critérios adicionais ou técnicos e contexto. Para bugs complexos, cada dimensão identificada terá cenário próprio, seguido de critérios técnicos, contexto, tarefas sugeridas e métricas somente quando sustentadas.

Alternativa considerada: tornar toda resposta tão extensa quanto as referências complexas. Foi rejeitada porque prejudicaria `Clarity`, aumentaria custo e produziria ruído nos casos simples.

### 2. Separar conteúdo em três níveis de confiança

- **Fato observado:** deve ser preservado literalmente quando relevante, incluindo números, mensagens e identificadores.
- **Resultado esperado inferível:** pode completar o aceite quando for consequência direta e conservadora do fluxo, como impedir avanço após validação inválida ou apresentar feedback de sucesso/erro.
- **Recomendação técnica:** pode ser proposta em bugs médios e complexos quando houver evidência causal ou uma prática padrão diretamente aplicável; deve aparecer em seção própria e nunca ser descrita como estado atual ou decisão já aprovada.

Valores numéricos, mensagens exatas, prazos, tecnologias e regras de negócio não informados não serão apresentados como fatos. Quando úteis, deverão ser claramente marcados como meta ou recomendação a validar. Essa abordagem substitui a proibição absoluta atual, que protege precisão mas reduz excessivamente o recall.

Alternativa considerada: copiar integralmente soluções típicas das referências. Foi rejeitada por aumentar o risco de alucinação e de queda da `Precision`, que está apenas 0,01 acima do mínimo.

### 3. Usar uma estrutura de saída adaptativa e semanticamente próxima do dataset

Todas as respostas terão User Story e Critérios de Aceitação. Seções condicionais serão acionadas por evidência e complexidade: critérios adicionais de prevenção, critérios técnicos ou de acessibilidade/segurança, exemplo de cálculo, contexto do bug, tarefas técnicas sugeridas e métricas de sucesso. Seções vazias serão proibidas.

Nos relatos multidimensionais, uma história principal agregará o objetivo do usuário e os critérios serão agrupados por dimensão. Histórias separadas só serão usadas quando os problemas não compartilharem um objetivo coerente.

Alternativa considerada: manter apenas `User Story`, `Critérios de Aceitação`, `Contexto do Bug` e `Informações a Confirmar`. Foi rejeitada porque não demonstra ao avaliador parte relevante do conteúdo esperado nos casos médios e complexos.

### 4. Substituir os few-shots por exemplos de calibração de cobertura

Os três exemplos continuarão sintéticos e cobrirão níveis simples, médio e complexo, mas passarão a demonstrar explicitamente:

- no simples, resultado funcional, feedback e estado da interface;
- no médio, critérios de erro/prevenção, contexto e recomendação técnica rastreável;
- no complexo, cobertura por dimensão, critérios técnicos, tarefas e métricas baseadas somente nos dados da entrada.

Os exemplos usarão o mesmo esqueleto pedido na saída e evitarão chaves literais que possam ser interpretadas como variáveis pelo LangChain.

Alternativa considerada: acrescentar muitos exemplos especializados. Foi rejeitada para limitar tokens, custo e diluição das instruções principais no modelo gerador compacto.

### 5. Validar localmente o contrato e remotamente a qualidade

Os testes locais continuarão verificando parsing YAML, persona, formato, few-shot, ausência de TODOs e técnicas. Serão acrescentadas verificações determinísticas para a matriz de cobertura, os níveis de confiança, as seções adaptativas e a presença de ao menos um few-shot com conteúdo técnico e multidimensional.

A qualidade semântica continuará sendo validada exclusivamente pelo fluxo existente: publicar, executar os 15 exemplos e conferir cada métrica. Se houver reprovação, os traces e os scores por exemplo orientarão uma mudança pequena por iteração, priorizando casos com F1 abaixo de 0,8 e monitorando regressões de precisão e clareza.

Não será criada lógica específica para OpenAI ou Google; as instruções permanecerão em linguagem natural compatível com ambos.

## Risks / Trade-offs

- **[Mais cobertura reduzir `Precision`]** → separar fatos de recomendações, proibir detalhes arbitrários e acompanhar exemplos que hoje apresentam precisão 0,67.
- **[Respostas maiores reduzir `Clarity`]** → impor profundidade proporcional, títulos por dimensão e ausência de repetição.
- **[Few-shots dominarem a resposta]** → usar exemplos sintéticos de domínios distintos e regras gerais de cobertura, sem copiar entradas do dataset.
- **[Otimização excessiva ao dataset]** → orientar por categorias e padrões semânticos, mantendo testes de fidelidade e a proibição de alterar referências ou avaliadores.
- **[Variação entre execuções ou provedores]** → manter temperatura zero no fluxo existente, exigir os mesmos limiares e registrar modelo/provedor junto à evidência.
- **[Custo e latência de múltiplas avaliações]** → executar primeiro todos os testes locais e limitar a calibração externa a no máximo cinco iterações orientadas por evidência.
- **[Falha de rede, autenticação ou LangSmith]** → interromper a etapa externa com mensagem acionável, sem interpretar falha operacional como reprovação do prompt e sem expor credenciais.

## Migration Plan

1. Atualizar o YAML e os testes localmente, preservando a versão `v2` e a variável `{bug_report}`.
2. Executar parsing, construção do `ChatPromptTemplate` e `pytest tests/test_prompts.py` sem rede.
3. Revisar o diff para confirmar que arquivos protegidos e segredos não foram alterados.
4. Publicar a revisão com `python src/push_prompts.py` usando credenciais válidas.
5. Executar `python src/evaluate.py`, registrar as cinco métricas, a média, o modelo, o provedor e a evidência do LangSmith.
6. Se qualquer métrica ficar abaixo de 0,8, analisar os piores exemplos e repetir uma alteração focal, o push e a avaliação, limitado a cinco iterações.
7. Em caso de regressão material, restaurar pelo histórico do Git o YAML anterior, republicá-lo e manter a execução reprovada como evidência da tentativa; nenhuma migração de dados é necessária.

## Open Questions

- O terminal atual mostra apenas scores por exemplo, sem o raciocínio do avaliador. Durante a aplicação, os traces do LangSmith deverão ser usados para distinguir omissão de conteúdo, divergência de formato e penalização por recomendação inventada.
- Caso `F1-Score` suba e `Precision` caia abaixo de 0,8, a primeira calibração deverá reduzir recomendações não rastreáveis antes de remover cobertura factual ou critérios de erro.
