## Why

O fluxo do desafio não consegue obter o prompt inicial porque `src/pull_prompts.py` ainda contém apenas reticências. Implementar esse script é necessário para autenticar no LangSmith, baixar a versão v1 definida pelo projeto e materializá-la localmente como ponto de partida reproduzível para a otimização.

## What Changes

- Implementar o fluxo de pull de `leonanluppi/bug_to_user_story_v1` por meio de `langchain.hub`.
- Validar a presença de `LANGSMITH_API_KEY` antes de acessar o serviço externo.
- Extrair do objeto retornado pelo Hub as mensagens de sistema e de usuário sem acoplar a implementação a conteúdo específico do prompt.
- Serializar o prompt no contrato YAML esperado e salvá-lo em `prompts/bug_to_user_story_v1.yml` usando o utilitário existente.
- Fornecer mensagens de CLI em pt-BR e códigos de saída distintos para sucesso e falha, sem expor credenciais.
- Adicionar testes unitários locais com mocks para cobrir sucesso, configuração ausente, erro do Hub, formato incompatível e falha de persistência.

Não há mudança incompatível de interface nem alteração dos arquivos-base protegidos pelo desafio.

## Capabilities

### New Capabilities

- `langsmith-prompt-pull`: obtenção autenticada de um prompt versionado no LangSmith Hub, conversão para o YAML local do projeto e tratamento verificável de falhas.

### Modified Capabilities

Nenhuma. O projeto ainda não possui especificações consolidadas.

## Impact

- Código principal afetado: `src/pull_prompts.py`.
- Testes novos ou ampliados: testes unitários específicos do fluxo de pull, sem chamadas reais de rede.
- Recurso local escrito em execução: `prompts/bug_to_user_story_v1.yml`.
- Integrações: LangSmith Prompt Hub por meio de `langchain.hub.pull`.
- Configuração necessária: `LANGSMITH_API_KEY`; valores opcionais de endpoint e tracing continuam sob responsabilidade do LangSmith/LangChain.
- A execução real depende de rede e de credenciais válidas e pode estar sujeita aos limites do serviço externo, mas não envolve provedor de LLM nem custo de inferência.
