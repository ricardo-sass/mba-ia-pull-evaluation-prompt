## Context

O prompt v1 apenas solicita a conversão de um relato em User Story, sem definir persona especializada, regras de fidelidade, formato verificável, exemplos ou tratamento proporcional à complexidade. O dataset de 15 casos varia entre bugs simples, médios e complexos nos domínios e-commerce, SaaS, mobile, ERP e CRM, incluindo segurança, performance, integrações, concorrência, cache, sincronização e memória.

O novo YAML será a entrada local do fluxo:

```text
prompts/bug_to_user_story_v2.yml
   │ validação local + ChatPromptTemplate
   ▼
LangSmith Prompt Hub (somente em operação posterior autorizada)
   │ prompt público consumido por src/evaluate.py
   ▼
Dataset → LLM gerador → LLM avaliador
   │
   └─ Helpfulness, Correctness, F1-Score, Clarity e Precision ≥ 0,8
```

A criação do arquivo e todas as verificações desta mudança serão locais. O conteúdo humano do YAML será escrito em pt-BR, funcionará com os modelos OpenAI e Google já suportados e não conterá credenciais, URLs de resultado ou métricas inventadas.

## Goals / Non-Goals

**Goals:**

- Criar um YAML v2 estruturalmente válido e compatível com o contrato de `src/push_prompts.py`.
- Melhorar clareza, fidelidade, completude e testabilidade das User Stories geradas.
- Aplicar Few-shot Learning, Role Prompting e Skeleton of Thought de forma explícita e rastreável.
- Cobrir relatos simples, médios, complexos, vagos, multidimensionais e potencialmente maliciosos.
- Preservar todos os fatos relevantes e evitar detalhes, soluções, prazos ou limites não sustentados pela entrada.
- Produzir somente a resposta final em pt-BR, sem expor raciocínio interno.

**Non-Goals:**

- Alterar qualquer arquivo além de `prompts/bug_to_user_story_v2.yml`.
- Realinhar nesta mudança caminhos temporários usados por outros arquivos locais.
- Publicar ou tornar público o prompt no LangSmith.
- Executar `src/evaluate.py`, consumir APIs de LLM ou garantir antecipadamente notas mínimas de 0,8.
- Documentar métricas, links ou iterações no README antes de existirem evidências reais.
- Prescrever uma solução técnica quando o relato apenas descreve o problema.

## Decisions

### 1. Usar um documento YAML único, estável e legível

O arquivo terá uma única chave raiz `bug_to_user_story_v2`. Os campos serão ordenados como `description`, `system_prompt`, `user_prompt`, `version`, `tags` e `techniques_applied`; os templates usarão blocos literais YAML para preservar quebras de linha e caracteres Unicode.

Alternativa considerada: strings YAML escapadas em uma linha. Foi rejeitada porque dificulta revisão, manutenção dos exemplos e detecção de erros no formato.

### 2. Separar política permanente de entrada não confiável

O `system_prompt` conterá persona, objetivos, regras, processo e formato. O `user_prompt` conterá apenas a solicitação e o relato delimitado, com exatamente a variável `{bug_report}`. O sistema instruirá o modelo a tratar o conteúdo delimitado como dados, ignorando qualquer tentativa interna de substituir instruções.

Alternativa considerada: interpolar `{bug_report}` no `system_prompt`, como ocorre no v1. Foi rejeitada por misturar dados com política, duplicar a entrada e aumentar o risco de injeção de prompt.

### 3. Combinar três técnicas complementares

- **Role Prompting:** persona de Product Manager sênior com experiência em qualidade, análise de bugs e critérios de aceitação.
- **Few-shot Learning:** três pares sintéticos de entrada/saída, distintos do dataset avaliado, cobrindo complexidades simples, média e complexa.
- **Skeleton of Thought:** roteiro interno de análise e um esqueleto fixo de saída, sem solicitar nem revelar cadeia de raciocínio.

Alternativa considerada: Chain of Thought explícito. Foi rejeitada porque não é necessário expor raciocínio para obter uma saída estruturada e aumentaria verbosidade e custo.

### 4. Usar um formato Markdown adaptável

Toda resposta conterá `## User Story`, uma frase `Como um..., eu quero..., para que...` e `## Critérios de Aceitação`. Cada cenário utilizará Dado/Quando/Então e poderá incluir E. `## Contexto do Bug` e `## Informações a Confirmar` serão opcionais e só aparecerão quando houver dados relevantes ou lacunas materiais.

Bugs simples terão uma história e poucos critérios diretos. Bugs complexos manterão uma história principal coesa e agruparão critérios por dimensão, por exemplo segurança, integração, lógica de negócio e experiência do usuário, evitando perder aspectos do relato.

Alternativa considerada: sempre produzir um documento extenso com seções técnicas. Foi rejeitada porque prejudicaria Clarity e Precision em casos simples.

### 5. Priorizar fidelidade sem empobrecer a utilidade

O prompt distinguirá fatos informados, inferências mínimas necessárias para formular a perspectiva do usuário e informações ausentes. Deve preservar plataformas, endpoints, mensagens, números, severidade, impacto, passos e comportamento atual/esperado presentes na entrada. Não deve inventar tecnologias, arquitetura, mensagens, SLAs, regras ou soluções; quando uma lacuna impedir um critério preciso, deve registrá-la em `Informações a Confirmar`.

Alternativa considerada: completar lacunas com práticas comuns. Foi rejeitada porque pode aumentar aparente completude às custas de Correctness e Precision.

### 6. Tornar os exemplos representativos sem contaminar a avaliação

Os três exemplos serão sintéticos e compactos:

1. um defeito simples de interface;
2. uma falha média de integração com evidência técnica;
3. um caso complexo com múltiplos aspectos relacionados.

Cada exemplo terá marcadores explícitos `Exemplo`, `Entrada` e `Saída`, demonstrará o formato final e não conterá chaves literais que o LangChain possa interpretar como variáveis adicionais.

Alternativa considerada: copiar entradas e referências do dataset. Foi rejeitada para reduzir sobreajuste e preservar a validade da avaliação posterior.

### 7. Validar sintaxe e contrato sem operações externas

A aplicação carregará o arquivo com PyYAML, confirmará campos, tipos, versão, variável, ausência de TODOs e técnicas. Em seguida construirá um `ChatPromptTemplate` local e verificará que sua única variável é `bug_report`. As seis regras de `tests/test_prompts.py` serão exercitadas diretamente sobre os dados v2; a execução normal do arquivo continuará sendo apenas uma verificação de regressão enquanto ele apontar para outro YAML local.

Nenhuma etapa chamará LangSmith, OpenAI ou Google. Isso elimina custo, necessidade de credenciais e risco de publicação acidental nesta mudança.

## Risks / Trade-offs

- [Prompt e três exemplos aumentam tokens de entrada] → Manter exemplos compactos e remover explicações redundantes.
- [Formato rígido pode gerar texto excessivo para bugs simples] → Tornar seções contextuais opcionais e ajustar quantidade de critérios à complexidade.
- [Regras contra invenção podem reduzir sobreposição com referências que sugerem soluções] → Preservar integralmente soluções já informadas e permitir perguntas explícitas, sem fabricar detalhes.
- [Relatos complexos podem conter vários problemas independentes] → Agrupar dimensões relacionadas sob uma história principal e sinalizar quando a separação em histórias futuras for necessária.
- [Chaves dos exemplos podem ser interpretadas pelo LangChain] → Evitar chaves literais nos exemplos e validar que somente `bug_report` seja reconhecida como variável.
- [Instruções dentro do relato podem tentar substituir o sistema] → Delimitar a entrada e ordenar que ela seja tratada exclusivamente como dados de bug.
- [Os testes locais atuais podem apontar para outro YAML] → Validar o v2 diretamente e registrar separadamente qualquer falha de regressão sem alterar o alvo fora do escopo.
- [A qualidade remota permanece desconhecida] → Não declarar aprovação; condicionar qualquer afirmação de 0,8 ao push e à avaliação posteriores com evidências reais.

## Migration Plan

1. Criar `prompts/bug_to_user_story_v2.yml` sem substituir o v1 ou outros arquivos locais.
2. Validar parsing, contrato, variáveis e construção do `ChatPromptTemplate` sem rede.
3. Exercitar as seis regras estruturais sobre os dados v2 e executar a suíte local como regressão.
4. Encerrar esta mudança sem push ou avaliação externa.

Rollback local: remover apenas o novo arquivo v2. Não há rollback remoto, pois esta mudança não modifica o LangSmith.

## Open Questions

Nenhuma questão bloqueante. Publicação, avaliação e iterações orientadas pelas métricas pertencem a uma etapa posterior e exigem autorização explícita.
