## Purpose

Definir a validação e a publicação pública do prompt otimizado v2 no LangSmith Hub, incluindo metadados e tratamento de falhas.

## Requirements

### Requirement: Validar a configuração para publicação
O comando **DEVE** (`SHALL`) verificar se `LANGSMITH_API_KEY` e `USERNAME_LANGSMITH_HUB` estão configuradas e não vazias antes de realizar qualquer chamada ao LangSmith Hub.

#### Scenario: Configuração disponível
- **WHEN** ambas as variáveis obrigatórias estão preenchidas
- **THEN** o sistema prossegue para carregar e validar o prompt local

#### Scenario: Configuração incompleta
- **WHEN** uma ou ambas as variáveis obrigatórias estão ausentes ou vazias
- **THEN** o sistema informa em pt-BR quais variáveis faltam, não chama o LangSmith Hub e encerra com código diferente de zero

### Requirement: Carregar o prompt otimizado local
O sistema **DEVE** (`SHALL`) carregar `prompts/bug_to_user_story_v2.yml` com `load_yaml` e selecionar uma única entrada de nível superior chamada `bug_to_user_story_v2`.

#### Scenario: YAML disponível e selecionável
- **WHEN** o arquivo existe, é um mapeamento YAML válido e contém `bug_to_user_story_v2` como mapeamento
- **THEN** o sistema encaminha os dados internos para validação sem modificá-los

#### Scenario: Arquivo ausente ou YAML inválido
- **WHEN** o arquivo não existe, está vazio ou não pode ser interpretado como YAML
- **THEN** o sistema informa a falha local, não chama o LangSmith Hub e encerra com código diferente de zero

#### Scenario: Chave v2 ausente ou inválida
- **WHEN** o documento não contém `bug_to_user_story_v2` ou o valor dessa chave não é um mapeamento
- **THEN** o sistema informa o contrato esperado, não chama o LangSmith Hub e encerra com código diferente de zero

### Requirement: Validar o contrato do prompt v2
Antes da publicação, o sistema **DEVE** (`SHALL`) exigir `description`, `system_prompt`, `user_prompt`, `version`, `tags` e `techniques_applied`; os textos obrigatórios devem ser não vazios, `version` deve ser `v2`, `tags` deve conter strings válidas, `techniques_applied` deve listar no mínimo duas técnicas e nenhum template pode conter `TODO` ou `[TODO]`.

#### Scenario: Prompt v2 válido
- **WHEN** todos os campos, tipos, valores e metadados satisfazem o contrato e `user_prompt` contém `{bug_report}`
- **THEN** a validação retorna sucesso e não produz erros

#### Scenario: Campos obrigatórios ausentes ou vazios
- **WHEN** qualquer texto obrigatório está ausente, vazio ou possui tipo incompatível
- **THEN** a validação retorna falha com um erro específico para cada problema encontrado

#### Scenario: Metadados insuficientes
- **WHEN** a versão não é `v2`, as tags são inválidas ou há menos de duas técnicas declaradas
- **THEN** a validação retorna falha e o prompt não é publicado

#### Scenario: Variável de entrada ausente
- **WHEN** `user_prompt` não contém literalmente `{bug_report}`
- **THEN** a validação retorna falha para impedir um prompt incapaz de receber os exemplos do dataset

#### Scenario: Marcador pendente
- **WHEN** `system_prompt` ou `user_prompt` contém `TODO` ou `[TODO]`
- **THEN** a validação retorna falha e o prompt não é publicado

### Requirement: Construir o ChatPromptTemplate preservando papéis
O sistema **DEVE** (`SHALL`) construir um `ChatPromptTemplate` com `system_prompt` como mensagem de sistema e `user_prompt` como mensagem humana, preservando as variáveis declaradas no YAML.

#### Scenario: Templates compatíveis com LangChain
- **WHEN** os dois templates são textuais e possuem sintaxe aceita pelo LangChain
- **THEN** o sistema cria o `ChatPromptTemplate` com os papéis na ordem sistema e usuário

#### Scenario: Sintaxe de template incompatível
- **WHEN** o LangChain rejeita chaves, variáveis ou outra sintaxe do template
- **THEN** o sistema informa erro de construção, não chama `hub.push` e encerra com código diferente de zero

### Requirement: Publicar o prompt v2 com metadados
O sistema **DEVE** (`SHALL`) publicar por `hub.push` no identificador `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2`, solicitar visibilidade pública e enviar descrição, tags e técnicas aplicadas sem incluir credenciais.

#### Scenario: Primeira publicação bem-sucedida
- **WHEN** o prompt local é válido e o LangSmith aceita a criação
- **THEN** o sistema envia `new_repo_is_public=True`, descrição, tags e um README com as técnicas aplicadas, exibe a URL retornada e informa sucesso

#### Scenario: Atualização bem-sucedida
- **WHEN** o identificador público já existe e o LangSmith aceita uma nova versão
- **THEN** o sistema atualiza o prompt no mesmo identificador, mantém a solicitação de visibilidade pública e exibe a URL retornada

#### Scenario: Falha do serviço externo
- **WHEN** o LangSmith retorna erro de autenticação, autorização, nome, rede ou serviço
- **THEN** o sistema exibe uma mensagem acionável em pt-BR, não expõe chaves ou tokens, não informa sucesso e encerra com código diferente de zero

### Requirement: Comunicar o resultado pela CLI
O comando **DEVE** (`SHALL`) apresentar cabeçalho, caminho local e identificador remoto em pt-BR, retornar código `0` somente após publicação confirmada e retornar código diferente de zero para qualquer falha anterior ou externa.

#### Scenario: Execução concluída
- **WHEN** configuração, carregamento, validação, construção e publicação terminam sem erro
- **THEN** o comando retorna `0` e informa a URL pública produzida pelo LangSmith

#### Scenario: Execução interrompida por validação
- **WHEN** o prompt local possui um ou mais erros
- **THEN** o comando lista todos os erros encontrados, não realiza publicação e retorna código diferente de zero
