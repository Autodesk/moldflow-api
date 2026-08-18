# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused invoke output serialization tests for moldflow CLI."""

# Test modules intentionally use many tiny inline doubles to mirror CLI call patterns.
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument,redefined-outer-name

from __future__ import annotations

from unittest.mock import patch
import json

import pytest
from rich import box
from typer.testing import CliRunner
import moldflow

from moldflow_cli.commands import build_cli_app
from moldflow_cli.output_utils import human_table_kwargs

runner = CliRunner()
_UNICODE_BOX_CHARS = ("╭", "╮", "╰", "╯", "│", "─", "┌", "┐", "└", "┘")


@pytest.mark.cli
@pytest.mark.unit
def test_captured_help_uses_ascii_panels():
    """Captured help output should avoid Unicode panel borders."""
    app = build_cli_app()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert not any(char in result.stdout for char in _UNICODE_BOX_CHARS)


@pytest.mark.cli
@pytest.mark.unit
def test_captured_error_uses_ascii_panels():
    """Captured error output should avoid Unicode panel borders."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "boundary_conditions.create_entity_list"])
    assert result.exit_code != 0
    text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert not any(char in text for char in _UNICODE_BOX_CHARS)


@pytest.mark.cli
@pytest.mark.unit
def test_human_table_kwargs_use_ascii_when_output_is_captured():
    """Captured human table output should use ASCII borders for portability."""

    class CapturedConsole:
        is_terminal = False
        is_dumb_terminal = False

    kwargs = human_table_kwargs(CapturedConsole())
    assert kwargs == {"box": box.ASCII, "safe_box": True}


def _unwrap_invoke_envelope(stdout_text: str):
    payload = json.loads(stdout_text)
    assert "ok" in payload and "result" in payload and "result_type" in payload
    return payload["result"]


class FakeEntList:
    """Fake EntList-like wrapper exposing convert_to_string and size."""

    def __init__(self) -> None:
        self._vals = ["node1", "node2", "node3"]

    @property
    def size(self) -> int:
        return len(self._vals)

    def convert_to_string(self) -> str:
        return ",".join(self._vals)


class FakeDoubleArray:
    """Fake DoubleArray-like wrapper exposing to_list and size."""

    def __init__(self) -> None:
        self._vals = [1.0, 2.5, 3.75]

    @property
    def size(self) -> int:
        return len(self._vals)

    def to_list(self) -> list[float]:
        return list(self._vals)


class FakeVectorArray:
    """Fake VectorArray-like wrapper exposing x/y/z and size."""

    def __init__(self) -> None:
        self._vals = [(0.0, 0.0, 0.0), (1.0, 2.0, 3.0)]

    @property
    def size(self) -> int:
        return len(self._vals)

    def x(self, index: int) -> float:
        return self._vals[index][0]

    def y(self, index: int) -> float:
        return self._vals[index][1]

    def z(self, index: int) -> float:
        return self._vals[index][2]


class FakeProperty:
    """Fake Property-like wrapper exposing id/name/type."""

    def __init__(self) -> None:
        self.id = 42
        self.name = "TestProperty"
        self.type = 7


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_entlist_human_and_json():
    """Ensure EntList-like wrappers render nicely in text and JSON modes."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_entlist", None)

    def cli_return_entlist(self) -> FakeEntList:  # type: ignore[unused-argument]
        return FakeEntList()

    setattr(moldflow.Synergy, "cli_return_entlist", cli_return_entlist)

    class SynergyForTest:
        def cli_return_entlist(self) -> FakeEntList:
            return FakeEntList()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            # Human-readable mode
            result_txt = runner.invoke(app, ["invoke", "synergy.cli_return_entlist"])
            # JSON mode
            result_json = runner.invoke(
                app, ["invoke", "synergy.cli_return_entlist", "--json-output"]
            )

        assert result_txt.exit_code == 0
        assert result_json.exit_code == 0
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
        assert "node1,node2,node3" in result_txt.stdout

        payload = json.loads(result_json.stdout)
        data = payload["result"]
        assert payload["ok"] is True
        assert data["type"] == "FakeEntList"
        assert data["size"] == 3
        assert data["string"] == "node1,node2,node3"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_entlist")
        else:
            setattr(moldflow.Synergy, "cli_return_entlist", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_double_array_human_output_is_labeled():
    """Array-like human output should include a label instead of a bare JSON fragment."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_double_array", None)

    def cli_return_double_array(self) -> FakeDoubleArray:  # type: ignore[unused-argument]
        return FakeDoubleArray()

    setattr(moldflow.Synergy, "cli_return_double_array", cli_return_double_array)

    class SynergyForTest:
        def cli_return_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_return_double_array"])

        assert result.exit_code == 0
        assert "FakeDoubleArray values (3 items):" in result.stdout
        assert "1. 1.0" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_double_array")
        else:
            setattr(moldflow.Synergy, "cli_return_double_array", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_double_array_json():
    """Ensure DoubleArray-like wrappers render as value lists in JSON mode."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_double_array", None)

    def cli_return_double_array(self) -> FakeDoubleArray:  # type: ignore[unused-argument]
        return FakeDoubleArray()

    setattr(moldflow.Synergy, "cli_return_double_array", cli_return_double_array)

    class SynergyForTest:
        def cli_return_double_array(self) -> FakeDoubleArray:
            return FakeDoubleArray()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            result = runner.invoke(
                app, ["invoke", "synergy.cli_return_double_array", "--json-output"]
            )

        assert result.exit_code == 0
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
        data = _unwrap_invoke_envelope(result.stdout)
        assert data["type"] == "FakeDoubleArray"
        assert data["size"] == 3
        assert data["values"] == [1.0, 2.5, 3.75]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_double_array")
        else:
            setattr(moldflow.Synergy, "cli_return_double_array", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_vector_array_json():
    """Ensure VectorArray-like wrappers render as coordinate lists in JSON mode."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_vector_array", None)

    def cli_return_vector_array(self) -> FakeVectorArray:  # type: ignore[unused-argument]
        return FakeVectorArray()

    setattr(moldflow.Synergy, "cli_return_vector_array", cli_return_vector_array)

    class SynergyForTest:
        def cli_return_vector_array(self) -> FakeVectorArray:
            return FakeVectorArray()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            result = runner.invoke(
                app, ["invoke", "synergy.cli_return_vector_array", "--json-output"]
            )

        assert result.exit_code == 0
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
        data = _unwrap_invoke_envelope(result.stdout)
        assert data["type"] == "FakeVectorArray"
        assert data["size"] == 2
        assert data["values"] == [{"x": 0.0, "y": 0.0, "z": 0.0}, {"x": 1.0, "y": 2.0, "z": 3.0}]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_vector_array")
        else:
            setattr(moldflow.Synergy, "cli_return_vector_array", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_property_json():
    """Ensure Property-like wrappers render with id/name/type in JSON mode."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_property", None)

    def cli_return_property(self) -> FakeProperty:  # type: ignore[unused-argument]
        return FakeProperty()

    setattr(moldflow.Synergy, "cli_return_property", cli_return_property)

    class SynergyForTest:
        def cli_return_property(self) -> FakeProperty:
            return FakeProperty()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["invoke", "synergy.cli_return_property", "--json-output"])

        assert result.exit_code == 0
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
        data = _unwrap_invoke_envelope(result.stdout)
        assert data["type"] == "FakeProperty"
        assert data["id"] == 42
        assert data["name"] == "TestProperty"
        assert data["prop_type"] == 7
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_property")
        else:
            setattr(moldflow.Synergy, "cli_return_property", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_serialization_does_not_probe_arbitrary_properties():
    """Fallback serialization should use instance fields without touching property getters."""
    app = build_cli_app()

    class RiskyWrapper:
        property_calls = 0

        def __init__(self) -> None:
            self.safe_value = 123

        @property
        def expensive_property(self) -> int:
            type(self).property_calls += 1
            raise RuntimeError("property getter should not be called during serialization")

    orig = getattr(moldflow.Synergy, "cli_return_risky_wrapper", None)

    def cli_return_risky_wrapper(self) -> RiskyWrapper:  # type: ignore[unused-argument]
        return RiskyWrapper()

    setattr(moldflow.Synergy, "cli_return_risky_wrapper", cli_return_risky_wrapper)

    class SynergyForTest:
        def cli_return_risky_wrapper(self) -> RiskyWrapper:
            return RiskyWrapper()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_return_risky_wrapper", "--json-output"]
            )

        assert result.exit_code == 0
        data = _unwrap_invoke_envelope(result.stdout)
        assert data["type"] == "RiskyWrapper"
        assert data["attributes"]["safe_value"] == 123
        assert RiskyWrapper.property_calls == 0
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_risky_wrapper")
        else:
            setattr(moldflow.Synergy, "cli_return_risky_wrapper", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_human_output_labels_object_attributes():
    """Generic object human output should name the object before showing attributes."""
    app = build_cli_app()

    class RiskyWrapper:
        def __init__(self) -> None:
            self.safe_value = 123

    orig = getattr(moldflow.Synergy, "cli_return_risky_wrapper_human", None)

    def cli_return_risky_wrapper_human(self) -> RiskyWrapper:  # type: ignore[unused-argument]
        return RiskyWrapper()

    setattr(moldflow.Synergy, "cli_return_risky_wrapper_human", cli_return_risky_wrapper_human)

    class SynergyForTest:
        def cli_return_risky_wrapper_human(self) -> RiskyWrapper:
            return RiskyWrapper()

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_return_risky_wrapper_human"])

        assert result.exit_code == 0
        assert "RiskyWrapper attributes:" in result.stdout
        assert '"safe_value": 123' in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_risky_wrapper_human")
        else:
            setattr(moldflow.Synergy, "cli_return_risky_wrapper_human", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_synergy_json_scalar_bool():
    """Ensure JSON mode emits primitive booleans without extra quoting."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_bool", None)

    def cli_return_bool(self) -> bool:  # type: ignore[unused-argument]
        return True

    setattr(moldflow.Synergy, "cli_return_bool", cli_return_bool)

    class SynergyForTest:
        def cli_return_bool(self) -> bool:
            return True

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["invoke", "synergy.cli_return_bool", "--json-output"])

        assert result.exit_code == 0
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["result"] is True
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_bool")
        else:
            setattr(moldflow.Synergy, "cli_return_bool", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_return_complex_structure_roundtrip_json():
    """Return nested fake structures and ensure --json emits nested JSON shapes."""
    app = build_cli_app()

    class FakeEntList:
        def __init__(self):
            self._vals = ["a", "b"]

        @property
        def size(self):
            return len(self._vals)

        def convert_to_string(self):
            return ",".join(self._vals)

    class FakeVectorArray:
        def __init__(self):
            self._vals = [(1.0, 2.0, 3.0)]

        @property
        def size(self):
            return len(self._vals)

        def x(self, i):
            return self._vals[i][0]

        def y(self, i):
            return self._vals[i][1]

        def z(self, i):
            return self._vals[i][2]

    class Fake:
        def complex(self):
            return {"list": FakeEntList(), "vectors": FakeVectorArray()}

    sy = Fake()
    orig = getattr(moldflow.Synergy, "complex", None)

    def _complex(self):
        return {"list": FakeEntList(), "vectors": FakeVectorArray()}

    setattr(moldflow.Synergy, "complex", _complex)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            r = runner.invoke(app, ["invoke", "synergy.complex", "--json-output"])
        assert r.exit_code == 0
        payload = _unwrap_invoke_envelope(getattr(r, "stdout", "") or getattr(r, "output", ""))
        assert isinstance(payload, dict)
        assert payload["list"]["type"] == "FakeEntList"
        assert payload["list"]["string"] == "a,b"
        assert payload["vectors"]["type"] == "FakeVectorArray"
        assert payload["vectors"]["values"] == [{"x": 1.0, "y": 2.0, "z": 3.0}]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "complex")
        else:
            setattr(moldflow.Synergy, "complex", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_and_file_output(tmp_path):
    """--json-output prints JSON and --json-file-output writes JSON to a file."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_entlist", None)

    def cli_return_entlist(self) -> FakeEntList:  # type: ignore[unused-argument]
        return FakeEntList()

    setattr(moldflow.Synergy, "cli_return_entlist", cli_return_entlist)

    class Sy:
        def cli_return_entlist(self) -> FakeEntList:
            return FakeEntList()

    out_file = tmp_path / "out.json"
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.cli_return_entlist",
                    "--json-output",
                    "--json-file-output",
                    str(out_file),
                ],
            )

        assert r.exit_code == 0
        # stdout should contain JSON-like output
        assert "FakeEntList" in r.stdout or "node1" in r.stdout
        # file should exist and contain JSON-ish content
        assert out_file.exists()
        content = out_file.read_text(encoding="utf-8")
        assert "FakeEntList" in content or "node1" in content
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_entlist")
        else:
            setattr(moldflow.Synergy, "cli_return_entlist", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_file_output_preserves_human_stdout_by_default(tmp_path):
    """--json-file-output should write JSON to a file without forcing JSON stdout."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_entlist", None)

    def cli_return_entlist(self) -> FakeEntList:  # type: ignore[unused-argument]
        return FakeEntList()

    setattr(moldflow.Synergy, "cli_return_entlist", cli_return_entlist)

    class Sy:
        def cli_return_entlist(self) -> FakeEntList:
            return FakeEntList()

    out_file = tmp_path / "out.json"
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(
                app, ["invoke", "synergy.cli_return_entlist", "--json-file-output", str(out_file)]
            )

        assert r.exit_code == 0
        assert "node1,node2,node3" in r.stdout
        assert '"schema_version"' not in r.stdout
        assert "Wrote structured output to" in r.stdout
        assert out_file.exists()
        payload = json.loads(out_file.read_text(encoding="utf-8"))
        assert payload["result"]["type"] == "FakeEntList"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_entlist")
        else:
            setattr(moldflow.Synergy, "cli_return_entlist", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_preserves_markup_like_string_value():
    """Invoke --json should preserve bracketed text literally, not rich-parse it."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_markup_value", None)

    def cli_markup_value(self) -> str:
        return "[bold]keep-me[/bold]"

    setattr(moldflow.Synergy, "cli_markup_value", cli_markup_value)

    class Sy:
        def cli_markup_value(self) -> str:
            return "[bold]keep-me[/bold]"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_markup_value", "--json-output"])

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["result"] == "[bold]keep-me[/bold]"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_markup_value")
        else:
            setattr(moldflow.Synergy, "cli_markup_value", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_plain_output_preserves_markup_like_string_value():
    """Invoke plain output should print bracketed text literally (no rich markup parsing)."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_markup_value", None)

    def cli_markup_value(self) -> str:
        return "[bold]keep-me[/bold]"

    setattr(moldflow.Synergy, "cli_markup_value", cli_markup_value)

    class Sy:
        def cli_markup_value(self) -> str:
            return "[bold]keep-me[/bold]"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_markup_value"])

        assert result.exit_code == 0
        assert "[bold]keep-me[/bold]" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_markup_value")
        else:
            setattr(moldflow.Synergy, "cli_markup_value", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_reports_serialization_errors_with_cli_validation_exit():
    """Structured output serialization errors should surface as BadParameter (exit code 2)."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_markup_value", None)

    def cli_markup_value(self) -> str:
        return "ok"

    setattr(moldflow.Synergy, "cli_markup_value", cli_markup_value)

    class Sy:
        def cli_markup_value(self) -> str:
            return "ok"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ), patch("moldflow_cli.output_utils._json.dumps", side_effect=TypeError("json exploded")):
            result = runner.invoke(app, ["invoke", "synergy.cli_markup_value", "--json-output"])

        assert result.exit_code == 2
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "failed to render json output" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_markup_value")
        else:
            setattr(moldflow.Synergy, "cli_markup_value", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_unknown_wrapper_fallback_is_structured():
    """Unknown wrappers should serialize to structured JSON via public attributes."""
    app = build_cli_app()

    class UnknownWrapper:
        def __init__(self) -> None:
            self.alpha = 3
            self.beta = "ok"
            self._private = "secret"

        def helper(self):  # pragma: no cover - callables are intentionally skipped
            return 1

    orig = getattr(moldflow.Synergy, "cli_unknown_wrapper", None)

    def cli_unknown_wrapper(self):
        return UnknownWrapper()

    setattr(moldflow.Synergy, "cli_unknown_wrapper", cli_unknown_wrapper)

    class Sy:
        def cli_unknown_wrapper(self):
            return UnknownWrapper()

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_unknown_wrapper", "--json-output"])

        assert result.exit_code == 0
        payload = _unwrap_invoke_envelope(result.stdout)
        assert payload["type"] == "UnknownWrapper"
        assert payload["attributes"]["alpha"] == 3
        assert payload["attributes"]["beta"] == "ok"
        assert "_private" not in payload["attributes"]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_unknown_wrapper")
        else:
            setattr(moldflow.Synergy, "cli_unknown_wrapper", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_unknown_wrapper_circular_reference_is_safe():
    """Unknown wrappers with self/cyclic refs should not recurse indefinitely."""
    app = build_cli_app()

    class UnknownWrapperCycle:
        def __init__(self) -> None:
            self.name = "root"
            self.self_ref = self

    orig = getattr(moldflow.Synergy, "cli_unknown_wrapper_cycle", None)

    def cli_unknown_wrapper_cycle(self):
        return UnknownWrapperCycle()

    setattr(moldflow.Synergy, "cli_unknown_wrapper_cycle", cli_unknown_wrapper_cycle)

    class Sy:
        def cli_unknown_wrapper_cycle(self):
            return UnknownWrapperCycle()

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_unknown_wrapper_cycle", "--json-output"]
            )

        assert result.exit_code == 0
        payload = _unwrap_invoke_envelope(result.stdout)
        assert payload["type"] == "UnknownWrapperCycle"
        attrs = payload["attributes"]
        assert attrs["name"] == "root"
        assert attrs["self_ref"]["type"] == "UnknownWrapperCycle"
        assert attrs["self_ref"]["circular_ref"] is True
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_unknown_wrapper_cycle")
        else:
            setattr(moldflow.Synergy, "cli_unknown_wrapper_cycle", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_shared_references_are_not_marked_as_circular():
    """Repeated references in sibling fields should serialize fully, not as circular refs."""
    app = build_cli_app()

    class Child:
        def __init__(self) -> None:
            self.value = 99

    class UnknownWrapperShared:
        def __init__(self) -> None:
            shared = Child()
            self.left = shared
            self.right = shared

    orig = getattr(moldflow.Synergy, "cli_unknown_wrapper_shared", None)

    def cli_unknown_wrapper_shared(self):
        return UnknownWrapperShared()

    setattr(moldflow.Synergy, "cli_unknown_wrapper_shared", cli_unknown_wrapper_shared)

    class Sy:
        def cli_unknown_wrapper_shared(self):
            return UnknownWrapperShared()

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_unknown_wrapper_shared", "--json-output"]
            )

        assert result.exit_code == 0
        payload = _unwrap_invoke_envelope(result.stdout)
        assert payload["type"] == "UnknownWrapperShared"
        attrs = payload["attributes"]
        assert attrs["left"]["type"] == "Child"
        assert attrs["left"]["attributes"]["value"] == 99
        assert attrs["right"]["type"] == "Child"
        assert attrs["right"]["attributes"]["value"] == 99
        assert attrs["right"].get("circular_ref") is not True
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_unknown_wrapper_shared")
        else:
            setattr(moldflow.Synergy, "cli_unknown_wrapper_shared", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_json_output_set_values_are_stably_sorted():
    """Set serialization should be deterministic for automation-friendly JSON output."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_return_set", None)

    def cli_return_set(self):  # type: ignore[unused-argument]
        return {"b", "a", "c"}

    setattr(moldflow.Synergy, "cli_return_set", cli_return_set)

    class Sy:
        def cli_return_set(self):
            return {"b", "a", "c"}

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_return_set", "--json-output"])

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["result"] == ["a", "b", "c"]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_return_set")
        else:
            setattr(moldflow.Synergy, "cli_return_set", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_results_use_stable_schema_for_all_items(tmp_path):
    """Batch results should keep a consistent key set across success and validation failures."""
    app = build_cli_app()
    batch_file = tmp_path / "batch.json"
    batch_file.write_text(
        json.dumps(
            [
                {"target": "synergy.open_project", "args": ["path=C:/Temp/demo.mfproj"]},
                {"target": "synergy.open_project", "unknown_field": 1},
            ]
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        app, ["invoke", "--batch-file", str(batch_file), "--dry-run", "--json-output"]
    )
    assert result.exit_code != 0
    payload = json.loads(result.stdout)
    items = payload.get("batch_results", [])
    assert isinstance(items, list)
    assert len(items) == 2
    expected_keys = {
        "index",
        "target",
        "request",
        "ok",
        "result",
        "result_type",
        "plan",
        "diagnostics",
        "error_type",
        "error",
    }
    for item in items:
        assert isinstance(item, dict)
        assert set(item.keys()) == expected_keys
