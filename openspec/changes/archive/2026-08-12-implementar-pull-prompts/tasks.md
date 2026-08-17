## 1. Implementação local do pull

- [x] 1.1 Definir em `src/pull_prompts.py` as constantes do nome remoto, chave YAML e caminho de saída, além de uma extração tipada que aceite exatamente uma mensagem textual de sistema e uma de usuário e preserve variáveis como `{bug_report}`.
- [x] 1.2 Implementar `pull_prompts_from_langsmith()` para chamar `hub.pull`, montar o documento com metadados determinísticos, persistir por `save_yaml` e converter falhas de integração, estrutura ou escrita em resultado falso e mensagens seguras em pt-BR.
- [x] 1.3 Implementar `main()` para exibir o cabeçalho, validar `LANGSMITH_API_KEY` antes da rede, informar progresso e retornar `0` somente após pull e persistência bem-sucedidos.

## 2. Testes automatizados

- [x] 2.1 Criar `tests/test_pull_prompts.py` com um `ChatPromptTemplate` real e mocks de rede/persistência para verificar nome remoto, contrato YAML, metadados, caminho de saída e preservação literal de `{bug_report}` no fluxo de sucesso.
- [x] 2.2 Cobrir credencial ausente, exceção de `hub.pull`, tipo incompatível, ausência ou duplicidade de papéis obrigatórios e retorno falso de `save_yaml`, verificando código de saída diferente de zero e ausência de falsa confirmação.
- [x] 2.3 Executar `pytest tests/test_pull_prompts.py` e `pytest tests/test_prompts.py`, corrigindo regressões locais sem acessar LangSmith ou ler credenciais reais.

## 3. Validação externa no LangSmith

- [x] 3.1 Em ambiente autorizado com `LANGSMITH_API_KEY` válida e rede disponível, executar `python src/pull_prompts.py` e registrar evidência de que `leonanluppi/bug_to_user_story_v1` foi obtido sem expor a credencial.
- [x] 3.2 Inspecionar `prompts/bug_to_user_story_v1.yml` após a execução e confirmar chave superior, campos obrigatórios, papéis corretos e preservação de `{bug_report}`; não marcar esta etapa como concluída sem resultado real.
