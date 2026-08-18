# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused unit tests for invoke argument validation helpers."""

from __future__ import annotations

from unittest.mock import patch
import json

import pytest
import typer
from typer.testing import CliRunner
import moldflow

from moldflow_cli.commands import build_cli_app
from moldflow_cli.invoke_binding import _append_payload_items, _validate_step_item_path_conflicts

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_non_object_json_payload():
    """Non-object JSON payloads should fail with a clear contract error."""
    parsed_items = []
    method_steps = [{"name": "cli_echo"}]
    with pytest.raises(typer.BadParameter, match="JSON parameters must be a JSON object"):
        _append_payload_items(parsed_items, [1, 2, 3], method_steps)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_duplicate_argument_path():
    """The same argument path provided multiple times should be rejected."""
    items = [(["value"], "a", "cli"), (["value"], "b", "cli")]
    with pytest.raises(typer.BadParameter, match="Duplicate argument path"):
        _validate_step_item_path_conflicts("cli_echo", items)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_duplicate_argument_path_case_insensitive_after_normalization():
    """Case-variant duplicate params should still be rejected."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def _cli_echo(self, value: str):
        del self
        return value

    setattr(moldflow.Synergy, "cli_echo", _cli_echo)
    try:

        class Sy:
            """Minimal synergy test double for cli_echo."""

            def cli_echo(self, value: str):
                """Echo helper used for duplicate-argument validation."""
                return value

        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_echo", "Value=a", "value=b"])

        assert result.exit_code != 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "duplicate argument path" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_single_step_json_wrapper_is_not_unwrapped_when_param_matches_step_name():
    """Do not unwrap when method really expects a param named like the step."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_echo_dict", None)

    def _cli_echo_dict(self, cli_echo_dict):
        del self
        return cli_echo_dict

    setattr(moldflow.Synergy, "cli_echo_dict", _cli_echo_dict)

    class Sy:
        """Fake Synergy object exposing cli_echo_dict."""

        def cli_echo_dict(self, cli_echo_dict):
            """Echo dict payload unchanged."""
            return cli_echo_dict

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.cli_echo_dict",
                    "--params-json",
                    '{"cli_echo_dict": {"a": 1}}',
                    "--json-output",
                ],
            )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["result"]["a"] == 1
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo_dict")
        else:
            setattr(moldflow.Synergy, "cli_echo_dict", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_includes_schema_version():
    """Describe structured output should include a stable schema version."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert "target" in payload and "params" in payload


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_object_output_includes_schema_version():
    """Object-like invoke JSON output should include schema_version."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_echo_obj", None)

    def _cli_echo_obj(self):
        del self

        class Obj:
            """Simple object-like return payload."""

            def __init__(self):
                self.name = "x"

        return Obj()

    setattr(moldflow.Synergy, "cli_echo_obj", _cli_echo_obj)

    class Sy:
        """Fake Synergy object exposing cli_echo_obj."""

        def cli_echo_obj(self):
            """Return a simple object-like payload."""

            class Obj:
                """Simple object-like return payload."""

                def __init__(self):
                    self.name = "x"

            return Obj()

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_echo_obj", "--json-output"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["schema_version"] == "1.0"
        assert payload["ok"] is True
        assert payload["result"]["attributes"]["name"] == "x"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo_obj")
        else:
            setattr(moldflow.Synergy, "cli_echo_obj", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_invalid_target_identifier_segment():
    """Invalid target segments should fail fast with a clear validation error."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(app, ["invoke", "synergy.open-project"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "must be a valid identifier" in combined.lower()
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_invalid_argument_path_identifier_segment():
    """Invalid argument path segments should be rejected before invocation."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(app, ["invoke", "synergy.open_project", "pa-th=test.mpi"])
    assert result.exit_code != 0
    assert result.exception is not None
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()
