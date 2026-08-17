## Why

O projeto ainda não consegue publicar o prompt otimizado porque `src/push_prompts.py` contém apenas esqueletos. Implementar esse script cria a ponte segura entre o YAML v2 validado localmente e o LangSmith Prompt Hub, etapa necessária antes da avaliação remota.

## What Changes

- Implementar o carregamento de `prompts/bug_to_user_story_v2.yml` e a seleção da entrada `bug_to_user_story_v2`.
- Validar estrutura, campos obrigatórios, versão, templates, ausência de TODOs e mínimo de duas técnicas antes de qualquer chamada de rede.
- Construir um `ChatPromptTemplate` com mensagens distintas de sistema e usuário, preservando variáveis como `{bug_report}`.
- Publicar como `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` por meio de `langchain.hub.push`.
- Solicitar visibilidade pública e enviar descrição, tags e técnicas aplicadas como metadados do prompt.
- Fornecer mensagens de CLI em pt-BR e códigos de saída distintos para configuração ausente, YAML inválido, prompt reprovado, erro remoto e sucesso.
- Adicionar testes unitários com mocks para verificar o payload enviado ao Hub e garantir que entradas inválidas não produzam chamadas externas.

Não há mudança incompatível de interface nem alteração dos arquivos-base protegidos pelo desafio.

## Capabilities

### New Capabilities

- `langsmith-prompt-push`: validação e publicação pública do prompt otimizado v2 no LangSmith Hub, com metadados, tratamento de falhas e comportamento testável.

### Modified Capabilities

Nenhuma. A capacidade de pull existente permanece independente e não tem seus requisitos alterados.

## Impact

- Código principal afetado: `src/push_prompts.py`.
- Testes novos: testes unitários específicos do fluxo de push, sem chamadas reais de rede.
- Entrada local esperada: `prompts/bug_to_user_story_v2.yml`, que pertence a outra entrega e ainda não existe no estado atual.
- Integração externa: LangSmith Prompt Hub por meio de `langchain.hub.push`.
- Configuração necessária: `LANGSMITH_API_KEY` e `USERNAME_LANGSMITH_HUB`.
- Uma execução real cria ou atualiza um recurso público no LangSmith. A publicação externa não será realizada durante a implementação desta mudança sem solicitação explícita e um YAML v2 válido.
- Não há inferência de LLM nem custo de tokens no push, embora a operação dependa de rede, credenciais e limites do LangSmith.
