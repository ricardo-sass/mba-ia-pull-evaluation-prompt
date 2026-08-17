## 1. Implementação local do push

- [x] 1.1 Definir em `src/push_prompts.py` as constantes do caminho v2, chave YAML e sufixo remoto, importar a validação estrutural existente e criar auxiliares determinísticos para deduplicar metadados e gerar o README do Hub.
- [x] 1.2 Implementar `validate_prompt()` para acumular erros de campos, tipos, versão, tags, técnicas, `{bug_report}` e TODOs, reutilizando `validate_prompt_structure()` sem alterar `src/utils.py`.
- [x] 1.3 Implementar `push_prompt_to_langsmith()` para construir o `ChatPromptTemplate`, preservar papéis e variáveis, chamar `hub.push` com visibilidade pública, descrição, README e tags/técnicas e tratar falhas sem expor exceções sensíveis.
- [x] 1.4 Implementar `main()` para validar `LANGSMITH_API_KEY` e `USERNAME_LANGSMITH_HUB`, carregar e selecionar `bug_to_user_story_v2`, listar todos os erros locais, formar `{username}/bug_to_user_story_v2` e retornar código `0` somente após sucesso remoto.

## 2. Testes automatizados

- [x] 2.1 Criar `tests/test_push_prompts.py` com dados v2 sintéticos e mocks para verificar nome remoto, ordem e conteúdo das mensagens do `ChatPromptTemplate`, visibilidade pública, descrição, README, deduplicação de tags/técnicas e URL de sucesso.
- [x] 2.2 Cobrir ambiente incompleto, arquivo ausente ou inválido, chave superior incorreta, todos os erros de validação, sintaxe incompatível do template, exceção do Hub e códigos de saída, garantindo que entradas inválidas nunca chamem `hub.push`.
- [x] 2.3 Executar `pytest tests/test_push_prompts.py`, `pytest tests/test_prompts.py` e a suíte completa, corrigindo regressões sem acessar rede, `.env` real ou LangSmith.

## 3. Preparação da operação externa e evidências

- [x] 3.1 Executar uma validação local integral com mocks e registrar evidência dos parâmetros que seriam enviados ao Hub, sem realizar publicação real nesta mudança.
- [x] 3.2 Registrar no handoff que o push real e a verificação pública no dashboard dependem de `prompts/bug_to_user_story_v2.yml` válido e de autorização explícita; não inventar URL, visibilidade ou resultado externo.
