## Purpose

Definir a validação automatizada local dos requisitos estruturais e das técnicas declaradas no prompt otimizado.

## Requirements

### Requirement: Carregamento do prompt local

A suíte **DEVE** (`SHALL`) carregar em UTF-8 o arquivo YAML de prompt otimizado adotado pelo fluxo local, selecionar a entrada configurada e exigir que tanto a raiz quanto o conteúdo selecionado sejam mapeamentos.

#### Scenario: Prompt local carregado com sucesso
- **WHEN** o arquivo existe, contém YAML válido e possui a entrada configurada como mapeamento
- **THEN** os seis testes recebem os mesmos dados selecionados para executar suas validações

#### Scenario: Arquivo ou entrada inválida
- **WHEN** o arquivo está ausente, o YAML é inválido, a chave esperada não existe ou seu valor não é um mapeamento
- **THEN** a suíte falha localmente com uma mensagem que identifica o problema de carregamento ou seleção

### Requirement: Presença do prompt de sistema

A suíte **DEVE** (`SHALL`) verificar que `system_prompt` existe, é uma string e contém texto após a remoção de espaços periféricos.

#### Scenario: Prompt de sistema preenchido
- **WHEN** `system_prompt` contém texto significativo
- **THEN** `test_prompt_has_system_prompt` é aprovado

#### Scenario: Prompt de sistema ausente ou vazio
- **WHEN** `system_prompt` não existe, não é uma string ou contém apenas espaços
- **THEN** `test_prompt_has_system_prompt` falha com uma mensagem acionável em pt-BR

### Requirement: Definição explícita de persona

A suíte **DEVE** (`SHALL`) verificar, sem distinção entre maiúsculas e minúsculas, que `system_prompt` instrui explicitamente o modelo a assumir uma persona ou papel adequado.

#### Scenario: Persona definida
- **WHEN** o texto contém uma construção explícita como `Você é`, `Atue como` ou equivalente aceito pela suíte
- **THEN** `test_prompt_has_role_definition` é aprovado

#### Scenario: Persona ausente
- **WHEN** o texto apenas descreve a tarefa sem atribuir uma persona ou papel ao modelo
- **THEN** `test_prompt_has_role_definition` falha e informa a necessidade de definir a persona

### Requirement: Formato de saída exigido

A suíte **DEVE** (`SHALL`) verificar que `system_prompt` exige explicitamente uma saída em Markdown ou no formato canônico de User Story com os componentes `Como um`, `eu quero` e `para que`.

#### Scenario: Formato declarado
- **WHEN** o prompt exige Markdown ou apresenta todos os componentes do formato canônico de User Story
- **THEN** `test_prompt_mentions_format` é aprovado

#### Scenario: Formato não declarado
- **WHEN** o prompt solicita uma resposta sem definir qualquer um dos formatos aceitos
- **THEN** `test_prompt_mentions_format` falha com indicação do formato esperado

### Requirement: Exemplos few-shot verificáveis

A suíte **DEVE** (`SHALL`) verificar que `system_prompt` contém exemplos few-shot identificáveis, com pelo menos uma entrada e sua saída correspondente.

#### Scenario: Exemplo de entrada e saída presente
- **WHEN** o texto contém marcadores ou seções inequívocas de exemplo, entrada e saída
- **THEN** `test_prompt_has_few_shot_examples` é aprovado

#### Scenario: Menção sem exemplo completo
- **WHEN** o texto apenas menciona Few-shot Learning ou a palavra exemplo sem apresentar entrada e saída
- **THEN** `test_prompt_has_few_shot_examples` falha e informa que um par completo é obrigatório

### Requirement: Ausência de marcadores TODO

A suíte **NÃO DEVE** (`MUST NOT`) aceitar `TODO` ou `[TODO]`, independentemente de caixa, nos campos textuais do prompt.

#### Scenario: Textos finalizados
- **WHEN** os campos textuais não contêm marcadores TODO
- **THEN** `test_prompt_no_todos` é aprovado

#### Scenario: Pendência em qualquer template
- **WHEN** `system_prompt`, `user_prompt` ou outro campo textual contém uma variante de TODO
- **THEN** `test_prompt_no_todos` falha e identifica que há conteúdo pendente

### Requirement: Mínimo de técnicas válidas

A suíte **DEVE** (`SHALL`) exigir que `techniques_applied` seja uma lista com pelo menos duas strings não vazias, sem considerar valores inválidos na contagem.

#### Scenario: Duas ou mais técnicas válidas
- **WHEN** `techniques_applied` contém ao menos duas strings preenchidas
- **THEN** `test_minimum_techniques` é aprovado

#### Scenario: Metadados insuficientes ou malformados
- **WHEN** `techniques_applied` está ausente, não é uma lista ou possui menos de duas strings preenchidas
- **THEN** `test_minimum_techniques` falha e informa a quantidade mínima exigida

### Requirement: Execução local determinística

A suíte **DEVE** (`SHALL`) concluir suas verificações sem ler credenciais, acessar rede, chamar LangSmith ou invocar um provedor de LLM.

#### Scenario: Execução sem configuração externa
- **WHEN** `pytest tests/test_prompts.py` é executado em um ambiente sem `.env`, credenciais ou conectividade de rede
- **THEN** a coleta e as validações dependem somente do código, de `pytest`, de `PyYAML` e do arquivo YAML local
