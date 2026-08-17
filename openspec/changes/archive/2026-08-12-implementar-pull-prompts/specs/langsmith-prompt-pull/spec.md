## ADDED Requirements

### Requirement: Validar a configuração do LangSmith
O comando **DEVE** (`SHALL`) verificar se `LANGSMITH_API_KEY` está configurada e não vazia antes de realizar qualquer acesso ao LangSmith Hub.

#### Scenario: Credencial disponível
- **WHEN** o comando é iniciado com `LANGSMITH_API_KEY` preenchida
- **THEN** o sistema prossegue para a obtenção do prompt remoto

#### Scenario: Credencial ausente
- **WHEN** o comando é iniciado sem `LANGSMITH_API_KEY` ou com valor vazio
- **THEN** o sistema informa em pt-BR qual configuração está ausente, não chama o LangSmith Hub e encerra com código diferente de zero

### Requirement: Obter o prompt inicial versionado
O sistema **DEVE** (`SHALL`) solicitar exatamente `leonanluppi/bug_to_user_story_v1` por meio de `langchain.hub.pull`, reutilizando a configuração de ambiente reconhecida pelo LangChain e sem registrar credenciais.

#### Scenario: Prompt remoto disponível
- **WHEN** o LangSmith Hub retorna o prompt solicitado
- **THEN** o sistema encaminha o objeto retornado para extração e persistência local

#### Scenario: Serviço externo indisponível
- **WHEN** o LangSmith Hub retorna erro de autenticação, autorização, recurso inexistente, rede ou serviço
- **THEN** o sistema exibe uma mensagem acionável em pt-BR, não informa sucesso e encerra com código diferente de zero

### Requirement: Extrair as mensagens do prompt com segurança
O sistema **DEVE** (`SHALL`) extrair os templates de sistema e de usuário a partir dos papéis das mensagens de um `ChatPromptTemplate`, preservando integralmente o texto e as variáveis do template, como `{bug_report}`.

#### Scenario: Estrutura compatível
- **WHEN** o objeto remoto contém uma mensagem de sistema e uma mensagem de usuário com templates textuais
- **THEN** o sistema obtém ambos os textos sem renderizar, interpolar ou alterar suas variáveis

#### Scenario: Papel obrigatório ausente
- **WHEN** o objeto remoto não contém mensagem de sistema ou não contém mensagem de usuário
- **THEN** o sistema rejeita a estrutura, informa incompatibilidade sem expor dados sensíveis e não grava um novo YAML

#### Scenario: Papel obrigatório duplicado
- **WHEN** o objeto remoto contém mais de uma mensagem de sistema ou mais de uma mensagem de usuário
- **THEN** o sistema rejeita a estrutura ambígua e não concatena nem descarta mensagens silenciosamente

#### Scenario: Tipo de prompt incompatível
- **WHEN** o Hub retorna um objeto que não oferece a estrutura textual esperada de `ChatPromptTemplate`
- **THEN** o sistema trata a resposta como erro controlado e encerra com código diferente de zero

### Requirement: Persistir o contrato YAML local
O sistema **DEVE** (`SHALL`) salvar o resultado em `prompts/bug_to_user_story_v1.yml`, em UTF-8, sob a chave de nível superior `bug_to_user_story_v1`, usando `save_yaml` e incluindo `description`, `system_prompt`, `user_prompt`, `version`, `source` e `tags`.

#### Scenario: Persistência concluída
- **WHEN** a extração produz os templates obrigatórios e `save_yaml` conclui a escrita
- **THEN** o arquivo contém `version: v1`, `source: leonanluppi/bug_to_user_story_v1`, os templates extraídos e metadados adequados ao domínio de bug para User Story

#### Scenario: Diretório local ausente
- **WHEN** o diretório `prompts/` ainda não existe
- **THEN** o sistema permite que o utilitário de persistência crie o diretório e conclui a gravação no caminho esperado

#### Scenario: Falha de persistência
- **WHEN** `save_yaml` não consegue gravar o arquivo
- **THEN** o sistema informa a falha em pt-BR, não informa sucesso e encerra com código diferente de zero

### Requirement: Comunicar o resultado pela CLI
O comando **DEVE** (`SHALL`) apresentar um cabeçalho e mensagens de progresso em pt-BR, retornar código `0` somente quando o pull e a persistência forem concluídos e retornar código diferente de zero em qualquer falha.

#### Scenario: Execução bem-sucedida
- **WHEN** validação, pull, extração e persistência terminam sem erro
- **THEN** o comando informa o nome remoto e o caminho local, confirma a conclusão e retorna código `0`

#### Scenario: Execução malsucedida
- **WHEN** qualquer etapa obrigatória falha
- **THEN** o comando apresenta contexto suficiente para correção, omite chaves e tokens e retorna código diferente de zero
