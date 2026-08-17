## Context

`src/pull_prompts.py` já possui imports, carregamento de `.env` e dois pontos de entrada, mas `pull_prompts_from_langsmith()` e `main()` ainda são esqueletos. O projeto precisa obter `leonanluppi/bug_to_user_story_v1` antes da otimização, convertendo o `ChatPromptTemplate` remoto para o contrato YAML local consumido pelo restante do desafio.

O fluxo desta mudança ocupa apenas o início da arquitetura completa:

```text
CLI local
   │ valida LANGSMITH_API_KEY
   ▼
LangSmith Prompt Hub
   │ retorna ChatPromptTemplate v1
   ▼
Extração por papel das mensagens
   │
   ▼
prompts/bug_to_user_story_v1.yml
   │ otimização posterior, fora deste escopo
   ▼
Prompt v2 → LangSmith Hub → dataset → LLM gerador → LLM avaliador
```

O comando depende de rede e do LangSmith, mas não instancia modelos OpenAI ou Google e não realiza inferência. A implementação deve permanecer compatível com ambos os provedores usados nas etapas posteriores do projeto.

## Goals / Non-Goals

**Goals:**

- Tornar o script executável de ponta a ponta, com código de saída confiável.
- Baixar sempre o prompt inicial versionado definido pelo desafio.
- Preservar os templates de sistema e usuário, inclusive variáveis não renderizadas.
- Produzir YAML determinístico e compatível com o padrão já existente em `prompts/`.
- Reutilizar `save_yaml`, `check_env_vars` e `print_section_header`.
- Cobrir comportamento local e falhas com testes sem rede e sem credenciais reais.

**Non-Goals:**

- Otimizar ou alterar semanticamente o prompt v1.
- Criar `bug_to_user_story_v2.yml` ou publicar prompts no Hub.
- Executar dataset, LLMs ou métricas de avaliação.
- Alterar `src/evaluate.py`, `src/metrics.py`, `src/utils.py` ou o dataset protegido.
- Oferecer nome remoto ou caminho de saída configuráveis nesta versão.
- Implementar retries automáticos, cache ou fallback para uma cópia local.

## Decisions

### 1. Manter identificadores do desafio como constantes do módulo

O nome remoto, a chave YAML e o caminho de saída serão constantes explícitas em `src/pull_prompts.py`. Isso torna o comportamento auditável e impede divergência acidental do contrato solicitado.

Alternativa considerada: aceitar argumentos de CLI. Foi descartada porque o desafio exige um único prompt e a configuração adicional aumentaria a superfície de teste sem agregar valor ao fluxo atual.

### 2. Separar orquestração e operação

`main()` cuidará do cabeçalho, da validação da variável de ambiente e da conversão do resultado em código de saída. `pull_prompts_from_langsmith()` cuidará de pull, extração, montagem dos dados e persistência, retornando sucesso ou falha de forma explícita.

Alternativa considerada: concentrar tudo em `main()`. Foi descartada porque dificultaria testes unitários e misturaria política de CLI com integração externa.

### 3. Usar a estrutura de mensagens, não a serialização genérica do modelo

A extração percorrerá `ChatPromptTemplate.messages`, identificará mensagens de sistema e de usuário pelos tipos de papel do LangChain e lerá seus templates textuais. O conteúdo não será formatado, portanto `{bug_report}` permanecerá intacto. Estruturas sem ambos os papéis obrigatórios ou com templates não textuais serão rejeitadas antes da escrita.

Alternativas consideradas:

- Usar posições fixas, como `messages[0]` e `messages[1]`: frágil diante de reordenação.
- Usar `model_dump()`: na versão fixada do LangChain, a serialização genérica não preserva diretamente o conteúdo dos objetos de mensagem.
- Usar `pretty_repr()`: formato voltado a apresentação, inadequado como contrato de dados.

### 4. Produzir metadados locais determinísticos

O documento terá a chave `bug_to_user_story_v1` e os campos `description`, `system_prompt`, `user_prompt`, `version`, `source` e `tags`. `system_prompt` e `user_prompt` virão do Hub; os demais representam o contrato estável conhecido pelo repositório. Não será criado timestamp de execução, evitando diffs sem mudança semântica.

Alternativa considerada: copiar metadados arbitrários do objeto remoto. Foi descartada porque sua presença e seu formato não são garantidos pela API e poderiam tornar o YAML instável.

### 5. Reutilizar autenticação implícita e utilitários existentes

Após `check_env_vars(["LANGSMITH_API_KEY"])`, `hub.pull` usará a configuração de ambiente já reconhecida pelo LangChain. A chave não será passada para mensagens, exceções customizadas ou dados persistidos. A gravação será delegada a `save_yaml`, que já cria diretórios, usa UTF-8 e preserva Unicode.

Alternativa considerada: instanciar diretamente um cliente LangSmith ou duplicar o código YAML. Foi descartada para manter a integração mínima e evitar responsabilidades duplicadas.

### 6. Tratar erros na fronteira da integração

Erros do Hub, estrutura incompatível e retorno falso de `save_yaml` serão convertidos em mensagens de CLI em pt-BR e resultado de falha. A saída deve citar etapa, nome remoto ou caminho local, mas nunca chaves ou tokens. Não haverá retry automático, pois erros de autenticação e recurso inexistente não são transitórios e retries podem dificultar diagnóstico ou ampliar chamadas externas.

### 7. Testar com mocks nas fronteiras

Os testes substituirão `hub.pull`, `check_env_vars`, `save_yaml` e, quando necessário, a saída de terminal. Um `ChatPromptTemplate` sintético verificará a preservação de `{bug_report}`. Casos negativos cobrirão credencial ausente, exceção remota, papéis ausentes, tipo incompatível e falha de escrita. Nenhum teste acessará rede, `.env` real ou LangSmith.

## Risks / Trade-offs

- [Mudança futura na estrutura interna de `ChatPromptTemplate`] → Isolar a extração em função pequena e cobri-la com testes de contrato para a versão fixada em `requirements.txt`.
- [O prompt remoto contém múltiplas mensagens do mesmo papel] → Rejeitar estrutura ambígua nesta versão, evitando perda silenciosa ou concatenação que altere a semântica.
- [Uma execução sobrescreve a cópia v1 existente] → Exibir o caminho antes da gravação e manter conteúdo determinístico; o arquivo é deliberadamente o destino oficial do pull.
- [Falha de rede ou limites do LangSmith] → Encerrar com erro acionável e permitir nova execução manual, sem afirmar que o arquivo foi atualizado.
- [Exceções incluem detalhes do provedor] → Mostrar mensagem resumida e nunca interpolar variáveis de ambiente ou credenciais.
- [Mocks excessivos divergem da API real] → Construir objetos reais de `ChatPromptTemplate` nos testes de extração e mockar apenas rede e persistência.

## Migration Plan

1. Implementar funções auxiliares e o fluxo principal em `src/pull_prompts.py`.
2. Adicionar e executar os testes unitários locais.
3. Executar manualmente `python src/pull_prompts.py` em ambiente com credencial válida para confirmar a integração real.
4. Inspecionar `prompts/bug_to_user_story_v1.yml` e confirmar que os dois templates e `{bug_report}` foram preservados.

Rollback: reverter apenas `src/pull_prompts.py` e os testes adicionados. Se uma execução real substituir o YAML v1, restaurar a versão rastreada pelo Git; nenhum estado remoto é modificado pelo pull.

## Open Questions

Nenhuma questão bloqueante. A estrutura esperada do prompt remoto será validada em tempo de execução, e uma incompatibilidade será tratada como erro explícito em vez de pressupor conversão silenciosa.
