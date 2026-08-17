"""Testes unitários do fluxo de push de prompts para o LangSmith."""

import sys
from pathlib import Path

import pytest
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import push_prompts


def valid_prompt_data() -> dict:
    """Retorna dados v2 válidos e independentes para cada teste."""
    return {
        "description": "Converte bugs em User Stories completas",
        "system_prompt": "Você é uma Product Manager experiente.",
        "user_prompt": "Relato recebido:\n{bug_report}",
        "version": "v2",
        "tags": ["bug-analysis", "Few-shot Learning"],
        "techniques_applied": ["Few-shot Learning", "Role Prompting"],
    }


def test_push_sends_public_prompt_with_metadata(monkeypatch, capsys):
    captured = {}

    def fake_push(prompt_name, prompt, **kwargs):
        captured["prompt_name"] = prompt_name
        captured["prompt"] = prompt
        captured["kwargs"] = kwargs
        return "https://smith.langchain.com/prompts/aluno/bug_to_user_story_v2"

    monkeypatch.setattr(push_prompts.hub, "push", fake_push)

    assert (
        push_prompts.push_prompt_to_langsmith(
            "aluno/bug_to_user_story_v2", valid_prompt_data()
        )
        is True
    )

    assert captured["prompt_name"] == "aluno/bug_to_user_story_v2"
    messages = captured["prompt"].messages
    assert len(messages) == 2
    assert isinstance(messages[0], SystemMessagePromptTemplate)
    assert isinstance(messages[1], HumanMessagePromptTemplate)
    assert messages[0].prompt.template == "Você é uma Product Manager experiente."
    assert messages[1].prompt.template == "Relato recebido:\n{bug_report}"

    assert captured["kwargs"]["new_repo_is_public"] is True
    assert (
        captured["kwargs"]["new_repo_description"]
        == "Converte bugs em User Stories completas"
    )
    assert captured["kwargs"]["tags"] == [
        "bug-analysis",
        "Few-shot Learning",
        "Role Prompting",
    ]
    assert "Versão: v2" in captured["kwargs"]["readme"]
    assert "- Few-shot Learning" in captured["kwargs"]["readme"]
    assert "- Role Prompting" in captured["kwargs"]["readme"]

    output = capsys.readouterr().out
    assert "Prompt publicado com sucesso" in output
    assert "https://smith.langchain.com/prompts/aluno/bug_to_user_story_v2" in output


def test_validate_prompt_rejects_non_mapping():
    is_valid, errors = push_prompts.validate_prompt("inválido")

    assert is_valid is False
    assert errors == ["O conteúdo de bug_to_user_story_v2 deve ser um mapeamento"]


@pytest.mark.parametrize(
    "field",
    [
        "description",
        "system_prompt",
        "user_prompt",
        "version",
        "tags",
        "techniques_applied",
    ],
)
def test_validate_prompt_reports_missing_required_field(field):
    prompt_data = valid_prompt_data()
    prompt_data.pop(field)

    is_valid, errors = push_prompts.validate_prompt(prompt_data)

    assert is_valid is False
    assert any(field in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("description", "  ", "texto não vazio"),
        ("system_prompt", 123, "texto não vazio"),
        ("user_prompt", None, "texto não vazio"),
        ("version", "v1", "exatamente 'v2'"),
        ("tags", [], "lista não vazia"),
        ("tags", ["bug-analysis", 123], "lista não vazia"),
        ("techniques_applied", ["Few-shot Learning"], "ao menos dois"),
        ("techniques_applied", ["Few-shot Learning", ""], "ao menos dois"),
        ("user_prompt", "Relato sem variável", "{bug_report}"),
        ("system_prompt", "[TODO] definir persona", "TODO"),
        ("user_prompt", "TODO: {bug_report}", "TODO"),
    ],
)
def test_validate_prompt_reports_invalid_values(field, value, expected_error):
    prompt_data = valid_prompt_data()
    prompt_data[field] = value

    is_valid, errors = push_prompts.validate_prompt(prompt_data)

    assert is_valid is False
    assert any(expected_error in error for error in errors)


def test_push_rejects_invalid_template_syntax_before_hub(monkeypatch, capsys):
    prompt_data = valid_prompt_data()
    prompt_data["system_prompt"] = "Template com chave inválida {"

    def unexpected_push(*_args, **_kwargs):
        pytest.fail("hub.push não deveria receber um template incompatível")

    monkeypatch.setattr(push_prompts.hub, "push", unexpected_push)

    assert (
        push_prompts.push_prompt_to_langsmith(
            "aluno/bug_to_user_story_v2", prompt_data
        )
        is False
    )
    output = capsys.readouterr().out
    assert "Não foi possível construir" in output
    assert "publicado com sucesso" not in output


def test_push_handles_hub_error_without_exposing_exception(monkeypatch, capsys):
    def failing_push(*_args, **_kwargs):
        raise RuntimeError("token-secreto-na-excecao")

    monkeypatch.setattr(push_prompts.hub, "push", failing_push)

    assert (
        push_prompts.push_prompt_to_langsmith(
            "aluno/bug_to_user_story_v2", valid_prompt_data()
        )
        is False
    )
    output = capsys.readouterr().out
    assert "Não foi possível publicar" in output
    assert "token-secreto-na-excecao" not in output
    assert "publicado com sucesso" not in output


@pytest.mark.parametrize("invalid_url", [None, "", "   "])
def test_push_rejects_invalid_returned_url(monkeypatch, capsys, invalid_url):
    monkeypatch.setattr(
        push_prompts.hub, "push", lambda *_args, **_kwargs: invalid_url
    )

    assert (
        push_prompts.push_prompt_to_langsmith(
            "aluno/bug_to_user_story_v2", valid_prompt_data()
        )
        is False
    )
    output = capsys.readouterr().out
    assert "não retornou uma URL válida" in output
    assert "publicado com sucesso" not in output


def test_main_stops_when_environment_is_incomplete(monkeypatch):
    monkeypatch.setattr(push_prompts, "check_env_vars", lambda variables: False)

    def unexpected_load(_path):
        pytest.fail("load_yaml não deveria ser chamado sem configuração")

    monkeypatch.setattr(push_prompts, "load_yaml", unexpected_load)

    assert push_prompts.main() == 1


def test_main_rejects_whitespace_only_environment(monkeypatch):
    monkeypatch.setattr(push_prompts, "check_env_vars", lambda variables: True)
    monkeypatch.setenv("LANGSMITH_API_KEY", "   ")
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", "aluno")

    def unexpected_load(_path):
        pytest.fail("load_yaml não deveria ser chamado com variável vazia")

    monkeypatch.setattr(push_prompts, "load_yaml", unexpected_load)

    assert push_prompts.main() == 1


@pytest.mark.parametrize("document", [None, [], "texto"])
def test_main_rejects_invalid_yaml_document(monkeypatch, document):
    configure_valid_environment(monkeypatch)
    monkeypatch.setattr(push_prompts, "load_yaml", lambda _path: document)
    forbid_real_push(monkeypatch)

    assert push_prompts.main() == 1


@pytest.mark.parametrize(
    "document",
    [
        {},
        {"outra_chave": valid_prompt_data()},
        {push_prompts.PROMPT_KEY: "não é mapeamento"},
    ],
)
def test_main_rejects_missing_or_invalid_top_level_key(monkeypatch, document):
    configure_valid_environment(monkeypatch)
    monkeypatch.setattr(push_prompts, "load_yaml", lambda _path: document)
    forbid_real_push(monkeypatch)

    assert push_prompts.main() == 1


def test_main_lists_validation_errors_without_push(monkeypatch, capsys):
    configure_valid_environment(monkeypatch)
    prompt_data = valid_prompt_data()
    prompt_data.update(
        {
            "description": "",
            "version": "v1",
            "tags": [],
            "techniques_applied": [],
            "user_prompt": "sem variável",
        }
    )
    monkeypatch.setattr(
        push_prompts,
        "load_yaml",
        lambda _path: {push_prompts.PROMPT_KEY: prompt_data},
    )
    forbid_real_push(monkeypatch)

    assert push_prompts.main() == 1
    output = capsys.readouterr().out
    assert "erros de validação" in output
    assert "description" in output
    assert "version" in output
    assert "tags" in output
    assert "techniques_applied" in output
    assert "{bug_report}" in output


@pytest.mark.parametrize(
    ("push_result", "expected_code"),
    [(True, 0), (False, 1)],
)
def test_main_builds_versioned_name_and_converts_result_to_exit_code(
    monkeypatch, push_result, expected_code
):
    configure_valid_environment(monkeypatch)
    prompt_data = valid_prompt_data()
    monkeypatch.setattr(
        push_prompts,
        "load_yaml",
        lambda path: {push_prompts.PROMPT_KEY: prompt_data},
    )
    captured = {}

    def fake_push_prompt(prompt_name, received_data):
        captured["prompt_name"] = prompt_name
        captured["prompt_data"] = received_data
        return push_result

    monkeypatch.setattr(
        push_prompts, "push_prompt_to_langsmith", fake_push_prompt
    )

    assert push_prompts.main() == expected_code
    assert captured["prompt_name"] == "aluno/bug_to_user_story_v2"
    assert captured["prompt_data"] is prompt_data


def configure_valid_environment(monkeypatch):
    """Configura apenas valores sintéticos usados pela CLI nos testes."""
    monkeypatch.setattr(push_prompts, "check_env_vars", lambda variables: True)
    monkeypatch.setenv("LANGSMITH_API_KEY", "chave-sintetica")
    monkeypatch.setenv("USERNAME_LANGSMITH_HUB", "aluno")


def forbid_real_push(monkeypatch):
    """Falha o teste caso o fluxo tente atravessar a fronteira externa."""

    def unexpected_push(*_args, **_kwargs):
        pytest.fail("Nenhuma publicação deveria ocorrer para entrada inválida")

    monkeypatch.setattr(push_prompts.hub, "push", unexpected_push)
