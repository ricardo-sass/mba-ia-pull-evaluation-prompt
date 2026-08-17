## Context

`src/push_prompts.py` contém as assinaturas de `validate_prompt()`, `push_prompt_to_langsmith()` e `main()`, porém seus corpos ainda são esqueletos. O script deve transformar o documento local `bug_to_user_story_v2.yml` em um `ChatPromptTemplate`, publicar uma versão pública no namespace do aluno e fornecer metadados suficientes para identificação no LangSmith.

O fluxo se posiciona entre a otimização local e a avaliação remota:

```text
prompts/bug_to_user_story_v2.yml
   │ load_yaml + seleção + validação
   ▼
ChatPromptTemplate (system + human)
   │ hub.push público + descrição + tags + técnicas
   ▼
LangSmith Prompt Hub
   │ fonte de verdade consumida por src/evaluate.py
   ▼
Dataset → LLM gerador → métricas por LLM avaliador
```

O arquivo v2 ainda não existe no repositório. Por isso, a implementação e os testes podem ser concluídos com dados sintéticos, mas uma publicação real exige outra entrega, credenciais válidas, rede e autorização explícita para criar ou atualizar um recurso público.

## Goals / Non-Goals

**Goals:**

- Implementar o comando de push com códigos de saída confiáveis e mensagens em pt-BR.
- Bloquear qualquer acesso externo quando ambiente, arquivo ou prompt forem inválidos.
- Preservar a separação entre papéis de sistema e usuário no objeto publicado.
- Publicar sempre no nome versionado `{username}/bug_to_user_story_v2` e solicitar visibilidade pública.
- Enviar descrição, tags e técnicas aplicadas usando os parâmetros suportados pela versão fixada de `hub.push`.
- Reutilizar `load_yaml`, `check_env_vars`, `print_section_header` e a validação estrutural existente.
- Cobrir o fluxo com testes unitários determinísticos e sem rede.

**Non-Goals:**

- Criar ou otimizar `prompts/bug_to_user_story_v2.yml`.
- Executar uma publicação pública real durante a aplicação desta mudança sem autorização adicional.
- Avaliar o prompt, executar LLMs ou garantir notas mínimas de 0,8.
- Alterar `src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou o dataset.
- Implementar rollback remoto, exclusão de versões, retries automáticos ou múltiplos prompts por execução.
- Tornar caminho, chave YAML ou sufixo remoto configuráveis nesta versão.

## Decisions

### 1. Manter caminho, chave e sufixo remoto como constantes

`prompts/bug_to_user_story_v2.yml`, `bug_to_user_story_v2` e `bug_to_user_story_v2` serão constantes do módulo. `USERNAME_LANGSMITH_HUB` fornecerá somente o namespace, resultando em um identificador previsível e alinhado ao avaliador.

Alternativa considerada: aceitar argumentos de CLI. Foi descartada porque o desafio define um único artefato e o suporte genérico aumentaria a chance de publicar no nome errado.

### 2. Compor a validação em duas camadas

`validate_prompt()` reutilizará `validate_prompt_structure()` para as regras comuns e acrescentará as regras específicas do v2: `user_prompt`, versão exata, tipos, tags, duas técnicas, `{bug_report}` e ausência de TODOs nos dois templates. A função acumulará todos os erros em vez de interromper no primeiro.

Alternativa considerada: duplicar toda a validação dentro do script. Foi descartada para aproveitar a regra central existente, mantendo verificações adicionais próximas da integração que depende delas.

### 3. Construir o prompt somente depois da validação

`ChatPromptTemplate.from_messages()` receberá primeiro `("system", system_prompt)` e depois `("human", user_prompt)`. Erros de sintaxe serão tratados antes de `hub.push`. A variável `{bug_report}` não será renderizada durante o push.

Alternativa considerada: publicar diretamente os dados YAML. Foi descartada porque o Hub espera um objeto LangChain serializável e a avaliação posterior compõe esse objeto com o LLM.

### 4. Representar técnicas nos metadados suportados pelo Hub

`hub.push` receberá:

- `new_repo_is_public=True` para criar ou manter o prompt público;
- `new_repo_description` com `description`;
- `tags` com a união ordenada e sem duplicatas entre tags e técnicas;
- `readme` em pt-BR listando versão e técnicas aplicadas.

Na versão instalada, `hub.push` encaminha esses campos ao cliente LangSmith, inclusive `is_public`. Isso evita adicionar uma dependência ou cliente paralelo apenas para visibilidade.

Alternativa considerada: guardar técnicas apenas na descrição. Foi descartada porque mistura resumo funcional com rastreabilidade metodológica e dificulta filtragem por tags.

### 5. Separar responsabilidades das três funções existentes

- `validate_prompt()` será pura e retornará `(válido, erros)`.
- `push_prompt_to_langsmith()` construirá o objeto, preparará metadados, chamará o Hub e retornará sucesso ou falha.
- `main()` validará ambiente, carregará e selecionará o YAML, exibirá erros, formará o nome remoto e converterá o resultado em código de saída.

Essa separação mantém o estilo do script de pull e permite mocks pequenos nos testes.

### 6. Resumir erros externos sem reproduzir exceções

Falhas de construção do template terão mensagens controladas sobre sintaxe. Falhas do Hub terão orientação sobre credencial, nome, acesso e conexão, sem imprimir a exceção original, que pode conter detalhes sensíveis. Uma URL só será mostrada quando `hub.push` retornar com sucesso.

Não haverá retry automático: erros de autenticação e validação não são transitórios, e repetir uma operação de escrita pode produzir versões adicionais ou dificultar o diagnóstico.

### 7. Testar todas as fronteiras com mocks

Os testes usarão dados v2 sintéticos e um `ChatPromptTemplate` real para inspecionar papéis e templates. `load_yaml`, `check_env_vars` e `hub.push` serão mockados conforme o cenário. Serão verificados parâmetros de visibilidade, descrição, README, tags/técnicas, nome remoto, URL, códigos de saída e ausência de chamadas externas para entradas inválidas.

## Risks / Trade-offs

- [O YAML v2 ainda não existe] → Testar com fixtures sintéticas e fazer o comando falhar de forma acionável até a outra entrega criar o arquivo.
- [Publicação acidental de conteúdo inválido] → Validar integralmente antes de construir ou chamar o Hub e testar que falhas não atravessam essa barreira.
- [Prompt existente com visibilidade diferente] → Enviar `new_repo_is_public=True` em toda publicação e exigir verificação posterior no dashboard quando a operação real for autorizada.
- [Tags e técnicas duplicadas] → Deduplicar preservando ordem antes de enviar metadados.
- [Chaves literais de exemplos few-shot são interpretadas como variáveis] → Tratar erros do `ChatPromptTemplate` e exigir correção/escape no YAML, sem reescrever silenciosamente o conteúdo.
- [Falha externa após validação local] → Retornar erro sem afirmar sucesso; o usuário pode consultar o Hub antes de tentar novamente.
- [Dependência futura altera parâmetros de `hub.push`] → Cobrir a assinatura usada por testes e manter as versões fixadas em `requirements.txt`.

## Migration Plan

1. Implementar constantes, validação, construção do template, metadados e orquestração em `src/push_prompts.py`.
2. Adicionar testes unitários sem rede e executar toda a suíte local.
3. Após existir um v2 válido e haver autorização explícita, executar `python src/push_prompts.py` em ambiente autenticado.
4. Verificar no dashboard do LangSmith nome, visibilidade pública, conteúdo, tags, técnicas e URL antes de iniciar `src/evaluate.py`.

Rollback local: reverter `src/push_prompts.py` e os testes adicionados. Rollback remoto não faz parte desta mudança; uma publicação real cria histórico no LangSmith e deve ser tratada conscientemente pelo responsável do workspace.

## Open Questions

Nenhuma questão bloqueante para implementar o script e seus testes. A publicação real permanece deliberadamente condicionada à existência do YAML v2 e à autorização para modificar o LangSmith.
