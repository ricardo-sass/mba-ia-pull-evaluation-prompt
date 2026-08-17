## ADDED Requirements

### Requirement: Estrutura YAML versionada

O artefato **DEVE** (`SHALL`) existir em `prompts/bug_to_user_story_v2.yml`, possuir uma única chave raiz `bug_to_user_story_v2` e conter `description`, `system_prompt`, `user_prompt`, `version`, `tags` e `techniques_applied` com tipos válidos e textos não vazios. `version` **DEVE** ser exatamente `v2`, e nenhum campo textual **DEVE** conter `TODO` ou `[TODO]`.

#### Scenario: Documento v2 válido
- **WHEN** o arquivo é carregado com PyYAML
- **THEN** a raiz e `bug_to_user_story_v2` são mapeamentos, todos os campos obrigatórios existem e `version` é `v2`

#### Scenario: Campo ausente ou pendente
- **WHEN** um campo obrigatório está ausente, vazio, possui tipo incompatível ou contém marcador TODO
- **THEN** a validação local rejeita o documento antes de qualquer operação externa

### Requirement: Metadados das técnicas e domínio

O prompt **DEVE** (`SHALL`) declarar tags descritivas não vazias e listar em `techniques_applied` pelo menos `Few-shot Learning`, `Role Prompting` e `Skeleton of Thought`, sem duplicatas ou valores vazios.

#### Scenario: Metadados completos
- **WHEN** os metadados são inspecionados
- **THEN** eles identificam o domínio de bugs e User Stories, a versão otimizada e as três técnicas efetivamente presentes no conteúdo

### Requirement: Separação entre sistema e usuário

O `system_prompt` **DEVE** (`SHALL`) concentrar persona, regras, processo e formato, enquanto `user_prompt` **DEVE** conter o relato delimitado e exatamente uma ocorrência funcional da variável `{bug_report}`. O `ChatPromptTemplate` resultante **NÃO DEVE** (`MUST NOT`) exigir qualquer outra variável.

#### Scenario: Construção do template
- **WHEN** o YAML é convertido em mensagens de sistema e usuário pelo LangChain
- **THEN** o template é construído sem erro, preserva os dois papéis e expõe somente `bug_report` como variável de entrada

#### Scenario: Relato tratado como dado
- **WHEN** o relato contém texto que tenta ignorar, revelar ou substituir as instruções do sistema
- **THEN** o modelo trata esse texto como parte do bug e continua seguindo persona, regras e formato definidos no sistema

### Requirement: Persona e idioma

O `system_prompt` **DEVE** (`SHALL`) definir explicitamente a persona de Product Manager experiente em análise de bugs, qualidade de software e escrita de User Stories. A resposta final **DEVE** ser escrita em português brasileiro, preservando identificadores técnicos recebidos quando necessário.

#### Scenario: Conversão orientada por produto
- **WHEN** um relato válido é recebido
- **THEN** a resposta traduz o problema para valor e impacto ao usuário sem perder o contexto técnico relevante

#### Scenario: Entrada com termos técnicos em outro idioma
- **WHEN** o relato contém endpoints, códigos, logs ou nomes técnicos em inglês
- **THEN** a resposta permanece em pt-BR e conserva literalmente os identificadores necessários à fidelidade

### Requirement: Fidelidade ao relato

O prompt **DEVE** (`SHALL`) preservar fatos, atores, plataformas, condições, passos, números, mensagens, endpoints, severidade, impacto e comportamento atual ou esperado fornecidos. Ele **NÃO DEVE** (`MUST NOT`) inventar tecnologias, causas, soluções, mensagens, prazos, limites, regras de negócio ou resultados não sustentados pela entrada.

#### Scenario: Relato com evidências detalhadas
- **WHEN** o bug informa valores, ambiente, logs, impacto ou passos de reprodução
- **THEN** a User Story e seus critérios incorporam os elementos relevantes sem alterá-los

#### Scenario: Relato incompleto ou ambíguo
- **WHEN** faltam informações necessárias para definir um comportamento testável
- **THEN** a resposta formula somente o que é sustentado e registra perguntas objetivas em `Informações a Confirmar`, sem preencher lacunas com suposições

#### Scenario: Solução técnica já informada
- **WHEN** o relato contém uma causa ou proposta técnica explícita
- **THEN** a resposta pode preservá-la como contexto informado, sem apresentá-la como fato novo ou decisão obrigatória

### Requirement: Formato da User Story

A saída **DEVE** (`SHALL`) ser Markdown conciso, iniciar com `## User Story` e conter uma frase completa no formato `Como um [ator], eu quero [necessidade], para que [benefício]`. O ator, a necessidade e o benefício **DEVEM** ser coerentes com o relato e centrados no usuário ou sistema afetado.

#### Scenario: História gerada
- **WHEN** o relato descreve um único problema
- **THEN** a resposta contém uma User Story coesa, sem confundir comportamento desejado com implementação

#### Scenario: Benefício não explícito
- **WHEN** o impacto pode ser inferido diretamente do problema sem adicionar fatos específicos
- **THEN** o prompt expressa um benefício geral e seguro, como concluir a tarefa com confiança, sem criar métricas ou regras inexistentes

### Requirement: Critérios de aceitação testáveis

A saída **DEVE** (`SHALL`) conter `## Critérios de Aceitação` e cenários claros em Dado/Quando/Então, com condições observáveis e resultados verificáveis. Os critérios **DEVEM** cobrir o caminho principal, a falha relatada e casos de erro ou limite relevantes, sem duplicação ou solução técnica inventada.

#### Scenario: Bug funcional simples
- **WHEN** o relato descreve uma falha simples com contexto suficiente
- **THEN** a resposta produz poucos critérios diretos que reproduzem a condição e confirmam o comportamento esperado

#### Scenario: Bug com erro ou caso-limite
- **WHEN** o relato envolve validação, indisponibilidade, limite, timeout, concorrência ou entrada inválida
- **THEN** ao menos um cenário cobre explicitamente o erro ou caso-limite sustentado pela entrada

### Requirement: Adaptação à complexidade

O prompt **DEVE** (`SHALL`) ajustar profundidade e organização à complexidade do relato. Bugs simples **DEVEM** gerar respostas concisas; bugs médios **DEVEM** preservar evidências e contexto técnico; bugs complexos **DEVEM** cobrir todas as dimensões relevantes e agrupá-las de modo legível sob uma história principal.

#### Scenario: Bug médio com integração
- **WHEN** o relato contém fluxo de reprodução, endpoint, código de erro e consequência para o usuário
- **THEN** a resposta preserva esses fatos e cria critérios tanto para o resultado funcional quanto para a condição de integração

#### Scenario: Bug complexo multidimensional
- **WHEN** o relato combina segurança, integração, lógica de negócio, UX, performance, cache, concorrência, sincronização ou memória
- **THEN** a resposta mantém todos os aspectos relevantes, agrupa critérios por dimensão e conserva severidade e impacto informados

#### Scenario: Problemas independentes no mesmo relato
- **WHEN** o relato reúne problemas sem um objetivo comum suficiente para uma única história coesa
- **THEN** a resposta identifica a necessidade de separação e organiza histórias distintas sem omitir nenhum problema informado

### Requirement: Contexto opcional e ausência de ruído

A saída **DEVE** (`SHALL`) incluir `## Contexto do Bug` somente quando o relato trouxer detalhes técnicos, impacto, severidade ou evidências úteis, e `## Informações a Confirmar` somente quando houver lacunas materiais. Seções vazias, comentários sobre o processo, raciocínio interno e preâmbulos **NÃO DEVEM** (`MUST NOT`) aparecer.

#### Scenario: Bug simples e completo
- **WHEN** o relato é curto, claro e não possui contexto adicional relevante
- **THEN** a resposta se limita à User Story e aos critérios de aceitação

#### Scenario: Bug complexo com contexto rico
- **WHEN** o relato contém logs, números, ambiente, impacto ou severidade
- **THEN** a resposta inclui um resumo factual em `Contexto do Bug` sem repetir integralmente os critérios

### Requirement: Exemplos few-shot representativos

O `system_prompt` **DEVE** (`SHALL`) conter três exemplos sintéticos e compactos com marcadores explícitos `Exemplo`, `Entrada` e `Saída`, cobrindo complexidades simples, média e complexa. Cada saída de exemplo **DEVE** seguir o mesmo formato e as mesmas regras exigidas para respostas reais.

#### Scenario: Inspeção dos exemplos
- **WHEN** o conteúdo do sistema é revisado
- **THEN** são encontrados três pares completos de entrada e saída, com persona, formato e critérios demonstrados por casos distintos do dataset de avaliação

#### Scenario: Compatibilidade dos exemplos com LangChain
- **WHEN** o prompt é analisado pelo mecanismo de templates
- **THEN** os exemplos não introduzem variáveis por chaves literais nem impedem a construção do `ChatPromptTemplate`

### Requirement: Barreira de qualidade local e meta remota

O arquivo **DEVE** (`SHALL`) passar por parsing YAML, validação estrutural, construção local do `ChatPromptTemplate` e pelas seis regras de presença do sistema, persona, formato, few-shot, ausência de TODOs e técnicas mínimas. A aprovação final de qualidade **DEVE** exigir, em etapa externa posterior, Helpfulness, Correctness, F1-Score, Clarity e Precision individualmente maiores ou iguais a 0,8 e média geral maior ou igual a 0,8.

#### Scenario: Validação local bem-sucedida
- **WHEN** o arquivo v2 é validado sem rede
- **THEN** todos os campos, técnicas, regras textuais e a única variável `bug_report` satisfazem o contrato local

#### Scenario: Métricas ainda não executadas
- **WHEN** o YAML foi criado mas ainda não foi publicado e avaliado no LangSmith
- **THEN** a mudança registra a avaliação como pendente e não declara notas, aprovação, URL ou evidências inexistentes

#### Scenario: Avaliação remota futura
- **WHEN** uma etapa posterior autorizada publicar o prompt e executar `python src/evaluate.py`
- **THEN** o prompt só é considerado aprovado se cada uma das cinco métricas e a média geral atingirem pelo menos 0,8 com evidências reais
