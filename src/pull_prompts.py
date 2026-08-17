"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
PROMPT_KEY = "bug_to_user_story_v1"
OUTPUT_PATH = Path("prompts/bug_to_user_story_v1.yml")


def _get_text_template(message: object) -> str:
    """Extrai o template textual de uma mensagem do LangChain."""
    prompt = getattr(message, "prompt", None)
    template = getattr(prompt, "template", None)

    if not isinstance(template, str):
        raise ValueError("a mensagem obrigatória não possui um template textual")

    return template


def extract_prompt_templates(prompt: ChatPromptTemplate) -> tuple[str, str]:
    """Extrai exatamente um template de sistema e um de usuário."""
    if not isinstance(prompt, ChatPromptTemplate):
        raise ValueError("o objeto retornado não é um ChatPromptTemplate")

    system_templates = []
    user_templates = []

    for message in prompt.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            system_templates.append(_get_text_template(message))
        elif isinstance(message, HumanMessagePromptTemplate):
            user_templates.append(_get_text_template(message))
        else:
            raise ValueError("o prompt contém um papel de mensagem não suportado")

    if len(system_templates) != 1 or len(user_templates) != 1:
        raise ValueError(
            "o prompt deve conter exatamente uma mensagem de sistema "
            "e uma mensagem de usuário"
        )

    return system_templates[0], user_templates[0]


def pull_prompts_from_langsmith() -> bool:
    """Baixa o prompt inicial do LangSmith e salva sua versão YAML local."""
    print(f"Baixando prompt do LangSmith Hub: {PROMPT_NAME}")

    try:
        prompt = hub.pull(PROMPT_NAME)
    except Exception:
        print(f"❌ Não foi possível baixar o prompt '{PROMPT_NAME}'.")
        print("   Verifique sua credencial, seu acesso ao prompt e sua conexão.")
        return False

    try:
        system_prompt, user_prompt = extract_prompt_templates(prompt)
    except ValueError as error:
        print(f"❌ Estrutura de prompt incompatível: {error}.")
        return False

    prompt_data = {
        PROMPT_KEY: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source": PROMPT_NAME,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    print(f"Salvando prompt em: {OUTPUT_PATH}")
    if not save_yaml(prompt_data, str(OUTPUT_PATH)):
        print(f"❌ Não foi possível salvar o prompt em '{OUTPUT_PATH}'.")
        return False

    print(f"✅ Prompt salvo com sucesso em '{OUTPUT_PATH}'.")
    return True


def main() -> int:
    """Executa o fluxo de pull e retorna um código de saída para a CLI."""
    print_section_header("PULL DO PROMPT INICIAL")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
