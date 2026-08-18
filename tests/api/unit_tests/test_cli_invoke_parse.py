# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused invoke parsing/validation tests for moldflow CLI."""

# Test modules intentionally use many tiny inline doubles to mirror CLI call patterns.
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument,too-many-lines

from __future__ import annotations

from unittest.mock import patch
import json
import inspect

import pytest
from typer.testing import CliRunner
import moldflow
from moldflow.cli_input_metadata import cli_input_adapter

from moldflow_cli.commands import build_cli_app
from moldflow_cli.invoke_binding import _bucket_items_by_step, _coerce_final_value
from tests.api.unit_tests.conftest import strip_ansi

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_null_byte_in_value():
    """Parameters containing null bytes must be rejected before invocation."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_echo", "value=abc\x00def"])

        # Should fail validation before Synergy instantiation.
        assert r.exit_code != 0
        out = (getattr(r, "stdout", "") or getattr(r, "output", "")) + (
            getattr(r, "stderr", "") or ""
        )
        assert "null byte" in out.lower()
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_control_characters_in_value():
    """Values containing newlines/tabs must be rejected."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_echo", "value=hello\nworld"])

        assert r.exit_code != 0
        out = (getattr(r, "stdout", "") or getattr(r, "output", "")) + (
            getattr(r, "stderr", "") or ""
        )
        assert (
            "control characters" in out.lower() or "newline" in out.lower() or "tab" in out.lower()
        )
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_control_characters_even_when_value_would_parse_to_int():
    """Control chars should be rejected before scalar coercion for non-string params too."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_int_echo", None)

    def cli_int_echo(self, value: int) -> int:
        return value

    setattr(moldflow.Synergy, "cli_int_echo", cli_int_echo)

    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_int_echo", "value=\n1\n"])

        assert r.exit_code != 0
        combined = (getattr(r, "stdout", "") or getattr(r, "output", "")) + (
            getattr(r, "stderr", "") or ""
        )
        assert "control characters" in combined.lower() or "newline" in combined.lower()
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_int_echo")
        else:
            setattr(moldflow.Synergy, "cli_int_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_allows_shell_metacharacters_in_value():
    """Shell metacharacters should be accepted as literal argument content."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    class Sy:
        def cli_echo(self, value: str) -> str:
            return value

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_echo", "value=a|b&c<d>e$"])

        assert r.exit_code == 0
        assert "a|b&c<d>e$" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_allows_apostrophes_in_plain_values():
    """Ordinary punctuation like apostrophes should not be rejected as shell meta."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    class Sy:
        def cli_echo(self, value: str) -> str:
            return value

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_echo", "value=O'Neil"])

        assert r.exit_code == 0
        assert "O'Neil" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_preserves_numeric_looking_string_when_param_is_str():
    """String-annotated params should not be auto-coerced to int/float."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_type_name", None)

    def cli_type_name(self, value: str) -> str:
        return type(value).__name__

    setattr(moldflow.Synergy, "cli_type_name", cli_type_name)

    class Sy:
        def cli_type_name(self, value: str) -> str:
            return type(value).__name__

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_type_name", "value=00123"])

        assert r.exit_code == 0
        assert "str" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_type_name")
        else:
            setattr(moldflow.Synergy, "cli_type_name", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_preserves_numeric_looking_string_for_string_forward_ref_forms():
    """Forward-ref optional-string forms should preserve literal string values."""
    app = build_cli_app()

    orig_optional = getattr(moldflow.Synergy, "cli_type_name_optional", None)
    orig_pipe = getattr(moldflow.Synergy, "cli_type_name_pipe", None)
    orig_typing = getattr(moldflow.Synergy, "cli_type_name_typing_optional", None)

    def cli_type_name_optional(self, value):
        return type(value).__name__

    def cli_type_name_pipe(self, value):
        return type(value).__name__

    def cli_type_name_typing_optional(self, value):
        return type(value).__name__

    cli_type_name_optional.__annotations__ = {"value": "Optional[str]", "return": "str"}
    cli_type_name_pipe.__annotations__ = {"value": "str|None", "return": "str"}
    cli_type_name_typing_optional.__annotations__ = {
        "value": "typing.Optional[str]",
        "return": "str",
    }

    setattr(moldflow.Synergy, "cli_type_name_optional", cli_type_name_optional)
    setattr(moldflow.Synergy, "cli_type_name_pipe", cli_type_name_pipe)
    setattr(moldflow.Synergy, "cli_type_name_typing_optional", cli_type_name_typing_optional)

    class Sy:
        def cli_type_name_optional(self, value):
            return type(value).__name__

        def cli_type_name_pipe(self, value):
            return type(value).__name__

        def cli_type_name_typing_optional(self, value):
            return type(value).__name__

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r1 = runner.invoke(app, ["invoke", "synergy.cli_type_name_optional", "value=00123"])
            r2 = runner.invoke(app, ["invoke", "synergy.cli_type_name_pipe", "value=00123"])
            r3 = runner.invoke(
                app, ["invoke", "synergy.cli_type_name_typing_optional", "value=00123"]
            )

        assert r1.exit_code == 0
        assert r2.exit_code == 0
        assert r3.exit_code == 0
        assert "str" in r1.stdout
        assert "str" in r2.stdout
        assert "str" in r3.stdout
    finally:
        if orig_optional is None:
            delattr(moldflow.Synergy, "cli_type_name_optional")
        else:
            setattr(moldflow.Synergy, "cli_type_name_optional", orig_optional)
        if orig_pipe is None:
            delattr(moldflow.Synergy, "cli_type_name_pipe")
        else:
            setattr(moldflow.Synergy, "cli_type_name_pipe", orig_pipe)
        if orig_typing is None:
            delattr(moldflow.Synergy, "cli_type_name_typing_optional")
        else:
            setattr(moldflow.Synergy, "cli_type_name_typing_optional", orig_typing)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_multi_step_requires_param_after_step():
    """Multi-step invoke must require a parameter name after the step."""
    app = build_cli_app()

    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line",
                # Missing parameter name after the step (only 'find_plot_by_name=')
                "find_plot_by_name=",
            ],
        )

    # Should fail during argument routing before Synergy instantiation.
    assert result.exit_code != 0
    err = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "must specify a parameter name" in err.lower()
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_multi_step_json_requires_step_grouping():
    """Multi-step JSON input should explain step grouping when users flatten parameters."""
    app = build_cli_app()

    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line",
                "--params-json",
                '{"plot_name":"My Plot"}',
            ],
        )

    assert result.exit_code != 0
    err = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "find_plot_by_name" in err
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_bucket_items_by_step_reports_json_grouping_guidance():
    """The underlying routing error should explicitly tell JSON callers to group by step name."""

    method_steps = [{"name": "find_plot_by_name"}, {"name": "get_probe_plot_probe_line"}]
    parsed_items = [(["plot_name"], "My Plot", "json")]

    with pytest.raises(Exception, match="group parameters by step name"):
        _bucket_items_by_step(method_steps, parsed_items)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_input_literal():
    """Provide parameters via --json-input (literal) and ensure they are routed."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_params", None)

    def cli_params(self, name: str, path: str) -> str:
        return f"name={name};path={path}"

    setattr(moldflow.Synergy, "cli_params", cli_params)

    class Sy:
        def cli_params(self, name: str, path: str) -> str:
            return f"name={name};path={path}"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            payload = '{"name":"test","path":"C:\\\\Projects\\\\MyProject"}'
            r = runner.invoke(app, ["invoke", "synergy.cli_params", "--params-json", payload])

        assert r.exit_code == 0
        assert "name=test" in r.stdout
        assert "C:\\Projects\\MyProject" in r.stdout or "MyProject" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_params")
        else:
            setattr(moldflow.Synergy, "cli_params", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_input_allows_multiline_text():
    """JSON-sourced strings may contain newlines/tabs and should be accepted."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    class Sy:
        def cli_echo(self, value: str) -> str:
            return value

    try:
        payload = json.dumps({"value": "line1\nline2\tindented"})
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_echo", "--params-json", payload])

        assert r.exit_code == 0, (getattr(r, "stdout", "") or getattr(r, "output", "")) + (
            getattr(r, "stderr", "") or ""
        )
        assert "line1" in r.stdout
        assert "line2" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_missing_required_json_param_fails_before_synergy_instantiation():
    """Missing required params should error before any wrapper construction touches Synergy."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_needs_two", None)

    def cli_needs_two(self, import_options: "ImportOptions | None", name: str) -> str:
        return f"{import_options}:{name}"

    setattr(moldflow.Synergy, "cli_needs_two", cli_needs_two)

    try:
        payload = '{"import_options":{"use_mdl":true}}'
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_needs_two", "--params-json", payload])

        assert r.exit_code != 0
        out = (getattr(r, "stdout", "") or getattr(r, "output", "")) + (
            getattr(r, "stderr", "") or ""
        )
        assert "missing required parameter" in out.lower()
        mock_ctx_synergy.assert_not_called()
        # Wrapper construction may still touch factories in edge introspection paths;
        # what must never happen here is creating the live Synergy context.
        assert mock_fact_synergy.call_count <= 1
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_needs_two")
        else:
            setattr(moldflow.Synergy, "cli_needs_two", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_file_input(tmp_path):
    """Provide parameters via --params-json-file and ensure they are routed."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_params", None)

    def cli_params(self, name: str, path: str) -> str:
        return f"name={name};path={path}"

    setattr(moldflow.Synergy, "cli_params", cli_params)

    class Sy:
        def cli_params(self, name: str, path: str) -> str:
            return f"name={name};path={path}"

    try:
        p = tmp_path / "params.json"
        p.write_text('{"name":"filetest","path":"C:\\\\Tmp\\\\P"}', encoding="utf-8")
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_params", "--params-json-file", str(p)])

        assert r.exit_code == 0
        assert "name=filetest" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_params")
        else:
            setattr(moldflow.Synergy, "cli_params", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_conflicting_json_inputs_error():
    """Specifying both --json-input and --json-file-input should error."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        r = runner.invoke(
            app,
            [
                "invoke",
                "synergy.open_project",
                "--params-json",
                '{"name":"a"}',
                "--params-json-file",
                "params.json",
            ],
        )
    assert r.exit_code != 0
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_list_and_dict_values():
    """JSON input should preserve list/dict types rather than stringifying them."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_complex", None)

    def cli_complex(  # type: ignore[name-defined]
        self, ids: list[int], meta: dict[str, str]
    ) -> str:
        return f"ids={ids};meta={meta}"

    setattr(moldflow.Synergy, "cli_complex", cli_complex)

    class Sy:
        def cli_complex(self, ids: list[int], meta: dict[str, str]) -> str:
            return f"ids={ids};meta={meta}"

    try:
        payload = '{"ids":[1,2,3],"meta":{"a":"x","b":"y"}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_complex", "--params-json", payload])

        assert r.exit_code == 0
        assert "ids=[1, 2, 3]" in r.stdout
        assert "meta={'a': 'x', 'b': 'y'}" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_complex")
        else:
            setattr(moldflow.Synergy, "cli_complex", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_typed_object():
    """JSON input should construct typed wrapper objects using __type__."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_typed", None)

    class FakeImportOptions:
        def __init__(self) -> None:
            self.use_mdl = None

    def cli_typed(  # type: ignore[name-defined]
        self, import_options: "ImportOptions | None"
    ) -> str:
        return f"use_mdl={import_options.use_mdl}"

    setattr(moldflow.Synergy, "cli_typed", cli_typed)

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def cli_typed(self, import_options: FakeImportOptions) -> str:
            return f"use_mdl={import_options.use_mdl}"

    try:
        payload = '{"import_options":{"__type__":"ImportOptions","use_mdl":true}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_typed", "--params-json", payload])

        assert r.exit_code == 0
        assert "use_mdl=True" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_typed")
        else:
            setattr(moldflow.Synergy, "cli_typed", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_coerce_final_value_json_nested_leaf_dict_uses_type_tag_for_wrappers():
    """Nested JSON leaves go through convert_value without a signature type.

    For a nested path, ``_coerce_final_value(..., origin='json')`` must still build
    wrappers when the leaf dict includes ``__type__``. A wrapper-shaped dict without
    ``__type__`` stays a plain dict (avoid assigning that shape expecting auto-wrap).
    """

    class FakeImportOptions:
        def __init__(self) -> None:
            self.use_mdl = None

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        wrapped = _coerce_final_value(
            "container", "opts", {"__type__": "ImportOptions", "use_mdl": True}, "json"
        )
        assert isinstance(wrapped, FakeImportOptions)
        assert wrapped.use_mdl is True

        plain = _coerce_final_value("container", "opts", {"use_mdl": True}, "json")
        assert plain == {"use_mdl": True}
        assert not isinstance(plain, FakeImportOptions)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_non_public_field_in_typed_json_object():
    """Typed JSON payloads must reject non-public wrapper fields."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_typed", None)

    class FakeImportOptions:
        pass

    def cli_typed(  # type: ignore[name-defined]
        self, import_options: "ImportOptions | None"
    ) -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_typed", cli_typed)

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def cli_typed(self, import_options: FakeImportOptions) -> str:
            return "ok"

    try:
        payload = '{"import_options":{"__type__":"ImportOptions","_private":1}}'
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_typed", "--params-json", payload])

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "non-public" in combined.lower()
        assert "_private" in combined
        mock_ctx_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_typed")
        else:
            setattr(moldflow.Synergy, "cli_typed", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_invalid_single_positional_json_shorthand_has_actionable_error():
    """Malformed single-positional JSON shorthand should mention the shorthand rule."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["--no-color", "invoke", "synergy.cli_echo", '{"value":'])

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        lower = combined.lower()
        assert "invalid json payload for parameters" in lower
        assert "treated as json shorthand" in lower
        assert "--params-json" in combined
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_does_not_silently_fallback_to_dict_when_typed_wrapper_assignment_fails():
    """Wrapper assignment failures should surface as validation errors, not dict fallback."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_typed_strict", None)

    class FakeImportOptions:
        __slots__ = ("use_mdl",)

        def __init__(self) -> None:
            self.use_mdl = False

    def cli_typed_strict(  # type: ignore[name-defined]
        self, import_options: "ImportOptions | None"
    ) -> str:
        return type(import_options).__name__

    setattr(moldflow.Synergy, "cli_typed_strict", cli_typed_strict)

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def cli_typed_strict(self, import_options: FakeImportOptions) -> str:
            return type(import_options).__name__

    try:
        payload = '{"import_options":{"unknown_field":1}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_typed_strict", "--params-json", payload])

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "invalid json value for parameter" in combined.lower()
        assert "unknown_field" in combined
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_typed_strict")
        else:
            setattr(moldflow.Synergy, "cli_typed_strict", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_entlist_selection_string():
    """Typed EntList JSON should accept a string selection field via the CLI adapter."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        def __init__(self) -> None:
            self.selected = None

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            self.selected = entity_string

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return getattr(nodes, "selected", "missing")

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return getattr(nodes, "selected", "missing")

    try:
        payload = '{"nodes":{"__type__":"EntList","entity_string":"N1,N2"}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_select_nodes", "--params-json", payload])

        assert r.exit_code == 0
        assert "N1,N2" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_non_string_entlist_selection_json():
    """Selection-like EntList JSON fields should reject non-string values clearly."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            raise AssertionError("select_from_string should not be called")

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return "ok"

    try:
        payload = '{"nodes":{"__type__":"EntList","entity_string":5}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_select_nodes", "--params-json", payload])

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "string selection expression" in combined.lower()
        assert "entity_string" in combined
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_unknown_entlist_json_field_with_guidance():
    """Selection-like JSON should point users to the canonical field when they guess wrong."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            pass

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return "ok"

    try:
        payload = '{"nodes":{"value":"N1,N2"}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_select_nodes", "--params-json", payload])

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "entity_string" in combined
        assert "template" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_non_json_entlist_selection_shorthand():
    """Non-JSON mode should support direct selection-string shorthand for EntList params."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        def __init__(self) -> None:
            self.selected = None

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            self.selected = entity_string

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return getattr(nodes, "selected", "missing")

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return getattr(nodes, "selected", "missing")

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_select_nodes", "nodes=N1,N2"])

        assert r.exit_code == 0
        assert "N1,N2" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_non_json_entlist_selection_explicit_field():
    """Non-JSON dotted canonical field syntax should route through the wrapper adapter."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        def __init__(self) -> None:
            self.selected = None

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            self.selected = entity_string

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return getattr(nodes, "selected", "missing")

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return getattr(nodes, "selected", "missing")

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_select_nodes", "nodes.entity_string=N1,N2"]
            )

        assert r.exit_code == 0
        assert "N1,N2" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_conflicting_non_json_entlist_selection_inputs():
    """Direct shorthand and explicit field syntax should be rejected as conflicting paths."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_select_nodes", None)

    class FakeEntList:
        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            pass

    def cli_select_nodes(self, nodes: "EntList | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_select_nodes", cli_select_nodes)

    class SelectionProvider:
        def create_entity_list(self) -> FakeEntList:
            return FakeEntList()

    class Sy:
        @property
        def property_editor(self) -> SelectionProvider:
            return SelectionProvider()

        def cli_select_nodes(self, nodes: FakeEntList) -> str:
            return "ok"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_select_nodes", "nodes=N1", "nodes.entity_string=N2"]
            )

        assert r.exit_code != 0
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "conflicting argument paths" in combined.lower()
        assert "cli_select_nodes.nodes" in combined.lower()
        assert "entity_string" in combined.lower()
        assert "nodes" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_select_nodes")
        else:
            setattr(moldflow.Synergy, "cli_select_nodes", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_vector_xyz_triplet():
    """Typed Vector JSON should accept the canonical xyz triplet field."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_direction", None)

    class FakeVector:
        def __init__(self) -> None:
            self.xyz = None

        @cli_input_adapter(
            value_kind="vector_triplet", preferred_field="xyz", shorthand_supported=True
        )
        def set_xyz(self, x: float, y: float, z: float) -> None:
            self.xyz = (x, y, z)

    def cli_accept_direction(self, direction: "Vector | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_direction", cli_accept_direction)

    class Sy:
        def create_vector(self) -> FakeVector:
            return FakeVector()

        def cli_accept_direction(self, direction: FakeVector) -> str:
            return str(direction.xyz)

    try:
        payload = '{"direction":{"__type__":"Vector","xyz":[0,0,1]}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_accept_direction", "--params-json", payload]
            )

        assert r.exit_code == 0
        assert "(0.0, 0.0, 1.0)" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_direction")
        else:
            setattr(moldflow.Synergy, "cli_accept_direction", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_non_json_vector_shorthand():
    """Non-JSON mode should support direct triplet shorthand for Vector params."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_direction", None)

    class FakeVector:
        def __init__(self) -> None:
            self.xyz = None

        @cli_input_adapter(
            value_kind="vector_triplet", preferred_field="xyz", shorthand_supported=True
        )
        def set_xyz(self, x: float, y: float, z: float) -> None:
            self.xyz = (x, y, z)

    def cli_accept_direction(self, direction: "Vector | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_direction", cli_accept_direction)

    class Sy:
        def create_vector(self) -> FakeVector:
            return FakeVector()

        def cli_accept_direction(self, direction: FakeVector) -> str:
            return str(direction.xyz)

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_accept_direction", "direction=0,0,1"])

        assert r.exit_code == 0
        assert "(0.0, 0.0, 1.0)" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_direction")
        else:
            setattr(moldflow.Synergy, "cli_accept_direction", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_double_array_values():
    """Typed list-backed wrappers should accept the canonical values field in JSON mode."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels", None)

    class FakeDoubleArray:
        def __init__(self) -> None:
            self.values = None

        @cli_input_adapter(value_kind="list_values", shorthand_supported=True)
        def from_list(self, values: list[float]) -> None:
            self.values = list(values)

    def cli_accept_levels(self, levels: "DoubleArray | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels", cli_accept_levels)

    class Sy:
        def create_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

        def cli_accept_levels(self, levels: FakeDoubleArray) -> str:
            return str(levels.values)

    try:
        payload = '{"levels":{"__type__":"DoubleArray","values":[1.0,2.5]}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_accept_levels", "--params-json", payload]
            )

        assert r.exit_code == 0
        assert "[1.0, 2.5]" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_double_array_values_without_type_tag():
    """JSON mode should infer DoubleArray when type tags are omitted."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels", None)

    class FakeDoubleArray:
        def __init__(self) -> None:
            self.values = None

        @cli_input_adapter(value_kind="list_values", shorthand_supported=True)
        def from_list(self, values: list[float]) -> None:
            self.values = list(values)

    def cli_accept_levels(self, levels: "DoubleArray | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels", cli_accept_levels)

    class Sy:
        def create_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

        def cli_accept_levels(self, levels: FakeDoubleArray) -> str:
            return str(levels.values)

    try:
        payload = '{"levels":{"values":[1.0,2.5]}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_accept_levels", "--params-json", payload]
            )

        assert r.exit_code == 0
        assert "[1.0, 2.5]" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_json_double_array_values_accepts_plain_type_alias():
    """JSON mode should tolerate a plain matching type field in known context."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels", None)

    class FakeDoubleArray:
        def __init__(self) -> None:
            self.values = None

        @cli_input_adapter(value_kind="list_values", shorthand_supported=True)
        def from_list(self, values: list[float]) -> None:
            self.values = list(values)

    def cli_accept_levels(self, levels: "DoubleArray | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels", cli_accept_levels)

    class Sy:
        def create_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

        def cli_accept_levels(self, levels: FakeDoubleArray) -> str:
            return str(levels.values)

    try:
        payload = '{"levels":{"type":"DoubleArray","values":[1.0,2.5]}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_accept_levels", "--params-json", payload]
            )

        assert r.exit_code == 0
        assert "[1.0, 2.5]" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_non_json_double_array_shorthand():
    """Non-JSON mode should support direct shorthand for list-backed wrappers."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels", None)

    class FakeDoubleArray:
        def __init__(self) -> None:
            self.values = None

        @cli_input_adapter(value_kind="list_values", shorthand_supported=True)
        def from_list(self, values: list[float]) -> None:
            self.values = list(values)

    def cli_accept_levels(self, levels: "DoubleArray | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels", cli_accept_levels)

    class Sy:
        def create_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

        def cli_accept_levels(self, levels: FakeDoubleArray) -> str:
            return str(levels.values)

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_accept_levels", "levels=1.0,2.5"])

        assert r.exit_code == 0
        assert "[1.0, 2.5]" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_non_json_vector_array_shorthand():
    """Non-JSON mode should support direct shorthand for vector-array wrappers."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_points", None)

    class FakeVectorArray:
        def __init__(self) -> None:
            self.points: list[tuple[float, float, float]] = []

        def clear(self) -> None:
            self.points = []

        @cli_input_adapter(
            value_kind="vector_array_values", preferred_field="xyz", shorthand_supported=True
        )
        def add_xyz(self, x: float, y: float, z: float) -> None:
            self.points.append((x, y, z))

    def cli_accept_points(self, points: "VectorArray | None") -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_points", cli_accept_points)

    class Sy:
        def create_vector_array(self) -> FakeVectorArray:
            return FakeVectorArray()

        def cli_accept_points(self, points: FakeVectorArray) -> str:
            return str(points.points)

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_accept_points", "points=0,0,0;1,0,0"])

        assert r.exit_code == 0
        assert "(0.0, 0.0, 0.0)" in r.stdout
        assert "(1.0, 0.0, 0.0)" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_points")
        else:
            setattr(moldflow.Synergy, "cli_accept_points", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_wraps_fallback_convert_value_errors_as_badparameter():
    """Fallback conversion errors should be surfaced as CLI validation failures."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_dict", None)

    def cli_accept_dict(self, meta: dict) -> str:  # type: ignore[name-defined]
        return str(meta)

    setattr(moldflow.Synergy, "cli_accept_dict", cli_accept_dict)

    class Sy:
        def cli_accept_dict(self, meta: dict) -> str:
            return str(meta)

    try:
        payload = '{"meta":{"inner":{"__type__":"NoSuchType","x":1}}}'
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_accept_dict", "--params-json", payload])

        assert r.exit_code == 2
        combined = (
            (getattr(r, "stdout", "") or getattr(r, "output", ""))
            + (getattr(r, "stderr", "") or "")
            + (f"\n{r.exception}" if getattr(r, "exception", None) else "")
        )
        assert "invalid json value for parameter 'meta'" in combined.lower()
        assert "nosuchtype" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_dict")
        else:
            setattr(moldflow.Synergy, "cli_accept_dict", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_accepts_bare_target_alias_and_normalizes_human_output():
    """Bare invoke targets should resolve through Synergy but render canonically."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", cli_echo)

    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "cli_echo", "value=ok", "--dry-run"])

        assert r.exit_code == 0
        out = (r.stdout or "") + (getattr(r, "stderr", "") or "")
        assert "Dry run for synergy.cli_echo" in out
        assert "invoke synergy.cli_echo value=<value>" in out
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_class_like_segment_not_exposed_on_parent_preinstantiation():
    """Class-like path segments must exist on the parent object before invocation."""
    app = build_cli_app()

    class CliGhost:
        def ping(self) -> str:
            return "pong"

    orig_cls = getattr(moldflow, "CliGhost", None)
    setattr(moldflow, "CliGhost", CliGhost)
    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_ghost.ping"])

        assert r.exit_code != 0
        out = (r.stdout or "") + (getattr(r, "stderr", "") or "")
        assert "does not resolve as an attribute" in out.lower()
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig_cls is None:
            delattr(moldflow, "CliGhost")
        else:
            setattr(moldflow, "CliGhost", orig_cls)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nested_kwargs_key_is_rejected_early():
    """Nested key syntax is invalid for **kwargs parameters and should fail pre-instantiation."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_kwargs_only", None)

    def cli_kwargs_only(self, **kwargs) -> str:
        return str(kwargs)

    setattr(moldflow.Synergy, "cli_kwargs_only", cli_kwargs_only)
    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            r = runner.invoke(app, ["invoke", "synergy.cli_kwargs_only", "alpha.beta=1"])

        assert r.exit_code != 0
        out = (r.stdout or "") + (getattr(r, "stderr", "") or "")
        assert "nested argument" in out.lower() or "not supported" in out.lower()
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_kwargs_only")
        else:
            setattr(moldflow.Synergy, "cli_kwargs_only", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_non_public_target_segments_preinstantiation():
    """Invoke should reject private/dunder segments before touching Synergy."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(app, ["invoke", "synergy.__class__"])

    assert result.exit_code != 0
    assert (
        "non-public segment"
        in ((result.stdout or "") + (getattr(result, "stderr", "") or "")).lower()
    )
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_empty_target_segment_preinstantiation():
    """Invoke should reject malformed dotted targets before touching Synergy."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(app, ["invoke", "synergy..open_project"])

    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "empty path segment" in combined.lower()
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_empty_argument_path_segment_preinstantiation():
    """Invoke should reject malformed argument paths before touching Synergy."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result = runner.invoke(app, ["invoke", "synergy.open_project", "name..x=value"])

    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "empty path segment" in combined.lower()
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_positional_only_params_fail_with_actionable_error():
    """Positional-only signatures should fail early with clear guidance."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_pos_only", None)

    def _cli_pos_only(self, value, /):
        return value

    setattr(moldflow.Synergy, "cli_pos_only", _cli_pos_only)

    class Sy:
        def cli_pos_only(self, value, /):
            return value

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_pos_only", "value=5"])
        assert result.exit_code != 0
        stderr_text = (getattr(result, "stderr_bytes", b"") or b"").decode("utf-8", "ignore")
        combined = f"{result.stdout or ''}\n{stderr_text}\n{result.exception or ''}"
        assert "positional-only parameters" in combined.lower()
        assert "not supported" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_pos_only")
        else:
            setattr(moldflow.Synergy, "cli_pos_only", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_conflicting_argument_paths():
    """A direct assignment and nested assignment for same param should be rejected."""
    app = build_cli_app()

    class Wrapper:
        def __init__(self) -> None:
            self.x = 0

    class Sy:
        def create_vector(self):
            return Wrapper()

        def do(self, obj) -> str:
            return "ok"

    orig = getattr(moldflow.Synergy, "do", None)

    def _do(self, obj: "Vector"):
        return "ok"

    setattr(moldflow.Synergy, "do", _do)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.do", "do.obj=1", "do.obj.x=2"])
        assert result.exit_code != 0
        stderr_text = (getattr(result, "stderr_bytes", b"") or b"").decode("utf-8", "ignore")
        combined = f"{result.stdout or ''}\n{stderr_text}\n{result.exception or ''}"
        assert "conflicting argument paths" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do")
        else:
            setattr(moldflow.Synergy, "do", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_none_forward_ref_object_pass_through():
    """Passing 'null' for an optional scalar param yields None and is accepted."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_optional", None)

    def cli_accept_optional(self, opt=None):
        return f"opt={opt!r}"

    setattr(moldflow.Synergy, "cli_accept_optional", cli_accept_optional)

    class Sy:
        def cli_accept_optional(self, opt=None):
            return f"opt={opt!r}"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_accept_optional", "opt=null"])
        assert result.exit_code == 0
        assert "opt=None" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_optional")
        else:
            setattr(moldflow.Synergy, "cli_accept_optional", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nested_attribute_invalid_path():
    """Setting a nested attribute path that doesn't exist should error without side-effects."""
    app = build_cli_app()

    class Wrapper:
        def __init__(self) -> None:
            self.exists = 1

    class Fake:
        def do(self, obj: Wrapper) -> str:
            return "ok"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "do", None)

    def _do(self, obj):
        return "ok"

    setattr(moldflow.Synergy, "do", _do)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            res = runner.invoke(app, ["invoke", "synergy.do", "do.obj.nonexist=5"])

        # Expect a non-zero exit; exact error text varies by Click/Typer versions.
        assert res.exit_code != 0
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do")
        else:
            setattr(moldflow.Synergy, "do", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_readonly_attribute_assignment():
    """Attempting to set a read-only property should produce a helpful error."""
    app = build_cli_app()

    class Wrapper:
        @property
        def ro(self):
            return 5

    class Fake:
        def do(self, obj: Wrapper) -> str:
            return "ok"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "do", None)

    def _do(self, obj):
        return "ok"

    setattr(moldflow.Synergy, "do", _do)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            res = runner.invoke(app, ["invoke", "synergy.do", "do.obj.ro=10"])

        # Expect a non-zero exit; exact error text varies by Click/Typer versions.
        assert res.exit_code != 0
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do")
        else:
            setattr(moldflow.Synergy, "do", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_factory_failure_propagation():
    """If a Synergy factory raises while creating a wrapper, the CLI surfaces the error."""
    app = build_cli_app()

    class Sy:
        @property
        def import_options(self):
            raise RuntimeError("factory failed")

        def import_file(self, file, import_options=None):
            return "ok"

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()), patch(
        "moldflow_cli.context.get_synergy", return_value=Sy()
    ):
        # Force wrapper/factory access by assigning nested attribute on import_options.
        res = runner.invoke(
            app, ["invoke", "synergy.import_file", "file=x", "import_file.import_options.foo=1"]
        )

        # Expect a non-zero exit; the exact message may vary across Click/Typer versions.
        assert res.exit_code != 0


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_unicode_and_path_escaping():
    """Ensure unicode and Windows paths round-trip through parsing."""
    app = build_cli_app()

    class Fake:
        def open_path(self, path: str, name: str) -> str:
            return f"path={path};name={name}"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "open_path", None)

    def _open_path(self, path: str, name: str) -> str:
        return f"path={path};name={name}"

    setattr(moldflow.Synergy, "open_path", _open_path)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            val = r"C:\path\to\file with spaces.txt"
            r = runner.invoke(app, ["invoke", "synergy.open_path", f'path={val}', "name=ünïçødé"])
        assert r.exit_code == 0
        assert "C:\\path\\to\\file" in r.stdout or "ünïçødé" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "open_path")
        else:
            setattr(moldflow.Synergy, "open_path", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_error_exit_codes():
    """Assert non-zero exit codes and helpful messages for common failure modes."""
    app = build_cli_app()

    # missing param / unknown param / parse error should not instantiate real Synergy.
    class Sy:
        def open_project(self, path: int):
            # Enforce type at runtime so CLI surfaces a parse/type error.
            if not isinstance(path, int):
                raise TypeError("path must be int")
            return f"opened:{path}"

    sy = Sy()
    with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
        "moldflow_cli.factories.get_synergy", return_value=sy
    ):
        # missing param
        r1 = runner.invoke(app, ["invoke", "synergy.open_project"])
        # unknown param
        r2 = runner.invoke(app, ["invoke", "synergy.open_project", "bad=1"])
        # parse error (pass non-numeric to int)
        r3 = runner.invoke(app, ["invoke", "synergy.open_project", "path=not-an-int"])

    assert r1.exit_code != 0
    assert r2.exit_code != 0
    assert r3.exit_code != 0
    out1 = (getattr(r1, "stdout", "") or getattr(r1, "output", "")) + (
        getattr(r1, "stderr", "") or ""
    )
    assert "missing required parameter" in out1.lower()
    assert "missing required parameter 'path'" in out1.lower()
    assert "open_project.path" not in out1
    assert "(self," not in out1


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_help_shows_arg_syntax():
    """Invoke --help should demonstrate the step.param.attr=value routing syntax."""
    app = build_cli_app()
    result = runner.invoke(app, ["--no-color", "invoke", "--help"])
    help_text = strip_ansi(result.stdout).lower()
    assert result.exit_code == 0
    assert "find_plot_by_name.plot_name" in help_text or "step.param.attr" in help_text
    assert "duplicate/conflicting paths" in help_text
    assert "rejected" in help_text
    assert "positional-only" in help_text
    assert "arrays/scalars" in help_text
    assert "template summary" in help_text
    assert "structured" in help_text and "stdout" in help_text
    assert all(token in help_text for token in ("without", "changing", "stdout", "mode"))
    assert all(token in help_text for token in ("line-delimited", "json", "trace", "stderr"))
    assert "--json" in help_text
    assert "--json-output" in help_text
    assert "legacy alias" in help_text
    assert "canonical" in help_text


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_mixed_case_target_renders_canonical_target_in_dry_run_output():
    """Dry-run output should show canonical target casing even when input target is mixed-case."""
    app = build_cli_app()
    result = runner.invoke(app, ["invoke", "OPEN_PROJECT", "--dry-run", "path=C:/Temp/demo.mfproj"])
    assert result.exit_code == 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "Dry run for synergy.open_project" in combined
    assert "invoke synergy.open_project path=<path>" in combined


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_large_number_of_args_performance_hint():
    """Sanity check: invoking with many parameters parses and executes."""
    app = build_cli_app()

    # Create a function that accepts **kwargs but exposes a large signature.
    param_count = 120

    def cli_many_args(self, **kwargs):
        return f"count={len(kwargs)}"

    sig_params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
    sig_params.extend(
        [
            inspect.Parameter(f"p{i}", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=None)
            for i in range(param_count)
        ]
    )
    cli_many_args.__signature__ = inspect.Signature(sig_params)

    orig = getattr(moldflow.Synergy, "cli_many_args", None)
    setattr(moldflow.Synergy, "cli_many_args", cli_many_args)

    class Sy:
        def cli_many_args(self, **kwargs):
            return f"count={len(kwargs)}"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            # Build argument list for half of the params to keep command length reasonable.
            args = ["invoke", "synergy.cli_many_args"] + [
                f"p{i}=1" for i in range(param_count // 2)
            ]
            result = runner.invoke(app, args)
        assert result.exit_code == 0
        assert "count=" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_many_args")
        else:
            setattr(moldflow.Synergy, "cli_many_args", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_bool_and_none_parsing_variants():
    """_parse_scalar should accept YES/NO/null and numeric parsing for invoke args."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_bool_and_none", None)

    def cli_bool_and_none(self, flag: bool, opt: int | None) -> str:  # type: ignore[name-defined]
        return f"flag={flag};opt={opt}"

    setattr(moldflow.Synergy, "cli_bool_and_none", cli_bool_and_none)

    class SynergyForTest:
        def cli_bool_and_none(self, flag: bool, opt: int | None) -> str:
            return f"flag={flag};opt={opt}"

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_bool_and_none", "flag=YES", "opt=null"]
            )

        assert result.exit_code == 0
        assert "flag=True" in result.stdout
        assert "opt=None" in result.stdout or "opt=null" in result.stdout.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_bool_and_none")
        else:
            setattr(moldflow.Synergy, "cli_bool_and_none", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nested_attribute_error_is_reported_as_badparameter():
    """Missing nested attributes should produce a clean CLI validation error."""
    app = build_cli_app()

    class Fake:
        def create_vector(self):
            class Vec:
                x = 0
                y = 0
                z = 0

            return Vec()

        def do(self, obj) -> str:
            return "ok"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "do", None)

    def _do(self, obj: "Vector"):
        return "ok"

    setattr(moldflow.Synergy, "do", _do)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(app, ["invoke", "synergy.do", "do.obj.nonexist.leaf=5"])
        assert result.exit_code != 0
        stderr_text = (getattr(result, "stderr_bytes", b"") or b"").decode("utf-8", "ignore")
        combined = f"{stderr_text}\n{result.exception}"
        assert "invalid nested argument path" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do")
        else:
            setattr(moldflow.Synergy, "do", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nested_leaf_attribute_must_exist():
    """Leaf typo in nested paths should fail instead of creating dynamic attributes."""
    app = build_cli_app()

    class Wrapper:
        def __init__(self) -> None:
            self.x = 0
            self.y = 0
            self.z = 0

    class Fake:
        def create_vector(self):
            return Wrapper()

        def do(self, obj) -> str:
            return "ok"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "do", None)

    def _do(self, obj: "Vector"):
        return "ok"

    setattr(moldflow.Synergy, "do", _do)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(app, ["invoke", "synergy.do", "do.obj.typo_leaf=5"])
        assert result.exit_code != 0
        stderr_text = (getattr(result, "stderr_bytes", b"") or b"").decode("utf-8", "ignore")
        combined = f"{stderr_text}\n{result.exception}"
        assert "invalid nested argument path" in combined.lower()
        assert "typo_leaf" in combined
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do")
        else:
            setattr(moldflow.Synergy, "do", orig)
