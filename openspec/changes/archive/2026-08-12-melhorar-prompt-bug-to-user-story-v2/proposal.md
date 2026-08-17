## Why

A avaliação real do prompt v2 obteve média geral 0,8054, mas foi reprovada porque `F1-Score` (0,72) e `Correctness` (0,76) ficaram abaixo do mínimo de 0,8. O resultado indica sobretudo baixa cobertura das informações esperadas: o prompt atual favorece concisão e restringe recomendações técnicas, enquanto as referências do dataset exigem critérios funcionais, contexto, prevenção, soluções técnicas e, nos casos complexos, tarefas e métricas de sucesso.

## What Changes

- Reorientar `prompts/bug_to_user_story_v2.yml` para maximizar cobertura factual e semântica das referências sem perder a precisão já aprovada (0,81).
- Adotar um contrato de saída adaptativo alinhado aos três níveis do dataset: conciso para bugs simples, enriquecido com contexto e critérios adicionais para bugs médios, e completo por dimensão para bugs complexos.
- Exigir uma varredura interna de cobertura de fatos, comportamento esperado, prevenção, erro, caso-limite, impacto e detalhes técnicos antes da resposta.
- Permitir deduções e recomendações técnicas controladas quando forem consequência direta do relato ou prática padrão necessária para tornar o aceite testável, identificando-as como recomendações em vez de fatos observados.
- Ampliar os exemplos few-shot para ensinar o mesmo nível de detalhamento, vocabulário e organização encontrados nas referências do dataset, sem copiar casos do dataset literalmente.
- Reforçar os critérios locais para detectar regressões na estrutura adaptativa, na cobertura e na separação entre fatos e recomendações.
- Manter `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl` inalterados.
- Publicar a nova revisão no LangSmith e executar nova avaliação como etapas externas posteriores, repetindo a calibração por até cinco iterações se alguma métrica continuar abaixo de 0,8.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `prompt-otimizado-v2`: alterar os requisitos de fidelidade, formato adaptativo, cobertura semântica, recomendações controladas, exemplos few-shot e barreira de qualidade para corrigir o déficit de recall observado sem reduzir clareza ou precisão abaixo de 0,8.

## Impact

- **Arquivo principal:** `prompts/bug_to_user_story_v2.yml`, mantendo a chave, a versão e a variável `{bug_report}` existentes.
- **Testes locais:** `tests/test_prompts.py` poderá receber verificações estruturais adicionais sem depender de rede; a suíte existente deverá continuar aprovada.
- **Especificação:** `openspec/specs/prompt-otimizado-v2/spec.md` será modificada após a aplicação e posterior arquivamento desta mudança.
- **Sistemas externos:** a publicação por `python src/push_prompts.py` e a avaliação por `python src/evaluate.py` dependem de rede, credenciais válidas, LangSmith e chamadas pagas aos modelos configurados. Nenhum segredo ou conteúdo de `.env` será registrado.
- **Compatibilidade:** não haverá mudança de API, nova dependência ou acoplamento a um provedor; o prompt continuará utilizável com OpenAI e Google.
- **Não objetivos:** não alterar o dataset, os cálculos das métricas, os modelos configurados nem declarar aprovação antes de existirem evidências reais da nova avaliação.
