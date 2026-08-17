"""Testes unitários do fluxo de pull de prompts do LangSmith."""

import sys
from pathlib import Path

import pytest
from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pull_prompts


def make_prompt(*messages: tuple[str, str]) -> ChatPromptTemplate:
    """Cria um prompt real do LangChain para os testes estruturais."""
    return ChatPromptTemplate.from_messages(list(messages))


def test_pull_saves_expected_yaml_contract(monkeypatch):
    prompt = make_prompt(
        ("system", "Analise o relato sem alterar {bug_report}."),
        ("human", "{bug_report}"),
    )
    saved = {}

    def fake_pull(prompt_name):
        assert prompt_name == pull_prompts.PROMPT_NAME
        return prompt

    def fake_save_yaml(data, file_path):
        saved["data"] = data
        saved["file_path"] = file_path
        return True

    monkeypatch.setattr(pull_prompts.hub, "pull", fake_pull)
    monkeypatch.setattr(pull_prompts, "save_yaml", fake_save_yaml)

    assert pull_prompts.pull_prompts_from_langsmith() is True
    assert saved["file_path"] == str(pull_prompts.OUTPUT_PATH)

    prompt_data = saved["data"][pull_prompts.PROMPT_KEY]
    assert prompt_data == {
        "description": "Prompt para converter relatos de bugs em User Stories",
        "system_prompt": "Analise o relato sem alterar {bug_report}.",
        "user_prompt": "{bug_report}",
        "version": "v1",
        "source": "leonanluppi/bug_to_user_story_v1",
        "tags": ["bug-analysis", "user-story", "product-management"],
    }


def test_main_stops_before_network_when_credential_is_missing(monkeypatch):
    monkeypatch.setattr(pull_prompts, "check_env_vars", lambda variables: False)

    def unexpected_pull(_prompt_name):
        pytest.fail("hub.pull não deveria ser chamado sem credencial")

    monkeypatch.setattr(pull_prompts.hub, "pull", unexpected_pull)

    assert pull_prompts.main() == 1


def test_pull_handles_hub_error_without_exposing_exception(monkeypatch, capsys):
    def failing_pull(_prompt_name):
        raise RuntimeError("token-secreto-na-excecao")

    monkeypatch.setattr(pull_prompts.hub, "pull", failing_pull)

    assert pull_prompts.pull_prompts_from_langsmith() is False
    output = capsys.readouterr().out
    assert "Não foi possível baixar" in output
    assert "token-secreto-na-excecao" not in output
    assert "salvo com sucesso" not in output


def test_pull_rejects_incompatible_object(monkeypatch, capsys):
    monkeypatch.setattr(pull_prompts.hub, "pull", lambda _prompt_name: object())

    assert pull_prompts.pull_prompts_from_langsmith() is False
    output = capsys.readouterr().out
    assert "Estrutura de prompt incompatível" in output
    assert "salvo com sucesso" not in output


@pytest.mark.parametrize(
    "prompt",
    [
        make_prompt(("system", "Somente sistema {bug_report}")),
        make_prompt(("human", "Somente usuário {bug_report}")),
    ],
    ids=["sem-usuario", "sem-sistema"],
)
def test_pull_rejects_missing_required_role(monkeypatch, capsys, prompt):
    monkeypatch.setattr(pull_prompts.hub, "pull", lambda _prompt_name: prompt)

    assert pull_prompts.pull_prompts_from_langsmith() is False
    output = capsys.readouterr().out
    assert "exatamente uma mensagem de sistema" in output
    assert "salvo com sucesso" not in output


@pytest.mark.parametrize(
    "prompt",
    [
        make_prompt(
            ("system", "Sistema A"),
            ("system", "Sistema B"),
            ("human", "{bug_report}"),
        ),
        make_prompt(
            ("system", "Sistema"),
            ("human", "Usuário A: {bug_report}"),
            ("human", "Usuário B: {bug_report}"),
        ),
    ],
    ids=["sistema-duplicado", "usuario-duplicado"],
)
def test_pull_rejects_duplicated_required_role(monkeypatch, capsys, prompt):
    monkeypatch.setattr(pull_prompts.hub, "pull", lambda _prompt_name: prompt)

    assert pull_prompts.pull_prompts_from_langsmith() is False
    output = capsys.readouterr().out
    assert "exatamente uma mensagem de sistema" in output
    assert "salvo com sucesso" not in output


def test_pull_reports_persistence_failure(monkeypatch, capsys):
    prompt = make_prompt(
        ("system", "Sistema {bug_report}"),
        ("human", "{bug_report}"),
    )
    monkeypatch.setattr(pull_prompts.hub, "pull", lambda _prompt_name: prompt)
    monkeypatch.setattr(pull_prompts, "save_yaml", lambda _data, _path: False)

    assert pull_prompts.pull_prompts_from_langsmith() is False
    output = capsys.readouterr().out
    assert "Não foi possível salvar" in output
    assert "salvo com sucesso" not in output


@pytest.mark.parametrize(
    ("pull_result", "expected_code"),
    [(True, 0), (False, 1)],
)
def test_main_converts_pull_result_to_exit_code(
    monkeypatch, pull_result, expected_code
):
    monkeypatch.setattr(pull_prompts, "check_env_vars", lambda variables: True)
    monkeypatch.setattr(
        pull_prompts, "pull_prompts_from_langsmith", lambda: pull_result
    )

    assert pull_prompts.main() == expected_code
