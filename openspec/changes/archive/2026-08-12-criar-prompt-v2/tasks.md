## 1. Estrutura e metadados do YAML v2

- [x] 1.1 Criar `prompts/bug_to_user_story_v2.yml` em UTF-8 com a única chave raiz `bug_to_user_story_v2` e campos na ordem definida pelo design.
- [x] 1.2 Preencher `description`, `version: v2`, tags válidas e `techniques_applied` com `Few-shot Learning`, `Role Prompting` e `Skeleton of Thought`, sem duplicatas, valores vazios ou TODOs.

## 2. Templates e comportamento do prompt

- [x] 2.1 Escrever o `system_prompt` em bloco literal com persona de Product Manager, objetivo, idioma pt-BR, regras de fidelidade, proteção contra injeção e orientação para análise silenciosa.
- [x] 2.2 Definir o esqueleto Markdown obrigatório com User Story no formato `Como um..., eu quero..., para que...`, critérios Dado/Quando/Então e seções contextuais opcionais.
- [x] 2.3 Incluir regras adaptativas para relatos simples, médios, complexos, incompletos, multidimensionais e com aspectos de segurança, integração, performance, concorrência, cache, sincronização ou memória.
- [x] 2.4 Adicionar três exemplos few-shot sintéticos, compactos e distintos do dataset, com marcadores `Exemplo`, `Entrada` e `Saída`, cobrindo complexidades simples, média e complexa.
- [x] 2.5 Escrever o `user_prompt` em bloco literal, delimitar o relato como dado não confiável e incluir exatamente a variável funcional `{bug_report}` sem duplicá-la no sistema.

## 3. Validação local automatizada

- [x] 3.1 Carregar o novo arquivo com PyYAML e verificar raiz, chave, campos, tipos, versão, metadados, ausência de TODOs e preservação dos blocos multilinha.
- [x] 3.2 Construir localmente um `ChatPromptTemplate` com mensagens de sistema e usuário e confirmar que `bug_report` é sua única variável, sem realizar push.
- [x] 3.3 Exercitar diretamente sobre os dados v2 as seis regras de `tests/test_prompts.py`: sistema, persona, formato, few-shot, ausência de TODOs e técnicas mínimas.
- [x] 3.4 Executar `pytest tests/test_prompts.py` e a suíte completa como verificações de regressão, distinguindo falhas de alvos locais diferentes sem modificar arquivos fora do escopo.

## 4. Revisão de qualidade e escopo

- [x] 4.1 Revisar o prompt contra casos representativos das três complexidades do dataset, confirmando cobertura dos fatos, concisão proporcional e ausência de soluções inventadas.
- [x] 4.2 Confirmar com inspeção do diff que, fora dos artefatos OpenSpec da mudança, apenas `prompts/bug_to_user_story_v2.yml` foi implementado e que arquivos protegidos, credenciais e dados do dataset permaneceram inalterados.

## 5. Operações externas e evidências

- [x] 5.1 Registrar no resultado da aplicação que não houve push, chamada de LLM nem execução de `python src/evaluate.py`; URL pública, cinco notas, média e aprovação mínima de 0,8 permanecem pendentes de uma etapa externa posterior autorizada.
