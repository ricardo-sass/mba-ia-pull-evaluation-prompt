## 1. Recalibração local do prompt

- [x] 1.1 Atualizar `system_prompt` em `prompts/bug_to_user_story_v2.yml` com a matriz interna de cobertura de fatos, lacunas e dimensões técnicas.
- [x] 1.2 Implementar no `system_prompt` os três níveis de confiança — fato observado, resultado inferível e recomendação técnica — com regras explícitas contra detalhes arbitrários.
- [x] 1.3 Substituir o formato atual pela estrutura adaptativa para bugs simples, médios e complexos, incluindo seções condicionais e proibindo seções vazias.
- [x] 1.4 Reescrever os três exemplos few-shot sintéticos para demonstrar cobertura crescente, critérios de erro ou prevenção, contexto, recomendações rastreáveis e organização multidimensional.
- [x] 1.5 Revisar `description`, `tags` e `techniques_applied` para que continuem coerentes com as técnicas efetivamente implementadas, preservando `version: v2` e a única variável `{bug_report}`.

## 2. Testes automatizados e validação local

- [x] 2.1 Acrescentar a `tests/test_prompts.py` verificações determinísticas da matriz de cobertura, dos níveis de confiança e da estrutura de saída adaptativa.
- [x] 2.2 Acrescentar teste que confirme três pares `Entrada`/`Saída` e conteúdo técnico ou multidimensional nos few-shots sem criar variáveis extras no `ChatPromptTemplate`.
- [x] 2.3 Executar o parsing YAML e construir localmente o `ChatPromptTemplate`, confirmando que somente `bug_report` é exigida.
- [x] 2.4 Executar `pytest tests/test_prompts.py` e corrigir todas as falhas sem acessar serviços externos.
- [x] 2.5 Revisar o diff para confirmar que `datasets/bug_to_user_story.jsonl`, `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e arquivos de segredos permaneceram inalterados.

## 3. Publicação externa no LangSmith

- [x] 3.1 Verificar a presença das variáveis de ambiente necessárias sem imprimir valores, tokens ou o conteúdo de `.env`.
- [x] 3.2 Executar `python src/push_prompts.py` e registrar evidência real da nova revisão pública de `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2`.
- [x] 3.3 Confirmar por pull ou inspeção do Hub que a revisão publicada corresponde ao YAML local antes da avaliação.

## 4. Avaliação e calibração orientada por métricas

- [x] 4.1 Executar `python src/evaluate.py` sobre os 15 exemplos e registrar scores por caso, as cinco métricas agregadas, média geral, provedor e modelos utilizados.
- [x] 4.2 Confirmar que Helpfulness, Correctness, F1-Score, Clarity, Precision e média geral são individualmente maiores ou iguais a 0,8.
- [x] 4.3 Se houver reprovação, inspecionar scores e traces dos piores casos, identificar se a causa é omissão, divergência de formato ou recomendação imprecisa e aplicar uma única calibração focal no YAML.
- [x] 4.4 Para cada calibração necessária, repetir validação local, push e avaliação, preservando evidências reais e limitando o processo a cinco iterações.

## 5. Evidências e encerramento

- [x] 5.1 Atualizar o `README.md` com as técnicas revisadas, o resultado final real, a comparação com o baseline reprovado e o link público do LangSmith, sem inventar notas ou URLs.
- [x] 5.2 Executar novamente `pytest tests/test_prompts.py` após a documentação e conferir o estado final do repositório.
- [x] 5.3 Registrar eventual falha operacional de rede, credencial, quota ou provedor separadamente de uma reprovação de qualidade e deixar pendente qualquer tarefa externa sem evidência.

## Registro de execução

- Em 12/08/2026, as variáveis obrigatórias foram verificadas sem exposição de valores.
- A execução de `python src/push_prompts.py` não alcançou o LangSmith porque o ambiente não resolveu `api.smith.langchain.com` (`NameResolutionError`).
- A ocorrência foi classificada como falha operacional de rede/DNS, não como reprovação de qualidade. As tarefas 3.2 em diante que dependem do LangSmith permanecem pendentes até uma execução com acesso à rede.
- A publicação externa foi concluída posteriormente pelo usuário: `https://smith.langchain.com/prompts/bug_to_user_story_v2/444daae3?organizationId=e0fd265c-0aee-43d8-8668-dad594379148`.
- Iteração 1 da mudança, com gerador `gpt-4o-mini` e avaliador `gpt-4o`: F1 por caso = `0,75; 0,75; 0,87; 0,69; 0,65; 0,75; 0,95; 0,65; 0,65; 0,65; 0,80; 0,69; 1,00; 0,89; 0,75`.
- Métricas agregadas da iteração 1: Helpfulness `0,87`, Correctness `0,81`, F1-Score `0,76`, Clarity `0,88`, Precision `0,86` e média geral `0,8399`. Resultado: reprovado apenas em F1-Score.
- Calibração focal 2 aplicada em `prompts/bug_to_user_story_v2.yml`: mapa de cobertura por padrão para UI, validação, responsividade, dashboard, integração, autorização, cálculo, performance, estoque, modal e sincronização offline. Validação local: `8 passed`; variável do template: somente `bug_report`.
- Iteração 2, com gerador `gpt-4o-mini` e avaliador `gpt-4o`: F1 por caso = `0,87; 0,75; 0,87; 0,58; 0,75; 0,75; 0,90; 0,75; 0,65; 0,65; 0,80; 0,65; 0,89; 1,00; 1,00`.
- Métricas agregadas da iteração 2: Helpfulness `0,87`, Correctness `0,82`, F1-Score `0,79` (média não arredondada aproximada `0,7907`), Clarity `0,90`, Precision `0,85` e média geral `0,8446`. Resultado: reprovado apenas em F1-Score.
- Calibração focal 3 aplicada: formato mais completo para bugs simples, few-shot sintético de contagem e microtemplates para cálculo, lista Android e modal, sem expandir as regras de relatos complexos. Validação local: `8 passed`; três pares few-shot; variável do template: somente `bug_report`.
- Iteração 3, com gerador `gpt-4o-mini` e avaliador `gpt-4o`: F1 por caso = `0,75; 0,75; 0,80; 0,58; 0,75; 0,85; 0,90; 0,65; 0,65; 0,65; 0,75; 0,69; 0,90; 0,80; 0,69`.
- Métricas agregadas da iteração 3: Helpfulness `0,86`, Correctness `0,78`, F1-Score `0,74`, Clarity `0,89`, Precision `0,83` e média geral `0,8194`. Resultado: regressão em F1-Score e Correctness.
- Calibração focal 4 aplicada: restauração da base da iteração 2 e uma única regra global de completude, com resultados funcionais afirmativos e uso excepcional de `Informações a Confirmar`. Validação local: `8 passed`; três pares few-shot; variável do template: somente `bug_report`.
- Iteração 4, com gerador `gpt-4o-mini` e avaliador `gpt-4o`: F1 por caso = `0,75; 0,75; 0,87; 0,65; 0,75; 0,75; 0,90; 0,65; 0,65; 0,65; 0,69; 0,80; 1,00; 0,80; 0,75`.
- Métricas agregadas da iteração 4: Helpfulness `0,87`, Correctness `0,81`, F1-Score `0,76`, Clarity `0,89`, Precision `0,86` e média geral `0,8370`. Resultado: reprovado apenas em F1-Score.
- Calibração focal 5 aplicada: remoção da regra global da iteração 4 e inclusão, após o relato, de um checklist de recall restrito aos padrões com pior recorrência — contagem, autorização, cálculo, lista Android, estoque e sincronização offline — preservando as instruções de fidelidade e a separação entre critérios e recomendações. Validação local: `8 passed`; três pares few-shot; variável do template: somente `bug_report`; arquivos protegidos sem diff.
- Iteração 5, com provider `openai`, gerador `gpt-4o-mini` e avaliador `gpt-4o`: F1 por caso = `0,87; 0,65; 0,87; 0,75; 0,75; 0,90; 1,00; 0,85; 0,65; 0,65; 0,85; 0,69; 0,89; 0,80; 1,00`.
- Métricas agregadas da iteração 5: Helpfulness `0,87`, Correctness `0,83`, F1-Score `0,81`, Clarity `0,89`, Precision `0,85` e média geral `0,8526`. Resultado: aprovado, com todas as métricas e a média geral maiores ou iguais a `0,8`.
- Evidência da avaliação: `https://smith.langchain.com/projects/MBA`.
- Encerramento local: `pytest -q tests/test_prompts.py` com `8 passed`; mudança OpenSpec válida em modo estrito; `git diff --check` sem erros; nenhum diff em `datasets/bug_to_user_story.jsonl`, `src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou `.env`. O arquivo não rastreado `README copy.md` já presente no estado final foi preservado sem alteração.
