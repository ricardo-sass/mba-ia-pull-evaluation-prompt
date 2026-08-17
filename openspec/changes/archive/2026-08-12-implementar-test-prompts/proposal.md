## Why

`tests/test_prompts.py` contém os seis testes mínimos exigidos pelo desafio, mas todos ainda estão vazios e, portanto, não protegem o contrato de qualidade do prompt otimizado. Implementá-los permite detectar localmente e de forma rápida regressões de estrutura, persona, formato, exemplos, marcadores pendentes e metadados antes de qualquer publicação ou avaliação no LangSmith.

## What Changes

- Implementar os seis testes existentes em `tests/test_prompts.py` com asserções claras e mensagens de falha acionáveis em pt-BR.
- Carregar uma única vez o prompt YAML usado pelo fluxo atual, selecionar sua entrada versionada e validar que o conteúdo possui a estrutura esperada.
- Verificar `system_prompt` não vazio, definição explícita de persona, formato de User Story ou Markdown, exemplos few-shot, ausência de `TODO` e ao menos duas técnicas válidas em `techniques_applied`.
- Manter a suíte totalmente local e determinística, sem acessar `.env`, provedores de LLM ou o LangSmith.
- Preservar os arquivos protegidos `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl` sem alterações.

## Capabilities

### New Capabilities

- `validacao-local-prompts`: validação automatizada, por meio de pytest, dos requisitos estruturais e das técnicas declaradas no prompt otimizado.

### Modified Capabilities

Nenhuma.

## Impact

- Código afetado: `tests/test_prompts.py`.
- Entrada local validada: o arquivo YAML de prompt otimizado adotado pelo fluxo atual em `prompts/`.
- Dependências existentes: `pytest` e `PyYAML`; nenhuma nova dependência será adicionada.
- Sistemas externos: nenhum. A mudança não realiza pull, push ou avaliação no LangSmith, não requer credenciais nem gera custo de API.
- Compatibilidade: a validação independe do provedor de LLM e permanece compatível com OpenAI e Google.
