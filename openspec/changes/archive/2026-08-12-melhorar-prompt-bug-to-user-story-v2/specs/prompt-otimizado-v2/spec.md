## ADDED Requirements

### Requirement: Cobertura semântica verificável

O `system_prompt` **DEVE** (`SHALL`) instruir uma análise interna de cobertura antes da redação, identificando ator, objetivo, ambiente, plataforma, passos, valores, mensagens, endpoints, comportamento observado, comportamento esperado, causa informada, impacto, severidade, erros, limites e dimensões técnicas presentes no relato. Cada fato relevante e cada problema independente **DEVE** aparecer ao menos uma vez na User Story, nos critérios de aceitação ou no contexto, sem repetição desnecessária.

#### Scenario: Relato com múltiplos fatos relevantes
- **WHEN** o bug informa endpoint, código de erro, estado atual, valor esperado e impacto
- **THEN** a resposta preserva semanticamente todos esses elementos nas seções apropriadas

#### Scenario: Relato multidimensional
- **WHEN** o bug reúne dois ou mais problemas nas dimensões de segurança, integração, negócio, UX, performance, cache, concorrência, sincronização ou memória
- **THEN** cada dimensão recebe ao menos um resultado verificável e nenhuma dimensão informada é omitida

#### Scenario: Revisão sem redundância
- **WHEN** o mesmo fato é útil em critérios e contexto
- **THEN** a resposta o referencia de forma complementar e não reproduz blocos idênticos de conteúdo

### Requirement: Estrutura de saída adaptativa

A saída **DEVE** (`SHALL`) conter sempre uma User Story e Critérios de Aceitação, e **DEVE** acrescentar somente as seções condicionais sustentadas pela complexidade e pelo conteúdo: critérios de prevenção ou adicionais, critérios técnicos ou especializados, exemplo de cálculo, contexto do bug, tarefas técnicas sugeridas e métricas de sucesso. Seções condicionais **NÃO DEVEM** (`MUST NOT`) estar vazias ou conter detalhes arbitrários apenas para preencher o formato.

#### Scenario: Bug simples de interação
- **WHEN** o relato descreve uma única falha de UI ou validação sem contexto técnico extenso
- **THEN** a saída contém história e critérios concisos, cobrindo resultado principal, bloqueio ou feedback diretamente inferível da interação

#### Scenario: Bug médio com causa informada
- **WHEN** o relato inclui reprodução, causa, erro, limite ou detalhe técnico relevante
- **THEN** a saída acrescenta contexto e critérios de prevenção, erro ou técnicos rastreáveis à entrada

#### Scenario: Bug complexo com recomendações aplicáveis
- **WHEN** o relato detalha múltiplas dimensões, causas e impacto
- **THEN** a saída apresenta história principal, critérios agrupados por dimensão, critérios técnicos e tarefas sugeridas, além de métricas somente quando existirem valores de referência ou metas claramente identificadas

#### Scenario: Seção sem sustentação
- **WHEN** o relato não oferece conteúdo para uma seção condicional
- **THEN** a seção é omitida em vez de ser preenchida com suposições ou marcadores

### Requirement: Distinção entre fatos, inferências e recomendações

O prompt **DEVE** (`SHALL`) distinguir fatos observados, resultados esperados inferíveis e recomendações. Inferências **DEVEM** ser consequências diretas e conservadoras do fluxo relatado. Recomendações técnicas **DEVEM** ser apresentadas em seção própria, associadas a uma causa ou risco informado e descritas como sugestão a validar, nunca como implementação existente ou decisão aprovada.

#### Scenario: Resultado funcional diretamente inferível
- **WHEN** uma entrada inválida é aceita e permite prosseguir
- **THEN** os critérios podem exigir bloqueio do avanço e feedback de validação sem inventar uma mensagem exata

#### Scenario: Prática técnica coerente com a causa
- **WHEN** o relato informa carregamento integral na thread principal e travamento com grande volume
- **THEN** a resposta pode recomendar paginação e processamento fora da thread principal, deixando explícito que são abordagens propostas

#### Scenario: Detalhe técnico arbitrário
- **WHEN** o relato não informa nem sustenta tecnologia, valor, prazo, mensagem ou regra de negócio específica
- **THEN** a resposta não apresenta esse detalhe como fato e, se ele for indispensável como meta, sinaliza que requer validação

## MODIFIED Requirements

### Requirement: Fidelidade ao relato

O prompt **DEVE** (`SHALL`) preservar fatos, atores, plataformas, condições, passos, números, mensagens, endpoints, severidade, impacto e comportamento atual ou esperado fornecidos. Ele **NÃO DEVE** (`MUST NOT`) inventar como fatos tecnologias, causas, soluções, mensagens, prazos, limites, métricas, regras de negócio ou resultados ausentes. O prompt **PODE** (`MAY`) formular resultados funcionais conservadores e recomendações técnicas diretamente sustentadas pelo relato, desde que não altere os fatos e deixe explícito o caráter inferido, recomendado ou pendente de validação.

#### Scenario: Relato com evidências detalhadas
- **WHEN** o bug informa valores, ambiente, logs, impacto ou passos de reprodução
- **THEN** a User Story, os critérios e o contexto incorporam todos os elementos relevantes sem alterá-los

#### Scenario: Relato incompleto ou ambíguo
- **WHEN** faltam informações necessárias para definir um comportamento testável
- **THEN** a resposta formula a parte sustentada, usa apenas inferências conservadoras e registra perguntas objetivas em `Informações a Confirmar` quando a lacuna mudar o aceite

#### Scenario: Solução técnica já informada
- **WHEN** o relato contém uma causa ou proposta técnica explícita
- **THEN** a resposta preserva esse conteúdo, distingue causa observada de proposta e o utiliza para enriquecer critérios técnicos sem apresentá-lo como fato novo

#### Scenario: Recomendação não informada mas rastreável
- **WHEN** uma prática técnica padrão decorre diretamente da causa ou do risco informado
- **THEN** a resposta pode incluí-la como recomendação a validar, sem adicionar tecnologia ou valor específico desnecessário

### Requirement: Adaptação à complexidade

O prompt **DEVE** (`SHALL`) ajustar profundidade, seções e organização à complexidade do relato. Bugs simples **DEVEM** gerar respostas concisas com o resultado funcional e feedback ou bloqueio diretamente inferível; bugs médios **DEVEM** preservar evidências, contexto técnico, prevenção e casos de erro; bugs complexos **DEVEM** cobrir todas as dimensões relevantes, agrupar critérios sob uma história principal e apresentar critérios técnicos, tarefas sugeridas e métricas sustentadas quando agregarem informação útil.

#### Scenario: Bug médio com integração
- **WHEN** o relato contém fluxo de reprodução, endpoint, código de erro e consequência para o usuário
- **THEN** a resposta preserva esses fatos e cria critérios para o resultado funcional, a condição de integração, o tratamento da falha e a prevenção de recorrência

#### Scenario: Bug complexo multidimensional
- **WHEN** o relato combina segurança, integração, lógica de negócio, UX, performance, cache, concorrência, sincronização ou memória
- **THEN** a resposta mantém todos os aspectos relevantes, agrupa critérios por dimensão, conserva severidade e impacto e separa critérios funcionais de recomendações técnicas

#### Scenario: Problemas independentes no mesmo relato
- **WHEN** o relato reúne problemas sem um objetivo comum suficiente para uma única história coesa
- **THEN** a resposta organiza histórias distintas com critérios próprios e não omite nenhum problema informado

#### Scenario: Métricas e tarefas em relato complexo
- **WHEN** o relato fornece baseline, limite, SLA, impacto mensurável ou causas técnicas
- **THEN** a resposta reutiliza esses dados em métricas de sucesso e tarefas sugeridas, marcando qualquer nova meta como recomendação a validar

### Requirement: Exemplos few-shot representativos

O `system_prompt` **DEVE** (`SHALL`) conter três exemplos sintéticos com marcadores explícitos `Exemplo`, `Entrada` e `Saída`, cobrindo complexidades simples, média e complexa. Cada saída **DEVE** seguir a estrutura adaptativa exigida para respostas reais: o exemplo simples demonstra resultado e feedback; o médio demonstra contexto, erro ou prevenção e recomendação rastreável; o complexo demonstra cobertura por dimensão, critérios técnicos e tarefas ou métricas sustentadas.

#### Scenario: Inspeção dos exemplos
- **WHEN** o conteúdo do sistema é revisado
- **THEN** são encontrados três pares completos de entrada e saída que ensinam níveis crescentes de cobertura sem copiar literalmente casos do dataset de avaliação

#### Scenario: Consistência entre instrução e exemplos
- **WHEN** os exemplos são comparados ao contrato de saída
- **THEN** nenhum exemplo apresenta como fato uma tecnologia, valor, regra ou solução ausente em sua entrada

#### Scenario: Compatibilidade dos exemplos com LangChain
- **WHEN** o prompt é analisado pelo mecanismo de templates
- **THEN** os exemplos não introduzem variáveis por chaves literais nem impedem a construção do `ChatPromptTemplate`

### Requirement: Barreira de qualidade local e meta remota

O arquivo **DEVE** (`SHALL`) passar por parsing YAML, validação estrutural, construção local do `ChatPromptTemplate` e por verificações de presença do sistema, persona, formato, few-shot, ausência de TODOs, técnicas mínimas, matriz de cobertura, níveis de confiança e estrutura adaptativa. A aprovação final **DEVE** exigir, em etapa externa posterior, Helpfulness, Correctness, F1-Score, Clarity e Precision individualmente maiores ou iguais a 0,8 e média geral maior ou igual a 0,8.

#### Scenario: Validação local bem-sucedida
- **WHEN** o arquivo v2 é validado sem rede
- **THEN** campos, técnicas, regras textuais, seções adaptativas e a única variável `bug_report` satisfazem o contrato local

#### Scenario: Métricas ainda não executadas
- **WHEN** o YAML foi alterado mas ainda não foi publicado e avaliado no LangSmith
- **THEN** a mudança registra a avaliação como pendente e não declara notas, aprovação, URL ou evidências inexistentes

#### Scenario: Avaliação remota aprovada
- **WHEN** a revisão publicada é avaliada sobre os 15 exemplos pelo fluxo oficial
- **THEN** ela só é considerada aprovada se cada uma das cinco métricas e a média geral atingirem pelo menos 0,8 com evidências reais

#### Scenario: Avaliação remota ainda reprovada
- **WHEN** qualquer métrica fica abaixo de 0,8
- **THEN** os scores e traces dos piores exemplos orientam uma nova calibração focal, seguida de novo push e nova avaliação, sem alterar dataset, métricas ou modelos para mascarar o resultado

#### Scenario: Falha de serviço externo
- **WHEN** push ou avaliação falha por rede, credencial, quota ou indisponibilidade do LangSmith ou do provedor
- **THEN** a falha é registrada como operacional, nenhum segredo é exposto e nenhuma conclusão de aprovação ou reprovação é inferida
