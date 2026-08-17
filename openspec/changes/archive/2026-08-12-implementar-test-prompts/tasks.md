## 1. Preparação e carregamento local

- [x] 1.1 Definir em `tests/test_prompts.py` constantes de caminho e chave alinhadas ao prompt YAML adotado pelo fluxo corrente, sem importar módulos de integração.
- [x] 1.2 Implementar fixture compartilhada que use `load_prompts()`, valide raiz, chave e mapeamento selecionado e apresente mensagens de falha em pt-BR.

## 2. Implementação dos seis testes obrigatórios

- [x] 2.1 Implementar `test_prompt_has_system_prompt` e `test_prompt_has_role_definition` com validação de tipo, texto não vazio e instrução explícita de persona.
- [x] 2.2 Implementar `test_prompt_mentions_format` e `test_prompt_has_few_shot_examples` com verificações sem distinção de caixa para formato aceito e par identificável de entrada/saída.
- [x] 2.3 Implementar `test_prompt_no_todos` sobre os campos textuais e `test_minimum_techniques` considerando somente strings não vazias.
- [x] 2.4 Revisar imports, type hints, docstrings e mensagens de asserção de `tests/test_prompts.py`, removendo código não utilizado e mantendo o conteúdo humano em pt-BR.

## 3. Validação automatizada e isolamento

- [x] 3.1 Executar `pytest tests/test_prompts.py` e confirmar que os seis testes são coletados e que aprovações ou falhas correspondem ao conteúdo real do YAML, registrando deficiências do prompt sem alterá-lo neste escopo.
- [x] 3.2 Executar a suíte completa com `pytest` e distinguir eventuais falhas esperadas da barreira de qualidade de regressões causadas pela implementação.
- [x] 3.3 Confirmar por inspeção e execução que a suíte não lê `.env`, não requer credenciais e não acessa LangSmith, OpenAI, Google ou a rede; nenhuma operação externa ou evidência remota é aplicável a esta mudança.
