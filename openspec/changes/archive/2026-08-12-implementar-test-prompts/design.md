## Context

`tests/test_prompts.py` já define os nomes e as intenções dos seis testes obrigatórios, além de oferecer `load_prompts()`, mas seus corpos contêm apenas `pass`. O repositório também possui um YAML local usado pelo fluxo corrente de prompt, enquanto o README define o prompt otimizado como o artefato que deve passar por essas verificações antes do push e da avaliação.

A mudança afeta somente a barreira de qualidade local. Seus usuários são quem desenvolve e revisa o prompt, que precisa receber falhas rápidas e compreensíveis sem configurar LangSmith, OpenAI ou Google. O idioma das docstrings, mensagens de asserção e demais conteúdos humanos será pt-BR.

## Goals / Non-Goals

**Goals:**

- Implementar exatamente os seis testes mínimos já nomeados no arquivo.
- Compartilhar o carregamento e a seleção do prompt entre os testes para evitar repetição.
- Validar conteúdo significativo, e não apenas a existência nominal dos campos.
- Produzir mensagens de falha que indiquem qual requisito do prompt precisa ser corrigido.
- Executar de forma determinística apenas com `pytest`, `PyYAML` e arquivos locais.

**Non-Goals:**

- Criar ou otimizar o conteúdo do prompt YAML.
- Alterar a implementação de `validate_prompt_structure()` ou qualquer outro arquivo protegido.
- Publicar prompts, validar credenciais ou acessar o LangSmith.
- Executar o dataset, chamar um LLM ou comprovar o limite de 0,8 das métricas remotas.
- Testar `src/pull_prompts.py` ou `src/push_prompts.py`, que possuem suítes próprias.

## Decisions

### 1. Centralizar caminho, chave e carregamento do prompt

O arquivo de teste declarará constantes para o caminho e a chave do YAML adotado pelo fluxo corrente e usará uma fixture de escopo de classe ou módulo para carregar e selecionar a entrada uma única vez. A fixture fará asserções explícitas sobre a raiz YAML, a presença da chave e o tipo mapeamento antes de entregar os dados aos seis testes.

Alternativa considerada: abrir o YAML em cada método. Foi rejeitada por repetir E/S e por espalhar a responsabilidade de seleção da entrada.

### 2. Fazer validações semânticas simples e transparentes

As verificações usarão normalização por `strip()` e comparação sem distinção de maiúsculas/minúsculas quando apropriado. A persona será reconhecida por uma instrução explícita de papel; o formato aceitará uma exigência de Markdown ou os componentes canônicos `Como um`, `eu quero` e `para que`; o few-shot exigirá evidências claras de exemplos com entrada e saída.

Alternativa considerada: expressões regulares extensas ou análise por LLM. Foi rejeitada porque aumentaria fragilidade, custo e dependência externa para um contrato estrutural simples.

### 3. Validar todo o texto relevante contra pendências

O teste de TODO inspecionará, sem diferenciar caixa, os campos textuais do prompt, especialmente `system_prompt` e `user_prompt`. Assim, um marcador pendente não passará apenas por estar fora do texto de sistema.

Alternativa considerada: verificar somente a forma literal `[TODO]` em `system_prompt`. Foi rejeitada porque deixaria passar variantes como `TODO:` e pendências no template humano.

### 4. Exigir duas técnicas declaradas e válidas

`techniques_applied` deverá ser uma lista com pelo menos duas strings não vazias. A presença real de exemplos no texto continuará coberta pelo teste específico de few-shot; os metadados não substituirão a validação do conteúdo.

Alternativa considerada: verificar apenas `len(techniques_applied)`. Foi rejeitada porque valores vazios ou de tipos incorretos poderiam satisfazer artificialmente a contagem.

### 5. Manter isolamento total de integrações externas

Os testes não importarão clientes de LangSmith, não lerão `.env` e não chamarão provedores de LLM. Como só analisam YAML, seu resultado será idêntico com OpenAI ou Google configurado, sem consumo de rede ou custo de API.

## Risks / Trade-offs

- [Heurísticas textuais podem rejeitar uma formulação válida escrita com vocabulário inesperado] → Manter um conjunto pequeno de alternativas explícitas e mensagens que indiquem o padrão aceito.
- [Heurísticas permissivas podem aceitar menções superficiais a persona, formato ou exemplos] → Combinar termos relacionados em vez de confiar em uma única palavra isolada.
- [O nome do YAML ou da chave pode mudar durante a otimização] → Isolar ambos em constantes, permitindo uma alteração localizada e visível.
- [A suíte inicialmente falhará enquanto o prompt local não cumprir o contrato] → Tratar a falha como resultado esperado da barreira de qualidade; não enfraquecer testes nem editar o prompt neste escopo.

## Migration Plan

1. Implementar a fixture e as seis asserções em `tests/test_prompts.py`.
2. Executar `pytest tests/test_prompts.py` e confirmar que cada falha remanescente descreve uma deficiência real do YAML corrente.
3. Executar a suíte completa para detectar regressões nos testes de pull e push.
4. Em caso de rollback, restaurar somente `tests/test_prompts.py`; nenhum estado externo ou dado persistente será alterado.

## Open Questions

Nenhuma. O arquivo e a chave concretos serão confirmados contra o fluxo local no momento da aplicação da mudança, preservando quaisquer edições intencionais já existentes no workspace.
