"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import (
    check_env_vars,
    load_yaml,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

PROMPT_PATH = Path("prompts/bug_to_user_story_v2.yml")
PROMPT_KEY = "bug_to_user_story_v2"
PROMPT_REPO_SUFFIX = "bug_to_user_story_v2"
REQUIRED_ENV_VARS = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]


def _deduplicate_strings(values: list[str]) -> list[str]:
    """Remove duplicatas preservando a ordem original."""
    unique_values = []
    seen = set()

    for value in values:
        if value not in seen:
            unique_values.append(value)
            seen.add(value)

    return unique_values


def _build_prompt_readme(prompt_data: dict) -> str:
    """Gera a documentação curta enviada como metadado ao LangSmith."""
    techniques = "\n".join(
        f"- {technique}" for technique in prompt_data["techniques_applied"]
    )
    return (
        f"# {PROMPT_REPO_SUFFIX}\n\n"
        f"Versão: {prompt_data['version']}\n\n"
        "## Técnicas aplicadas\n\n"
        f"{techniques}\n"
    )


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_data["system_prompt"]),
                ("human", prompt_data["user_prompt"]),
            ]
        )
    except Exception:
        print("❌ Não foi possível construir o ChatPromptTemplate.")
        print("   Verifique a sintaxe e o escape de chaves nos templates.")
        return False

    tags = _deduplicate_strings(
        prompt_data["tags"] + prompt_data["techniques_applied"]
    )
    readme = _build_prompt_readme(prompt_data)

    print(f"Publicando prompt público no LangSmith Hub: {prompt_name}")

    try:
        prompt_url = hub.push(
            prompt_name,
            prompt,
            new_repo_is_public=True,
            new_repo_description=prompt_data["description"],
            readme=readme,
            tags=tags,
        )
    except Exception:
        print(f"❌ Não foi possível publicar o prompt '{prompt_name}'.")
        print("   Verifique sua credencial, seu username, seu acesso e sua conexão.")
        return False

    if not isinstance(prompt_url, str) or not prompt_url.strip():
        print("❌ O LangSmith não retornou uma URL válida para o prompt publicado.")
        return False

    print("✅ Prompt publicado com sucesso.")
    print(f"URL pública: {prompt_url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    if not isinstance(prompt_data, dict):
        return False, ["O conteúdo de bug_to_user_story_v2 deve ser um mapeamento"]

    errors = []

    safe_prompt_data = dict(prompt_data)
    if not isinstance(safe_prompt_data.get("system_prompt"), str):
        safe_prompt_data["system_prompt"] = ""
    if not isinstance(safe_prompt_data.get("techniques_applied"), list):
        safe_prompt_data["techniques_applied"] = []

    _, structure_errors = validate_prompt_structure(safe_prompt_data)
    errors.extend(structure_errors)

    required_text_fields = ["description", "system_prompt", "user_prompt"]
    for field in required_text_fields:
        value = prompt_data.get(field)
        if field not in prompt_data:
            error = f"Campo obrigatório faltando: {field}"
            if error not in errors:
                errors.append(error)
        elif not isinstance(value, str) or not value.strip():
            errors.append(f"Campo '{field}' deve ser um texto não vazio")

    version = prompt_data.get("version")
    if "version" not in prompt_data:
        error = "Campo obrigatório faltando: version"
        if error not in errors:
            errors.append(error)
    elif version != "v2":
        errors.append("Campo 'version' deve ser exatamente 'v2'")

    tags = prompt_data.get("tags")
    if "tags" not in prompt_data:
        errors.append("Campo obrigatório faltando: tags")
    elif (
        not isinstance(tags, list)
        or not tags
        or any(not isinstance(tag, str) or not tag.strip() for tag in tags)
    ):
        errors.append("Campo 'tags' deve ser uma lista não vazia de textos válidos")

    techniques = prompt_data.get("techniques_applied")
    if "techniques_applied" not in prompt_data:
        errors.append("Campo obrigatório faltando: techniques_applied")
    elif (
        not isinstance(techniques, list)
        or len(techniques) < 2
        or any(
            not isinstance(technique, str) or not technique.strip()
            for technique in techniques
        )
    ):
        errors.append(
            "Campo 'techniques_applied' deve conter ao menos dois textos válidos"
        )

    user_prompt = prompt_data.get("user_prompt")
    if isinstance(user_prompt, str) and "{bug_report}" not in user_prompt:
        errors.append("Campo 'user_prompt' deve conter a variável {bug_report}")

    for field in ["system_prompt", "user_prompt"]:
        value = prompt_data.get(field)
        if isinstance(value, str) and "TODO" in value.upper():
            errors.append(f"Campo '{field}' não pode conter TODOs")

    return len(errors) == 0, _deduplicate_strings(errors)


def main() -> int:
    """Valida e publica o prompt otimizado no LangSmith Prompt Hub."""
    print_section_header("PUSH DO PROMPT OTIMIZADO")

    if not check_env_vars(REQUIRED_ENV_VARS):
        return 1

    whitespace_only_vars = [
        variable
        for variable in REQUIRED_ENV_VARS
        if not os.getenv(variable, "").strip()
    ]
    if whitespace_only_vars:
        print("❌ Variáveis de ambiente vazias:")
        for variable in whitespace_only_vars:
            print(f"   - {variable}")
        return 1

    print(f"Carregando prompt local: {PROMPT_PATH}")
    prompt_document = load_yaml(str(PROMPT_PATH))

    if not isinstance(prompt_document, dict):
        print("❌ O arquivo do prompt deve conter um mapeamento YAML válido.")
        return 1

    prompt_data = prompt_document.get(PROMPT_KEY)
    if not isinstance(prompt_data, dict):
        print(f"❌ Chave obrigatória ausente ou inválida: {PROMPT_KEY}")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ O prompt otimizado possui erros de validação:")
        for error in errors:
            print(f"   - {error}")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    prompt_name = f"{username}/{PROMPT_REPO_SUFFIX}"

    return 0 if push_prompt_to_langsmith(prompt_name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
