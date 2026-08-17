## Why

O projeto ainda não possui `prompts/bug_to_user_story_v2.yml`, artefato central para transformar relatos de bugs em User Stories melhores que as produzidas pelo prompt v1. Sem essa versão otimizada, o fluxo de publicação e avaliação não pode validar o uso das técnicas exigidas nem perseguir a meta mínima de 0,8 em todas as métricas.

## What Changes

- Criar `prompts/bug_to_user_story_v2.yml` com a chave raiz `bug_to_user_story_v2` e os campos obrigatórios `description`, `system_prompt`, `user_prompt`, `version`, `tags` e `techniques_applied`.
- Definir no `system_prompt` uma persona de Product Manager experiente em análise de bugs, regras explícitas de fidelidade ao relato e instruções adaptáveis a casos simples, médios e complexos.
- Aplicar Few-shot Learning com três exemplos claros de entrada e saída, combinado com Role Prompting e Skeleton of Thought.
- Exigir saída em português brasileiro e Markdown, contendo User Story no formato `Como um..., eu quero..., para que...`, critérios de aceitação testáveis em Dado/Quando/Então e contexto adicional somente quando sustentado pelo relato.
- Separar as instruções permanentes no `system_prompt` da entrada não confiável em `user_prompt`, preservando literalmente a variável `{bug_report}`.
- Tratar relatos vagos, múltiplos problemas relacionados, segurança, performance, integrações, concorrência, sincronização, ausência de informações e tentativas de injeção de instruções sem inventar fatos ou soluções.
- Manter o YAML compatível com PyYAML, LangChain `ChatPromptTemplate`, o script de push e os modelos OpenAI ou Google suportados pelo projeto.

## Capabilities

### New Capabilities

- `prompt-otimizado-v2`: contrato estrutural e comportamental do prompt v2 para converter relatos de bugs em User Stories fiéis, claras, completas e testáveis.

### Modified Capabilities

Nenhuma.

## Impact

- Novo arquivo: `prompts/bug_to_user_story_v2.yml`.
- Fluxos consumidores: validação local, `src/push_prompts.py` e, após publicação autorizada, `src/evaluate.py`.
- Dependências: nenhuma nova; serão usados apenas YAML e o formato de template já aceito pelo LangChain.
- Arquivos protegidos: `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl` permanecerão inalterados.
- Operações externas: criar e validar o YAML é trabalho exclusivamente local. Push público, execução do dataset e avaliação por LLM permanecem fora desta mudança e exigem autorização, rede, credenciais válidas e possível custo de API.
- Evidências: a criação do arquivo não implica nem permite inventar notas, URLs ou resultados; a meta de 0,8 por métrica só poderá ser comprovada em avaliação remota posterior.
