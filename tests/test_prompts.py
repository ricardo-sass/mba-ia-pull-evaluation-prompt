"""
Testes automatizados para validação de prompts.
"""
from pathlib import Path
from typing import Any

import pytest
import yaml
from langchain_core.prompts import ChatPromptTemplate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: Path) -> Any:
    """Carrega prompts do arquivo YAML."""
    with file_path.open("r", encoding="utf-8") as prompt_file:
        return yaml.safe_load(prompt_file)


@pytest.fixture(scope="class")
def prompt_data() -> dict:
    """Carrega e seleciona o prompt que será validado pela suíte."""
    assert PROMPT_PATH.is_file(), (
        f"Arquivo do prompt não encontrado: {PROMPT_PATH}"
    )

    try:
        prompt_document = load_prompts(PROMPT_PATH)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        pytest.fail(f"Não foi possível carregar o YAML do prompt: {exc}")

    assert isinstance(prompt_document, dict), (
        "A raiz do arquivo de prompt deve ser um mapeamento YAML."
    )
    assert PROMPT_KEY in prompt_document, (
        f"A chave obrigatória '{PROMPT_KEY}' não foi encontrada no YAML."
    )

    selected_prompt = prompt_document[PROMPT_KEY]
    assert isinstance(selected_prompt, dict), (
        f"O conteúdo de '{PROMPT_KEY}' deve ser um mapeamento YAML."
    )
    return selected_prompt


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data: dict) -> None:
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        system_prompt = prompt_data.get("system_prompt")

        assert isinstance(system_prompt, str), (
            "O campo 'system_prompt' deve existir e ser um texto."
        )
        assert system_prompt.strip(), "O campo 'system_prompt' não pode estar vazio."

    def test_prompt_has_role_definition(self, prompt_data: dict) -> None:
        """Verifica se o prompt define explicitamente uma persona."""
        system_prompt = prompt_data.get("system_prompt")
        assert isinstance(system_prompt, str), (
            "O campo 'system_prompt' deve ser um texto para validar a persona."
        )
        normalized_prompt = system_prompt.casefold()
        role_markers = (
            "você é",
            "atue como",
            "aja como",
            "seu papel é",
        )

        assert any(marker in normalized_prompt for marker in role_markers), (
            "O 'system_prompt' deve definir uma persona explicitamente, por exemplo: "
            "'Você é um Product Manager'."
        )

    def test_prompt_mentions_format(self, prompt_data: dict) -> None:
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt")
        assert isinstance(system_prompt, str), (
            "O campo 'system_prompt' deve ser um texto para validar o formato."
        )
        normalized_prompt = system_prompt.casefold()
        has_markdown_format = "markdown" in normalized_prompt
        user_story_markers = ("como um", "eu quero", "para que")
        has_user_story_format = all(
            marker in normalized_prompt for marker in user_story_markers
        )

        assert has_markdown_format or has_user_story_format, (
            "O 'system_prompt' deve exigir saída em Markdown ou no formato "
            "'Como um..., eu quero..., para que...'."
        )

    def test_prompt_has_few_shot_examples(self, prompt_data: dict) -> None:
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt")
        assert isinstance(system_prompt, str), (
            "O campo 'system_prompt' deve ser um texto para validar os exemplos."
        )
        normalized_prompt = system_prompt.casefold()
        input_markers = ("entrada", "relato de bug", "bug report")
        output_markers = ("saída", "saida", "user story gerada", "resultado")
        has_example = "exemplo" in normalized_prompt
        has_input = any(marker in normalized_prompt for marker in input_markers)
        has_output = any(marker in normalized_prompt for marker in output_markers)

        assert has_example and has_input and has_output, (
            "O 'system_prompt' deve conter ao menos um exemplo few-shot completo, "
            "com entrada e saída identificáveis."
        )

    def test_prompt_no_todos(self, prompt_data: dict) -> None:
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        fields_with_todo = [
            field
            for field, value in prompt_data.items()
            if isinstance(value, str) and "todo" in value.casefold()
        ]

        assert not fields_with_todo, (
            "Os campos textuais do prompt não podem conter TODOs. "
            f"Campos pendentes: {', '.join(fields_with_todo)}"
        )

    def test_minimum_techniques(self, prompt_data: dict) -> None:
        """Verifica se pelo menos duas técnicas válidas foram declaradas."""
        techniques = prompt_data.get("techniques_applied")

        assert isinstance(techniques, list), (
            "O campo 'techniques_applied' deve ser uma lista."
        )
        valid_techniques = [
            technique
            for technique in techniques
            if isinstance(technique, str) and technique.strip()
        ]
        assert len(valid_techniques) >= 2, (
            "O campo 'techniques_applied' deve declarar pelo menos duas técnicas "
            "como textos não vazios."
        )

    def test_prompt_has_coverage_and_adaptive_structure(
        self,
        prompt_data: dict,
    ) -> None:
        """Valida cobertura, níveis de confiança e profundidade adaptativa."""
        system_prompt = prompt_data.get("system_prompt")
        assert isinstance(system_prompt, str), (
            "O campo 'system_prompt' deve ser um texto para validar a cobertura."
        )
        normalized_prompt = system_prompt.casefold()

        coverage_markers = (
            "matriz de cobertura",
            "ator afetado",
            "comportamento observado",
            "comportamento esperado",
            "dimensões afetadas",
        )
        confidence_markers = (
            "fato observado",
            "resultado esperado inferível",
            "recomendação técnica",
        )
        complexity_markers = (
            "bug simples",
            "bug médio",
            "bug complexo",
            "estrutura de saída adaptativa",
            "nunca crie seção vazia",
        )

        assert all(marker in normalized_prompt for marker in coverage_markers), (
            "O prompt deve exigir uma matriz de cobertura dos fatos relevantes."
        )
        assert all(marker in normalized_prompt for marker in confidence_markers), (
            "O prompt deve distinguir fatos, inferências e recomendações."
        )
        assert all(marker in normalized_prompt for marker in complexity_markers), (
            "O prompt deve definir estrutura adaptativa e proibir seções vazias."
        )

    def test_prompt_has_three_consistent_few_shot_pairs(
        self,
        prompt_data: dict,
    ) -> None:
        """Confirma três few-shots completos e compatíveis com LangChain."""
        system_prompt = prompt_data.get("system_prompt")
        user_prompt = prompt_data.get("user_prompt")
        assert isinstance(system_prompt, str)
        assert isinstance(user_prompt, str)

        assert system_prompt.count("— Entrada") == 3, (
            "O prompt deve conter exatamente três entradas few-shot explícitas."
        )
        assert system_prompt.count("— Saída") == 3, (
            "O prompt deve conter exatamente três saídas few-shot explícitas."
        )
        assert "## Critérios Técnicos e Recomendações" in system_prompt, (
            "Os few-shots devem demonstrar cobertura técnica rastreável."
        )
        assert "## User Story Principal" in system_prompt, (
            "Os few-shots devem demonstrar organização multidimensional."
        )
        assert "## Tarefas Técnicas Sugeridas" in system_prompt, (
            "O exemplo complexo deve demonstrar tarefas técnicas sugeridas."
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )
        assert prompt_template.input_variables == ["bug_report"], (
            "O ChatPromptTemplate deve exigir somente a variável 'bug_report'."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
