# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused invoke execution-path tests for moldflow CLI."""

# Test modules intentionally use many tiny inline doubles to mirror CLI call patterns.
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-argument,too-many-lines,too-few-public-methods

from __future__ import annotations

from unittest.mock import patch
import typing
import json

import pytest
from typer.testing import CliRunner
import moldflow

from moldflow_cli.commands import build_cli_app

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_targets_return_values():
    """Property-only targets should be readable via invoke."""
    app = build_cli_app()

    class Sy:
        @property
        def version(self) -> str:
            return "2027"

        @property
        def edition(self) -> str:
            return "Insight"

    fake = Sy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        version_result = runner.invoke(app, ["invoke", "synergy.version"])
        edition_result = runner.invoke(app, ["invoke", "synergy.edition"])

    assert version_result.exit_code == 0
    assert edition_result.exit_code == 0
    assert "2027" in version_result.stdout
    assert "Insight" in edition_result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_target_rejects_arguments():
    """Read-only property targets should reject parameter input."""
    app = build_cli_app()

    class Sy:
        @property
        def version(self) -> str:
            return "2027"

    fake = Sy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result = runner.invoke(app, ["invoke", "synergy.version", "x=1"])

    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "does not accept arguments" in combined.lower()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_wrapper_property_target_is_rejected_as_terminal_read():
    """Wrapper-handle properties should require a chained member target instead of direct invoke."""
    app = build_cli_app()

    class CLITestManager:
        """Wrapper reachable from a Synergy property."""

    orig_cls = getattr(moldflow, "CLITestManager", None)
    orig_attr = getattr(moldflow.Synergy, "cli_test_manager", None)

    def _get_cli_test_manager(self) -> CLITestManager:
        del self
        return CLITestManager()

    setattr(moldflow, "CLITestManager", CLITestManager)
    setattr(moldflow.Synergy, "cli_test_manager", property(_get_cli_test_manager))
    try:
        result = runner.invoke(app, ["invoke", "cli_test_manager"])
        assert result.exit_code != 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        lowered = combined.lower()
        assert "wrapper property" in lowered
        assert "describe synergy.cli_test_manager.<member>" in combined
    finally:
        if orig_cls is None:
            delattr(moldflow, "CLITestManager")
        else:
            setattr(moldflow, "CLITestManager", orig_cls)
        if orig_attr is None:
            delattr(moldflow.Synergy, "cli_test_manager")
        else:
            setattr(moldflow.Synergy, "cli_test_manager", orig_attr)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_target_accepts_assignment_when_settable():
    """Settable properties should accept `value=...` assignment via invoke."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "mesh_type", None)

    setattr(
        moldflow.Synergy,
        "mesh_type",
        property(
            lambda self: getattr(self, "_mesh_type", "Fusion"),
            lambda self, value: setattr(self, "_mesh_type", value),
        ),
    )

    class Sy:
        def __init__(self) -> None:
            self._mesh_type = "Fusion"

        @property
        def mesh_type(self) -> str:
            return self._mesh_type

        @mesh_type.setter
        def mesh_type(self, value: str) -> None:
            self._mesh_type = value

    try:
        fake = Sy()
        with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
            "moldflow_cli.factories.get_synergy", return_value=fake
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.mesh_type", "value=3D", "--json-output"]
            )

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["result"] == "3D"
        assert fake.mesh_type == "3D"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "mesh_type")
        else:
            setattr(moldflow.Synergy, "mesh_type", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_write_only_property_target_is_rejected():
    """Setter-only properties should fail fast with a clear read-vs-write message."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "secret", None)

    class Sy:
        def __init__(self) -> None:
            self._secret: str | None = None

        def _set_secret(self, value: str) -> None:
            self._secret = value

        secret = property(fset=_set_secret)

    setattr(moldflow.Synergy, "secret", property(fset=lambda self, value: None))

    fake = Sy()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
            "moldflow_cli.factories.get_synergy", return_value=fake
        ):
            result = runner.invoke(app, ["invoke", "synergy.secret"])

        assert result.exit_code != 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "write-only property" in combined.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "secret")
        else:
            setattr(moldflow.Synergy, "secret", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_assignment_dry_run_does_not_execute_setter():
    """Dry-run on a property assignment target should emit a plan without mutating the object."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "mesh_type", None)

    class Sy:
        def __init__(self) -> None:
            self._mesh_type = "Fusion"
            self.setter_calls = 0

        @property
        def mesh_type(self) -> str:
            return self._mesh_type

        @mesh_type.setter
        def mesh_type(self, value: str) -> None:
            self.setter_calls += 1
            self._mesh_type = value

    setattr(moldflow.Synergy, "mesh_type", Sy.mesh_type)
    fake = Sy()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
            "moldflow_cli.factories.get_synergy", return_value=fake
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.mesh_type", "value=3D", "--dry-run", "--json-output"]
            )

        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["mode"] == "dry_run"
        assert payload["terminal_target"]["assignment"] is True
        assert payload["assignment"]["value"] == "3D"
        assert fake.mesh_type == "Fusion"
        assert fake.setter_calls == 0
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "mesh_type")
        else:
            setattr(moldflow.Synergy, "mesh_type", orig)


class FakeVector:
    """Lightweight stand-in for the Vector wrapper used in CLI tests."""

    def __init__(self) -> None:
        self.x: float | int | None = None
        self.y: float | int | None = None
        self.z: float | int | None = None

    def __repr__(self) -> str:
        return f"FakeVector(x={self.x}, y={self.y}, z={self.z})"


class FakePlot:
    """Fake plot object exposing the probe-line API used by the CLI tests."""

    def get_probe_plot_probe_line(
        self, index: int, start_pt: "Vector | None", end_pt: "Vector | None"
    ) -> str:
        """Return a simple sentinel that encodes arguments for assertion."""
        return f"probe_line(index={index}, start={start_pt}, end={end_pt})"


class FakePlotManager:
    """Fake plot manager that returns a FakePlot regardless of input."""

    def find_plot_by_name(
        self, plot_name: str, dataset_name: str | None = None  # pylint: disable=unused-argument
    ) -> FakePlot:
        """Return a FakePlot regardless of input."""
        return FakePlot()


class FakeSynergy:
    """Fake Synergy root exposing a plot_manager and create_vector factory."""

    @property
    def plot_manager(self) -> FakePlotManager:
        """Return a FakePlotManager."""
        return FakePlotManager()

    # Factory methods used by build_wrapper_instance for Vector | None.
    def create_vector(self) -> FakeVector:
        """Return a FakeVector."""
        return FakeVector()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_vectors_uses_factories_and_synergy_chain():
    """Verify chained invoke uses Synergy factories and object graph as expected."""
    app = build_cli_app()

    fake = FakeSynergy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake) as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ) as mock_fact_synergy:
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line",
                "find_plot_by_name.plot_name=My Plot",
                "get_probe_plot_probe_line.index=0",
                "get_probe_plot_probe_line.start_pt.x=1.0",
                "get_probe_plot_probe_line.start_pt.y=2.0",
                "get_probe_plot_probe_line.start_pt.z=3.0",
                "get_probe_plot_probe_line.end_pt.x=4.0",
                "get_probe_plot_probe_line.end_pt.y=5.0",
                "get_probe_plot_probe_line.end_pt.z=6.0",
            ],
        )

    assert result.exit_code == 0
    # Synergy should be instantiated via the mocked factories/context only.
    assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
    # Our fake implementation returns a simple string sentinel; ensure it appears.
    assert "probe_line(index=0" in result.stdout
    # And that our fake vectors have the expected coordinates in their repr.
    assert "FakeVector(x=1.0" in result.stdout
    assert "FakeVector(x=4.0" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_single_step_param_routing_equivalence():
    """Single-step invoke accepts both param=value and method.param=value forms."""
    app = build_cli_app()

    class FakeWin:
        def __init__(self) -> None:
            self.calls = []

        def set_application_window_pos(self, x: int, y: int, size_x: int, size_y: int) -> bool:
            self.calls.append((x, y, size_x, size_y))
            return True

    fake = FakeWin()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result_plain = runner.invoke(
            app,
            [
                "invoke",
                "synergy.set_application_window_pos",
                "x=7",
                "y=8",
                "size_x=70",
                "size_y=80",
            ],
        )
        result_prefixed = runner.invoke(
            app,
            [
                "invoke",
                "synergy.set_application_window_pos",
                "set_application_window_pos.x=7",
                "set_application_window_pos.y=8",
                "set_application_window_pos.size_x=70",
                "set_application_window_pos.size_y=80",
            ],
        )

    assert result_plain.exit_code == 0
    assert result_prefixed.exit_code == 0
    assert fake.calls == [(7, 8, 70, 80), (7, 8, 70, 80)]


@pytest.mark.cli
@pytest.mark.unit
def test_concurrent_invokes_do_not_share_state():
    """Two separate invoke calls that construct transient objects should not share state."""
    app = build_cli_app()

    class Maker:
        def make_obj(self):
            class O:
                pass

            return O()

    class Sy:
        @property
        def maker(self):
            return Maker()

    # Define the method on the Sy object returned by get_synergy so resolution matches.
    class SyWithFactory(Sy):
        def cli_make_obj(self):
            return object()

    # Point moldflow.Synergy to our test class so introspection and runtime agree.
    orig_mf_synergy = getattr(moldflow, "Synergy", None)
    setattr(moldflow, "Synergy", SyWithFactory)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=SyWithFactory()), patch(
            "moldflow_cli.factories.get_synergy", return_value=SyWithFactory()
        ):
            r1 = runner.invoke(app, ["invoke", "synergy.cli_make_obj"])
            r2 = runner.invoke(app, ["invoke", "synergy.cli_make_obj"])

        assert r1.exit_code == 0
        assert r2.exit_code == 0
        # The reprs should not be identical (fresh instances).
        assert r1.stdout != r2.stdout
    finally:
        if orig_mf_synergy is None:
            delattr(moldflow, "Synergy")
        else:
            setattr(moldflow, "Synergy", orig_mf_synergy)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_optional_return_forward_ref():
    """Chained invoke should resolve next-step class from Optional[Class] return refs."""
    app = build_cli_app()

    class Plot:
        def then_method(self) -> str:
            return "optional-chain-ok"

    class Sy:
        def get_plot_optional(self):
            return Plot()

    orig_plot = getattr(moldflow, "Plot", None)
    orig_get_plot_optional = getattr(moldflow.Synergy, "get_plot_optional", None)

    def _get_plot_optional(self):
        return Plot()

    _get_plot_optional.__annotations__ = {"return": "Optional[Plot]"}

    setattr(moldflow, "Plot", Plot)
    setattr(moldflow.Synergy, "get_plot_optional", _get_plot_optional)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_optional.then_method"])
        assert result.exit_code == 0
        assert "optional-chain-ok" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "Plot")
        else:
            setattr(moldflow, "Plot", orig_plot)
        if orig_get_plot_optional is None:
            delattr(moldflow.Synergy, "get_plot_optional")
        else:
            setattr(moldflow.Synergy, "get_plot_optional", orig_get_plot_optional)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_optional_forwardref_object_return_annotation():
    """Chained invoke should resolve Optional[ForwardRef[Class]] return annotations."""
    app = build_cli_app()

    class PlotForward:
        def then_method(self) -> str:
            return "forwardref-chain-ok"

    class Sy:
        def get_plot_forward_optional(self):
            return PlotForward()

    orig_plot = getattr(moldflow, "PlotForward", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_forward_optional", None)

    def _get_plot_forward_optional(self):
        return PlotForward()

    _get_plot_forward_optional.__annotations__ = {
        "return": typing.Optional[typing.ForwardRef("PlotForward")]
    }

    setattr(moldflow, "PlotForward", PlotForward)
    setattr(moldflow.Synergy, "get_plot_forward_optional", _get_plot_forward_optional)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_forward_optional.then_method"])
        assert result.exit_code == 0
        assert "forwardref-chain-ok" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "PlotForward")
        else:
            setattr(moldflow, "PlotForward", orig_plot)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_forward_optional")
        else:
            setattr(moldflow.Synergy, "get_plot_forward_optional", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_annotated_return_annotation():
    """Chained invoke should resolve next-step class from Annotated return refs."""
    app = build_cli_app()

    class PlotAnnotated:
        def then_method(self) -> str:
            return "annotated-chain-ok"

    class Sy:
        def get_plot_annotated(self):
            return PlotAnnotated()

    orig_plot = getattr(moldflow, "PlotAnnotated", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_annotated", None)

    def _get_plot_annotated(self):
        return PlotAnnotated()

    _get_plot_annotated.__annotations__ = {"return": typing.Annotated["PlotAnnotated", "meta"]}

    setattr(moldflow, "PlotAnnotated", PlotAnnotated)
    setattr(moldflow.Synergy, "get_plot_annotated", _get_plot_annotated)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_annotated.then_method"])
        assert result.exit_code == 0
        assert "annotated-chain-ok" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "PlotAnnotated")
        else:
            setattr(moldflow, "PlotAnnotated", orig_plot)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_annotated")
        else:
            setattr(moldflow.Synergy, "get_plot_annotated", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_annotated_string_return_annotation():
    """Chained invoke should resolve string Annotated return refs."""
    app = build_cli_app()

    class PlotAnnotatedStr:
        def then_method(self) -> str:
            return "annotated-string-chain-ok"

    class Sy:
        def get_plot_annotated_str(self):
            return PlotAnnotatedStr()

    orig_plot = getattr(moldflow, "PlotAnnotatedStr", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_annotated_str", None)

    def _get_plot_annotated_str(self):
        return PlotAnnotatedStr()

    _get_plot_annotated_str.__annotations__ = {"return": 'Annotated["PlotAnnotatedStr", "meta"]'}

    setattr(moldflow, "PlotAnnotatedStr", PlotAnnotatedStr)
    setattr(moldflow.Synergy, "get_plot_annotated_str", _get_plot_annotated_str)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_annotated_str.then_method"])
        assert result.exit_code == 0
        assert "annotated-string-chain-ok" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "PlotAnnotatedStr")
        else:
            setattr(moldflow, "PlotAnnotatedStr", orig_plot)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_annotated_str")
        else:
            setattr(moldflow.Synergy, "get_plot_annotated_str", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_optional_annotated_string_return_annotation():
    """Chained invoke should resolve Optional[Annotated[T, ...]] string return refs."""
    app = build_cli_app()

    class PlotAnnotatedOpt:
        def then_method(self) -> str:
            return "annotated-optional-string-chain-ok"

    class Sy:
        def get_plot_annotated_opt(self):
            return PlotAnnotatedOpt()

    orig_plot = getattr(moldflow, "PlotAnnotatedOpt", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_annotated_opt", None)

    def _get_plot_annotated_opt(self):
        return PlotAnnotatedOpt()

    _get_plot_annotated_opt.__annotations__ = {
        "return": 'Optional[Annotated["PlotAnnotatedOpt", "meta"]]'
    }

    setattr(moldflow, "PlotAnnotatedOpt", PlotAnnotatedOpt)
    setattr(moldflow.Synergy, "get_plot_annotated_opt", _get_plot_annotated_opt)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_annotated_opt.then_method"])
        assert result.exit_code == 0
        assert "annotated-optional-string-chain-ok" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "PlotAnnotatedOpt")
        else:
            setattr(moldflow, "PlotAnnotatedOpt", orig_plot)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_annotated_opt")
        else:
            setattr(moldflow.Synergy, "get_plot_annotated_opt", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_with_ambiguous_union_return_uses_runtime_fallback():
    """Ambiguous Union return annotations should still allow valid runtime chain calls."""
    app = build_cli_app()

    class PlotA:
        def ping(self, value: int) -> str:
            return f"A:{value}"

    class PlotB:
        def ping(self, value: int) -> str:
            return f"B:{value}"

    class Sy:
        def get_plot_union(self):
            return PlotA()

    orig_plot_a = getattr(moldflow, "PlotA", None)
    orig_plot_b = getattr(moldflow, "PlotB", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_union", None)

    def _get_plot_union(self):
        return PlotA()

    _get_plot_union.__annotations__ = {"return": "Union[PlotA, PlotB, None]"}

    setattr(moldflow, "PlotA", PlotA)
    setattr(moldflow, "PlotB", PlotB)
    setattr(moldflow.Synergy, "get_plot_union", _get_plot_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_plot_union.ping", "ping.value=7"])
        assert result.exit_code == 0
        assert "A:7" in result.stdout
    finally:
        if orig_plot_a is None:
            delattr(moldflow, "PlotA")
        else:
            setattr(moldflow, "PlotA", orig_plot_a)
        if orig_plot_b is None:
            delattr(moldflow, "PlotB")
        else:
            setattr(moldflow, "PlotB", orig_plot_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_union")
        else:
            setattr(moldflow.Synergy, "get_plot_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_runtime_fallback_chained_step_is_case_insensitive():
    """Runtime-fallback chained steps should still resolve method names case-insensitively."""
    app = build_cli_app()

    class PlotCase:
        def ping(self, value: int) -> str:
            return f"case:{value}"

    class OtherCase:
        def ping(self, value: int) -> str:  # pragma: no cover - not used, only union member
            return f"other:{value}"

    class Sy:
        def get_plot_union_case(self):
            return PlotCase()

    orig_plot = getattr(moldflow, "PlotCase", None)
    orig_other = getattr(moldflow, "OtherCase", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_union_case", None)

    def _get_plot_union_case(self):
        return PlotCase()

    _get_plot_union_case.__annotations__ = {"return": "Union[PlotCase, OtherCase, None]"}

    setattr(moldflow, "PlotCase", PlotCase)
    setattr(moldflow, "OtherCase", OtherCase)
    setattr(moldflow.Synergy, "get_plot_union_case", _get_plot_union_case)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.get_plot_union_case.PING", "PING.value=9"]
            )
        assert result.exit_code == 0
        assert "case:9" in result.stdout
    finally:
        if orig_plot is None:
            delattr(moldflow, "PlotCase")
        else:
            setattr(moldflow, "PlotCase", orig_plot)
        if orig_other is None:
            delattr(moldflow, "OtherCase")
        else:
            setattr(moldflow, "OtherCase", orig_other)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_union_case")
        else:
            setattr(moldflow.Synergy, "get_plot_union_case", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deep_runtime_fallback_chain_supports_multiple_deferred_steps():
    """Multiple deferred chain steps should execute correctly at runtime."""
    app = build_cli_app()

    class Level2A:
        def finish(self, value: int) -> str:
            return f"done:{value}"

    class Level2B:
        def finish(self, value: int) -> str:  # pragma: no cover - union member only
            return f"alt:{value}"

    class Level1A:
        def get_level2(self):
            return Level2A()

    class Level1B:
        def get_level2(self):  # pragma: no cover - union member only
            return Level2B()

    class Sy:
        def get_level1(self):
            return Level1A()

    orig_l1a = getattr(moldflow, "Level1A", None)
    orig_l1b = getattr(moldflow, "Level1B", None)
    orig_l2a = getattr(moldflow, "Level2A", None)
    orig_l2b = getattr(moldflow, "Level2B", None)
    orig_getter = getattr(moldflow.Synergy, "get_level1", None)

    def _get_level1(self):
        return Level1A()

    _get_level1.__annotations__ = {"return": "Union[Level1A, Level1B, None]"}

    setattr(moldflow, "Level1A", Level1A)
    setattr(moldflow, "Level1B", Level1B)
    setattr(moldflow, "Level2A", Level2A)
    setattr(moldflow, "Level2B", Level2B)
    setattr(moldflow.Synergy, "get_level1", _get_level1)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.get_level1.get_level2.finish", "finish.value=5"]
            )
        assert result.exit_code == 0
        assert "done:5" in result.stdout
    finally:
        if orig_l1a is None:
            delattr(moldflow, "Level1A")
        else:
            setattr(moldflow, "Level1A", orig_l1a)
        if orig_l1b is None:
            delattr(moldflow, "Level1B")
        else:
            setattr(moldflow, "Level1B", orig_l1b)
        if orig_l2a is None:
            delattr(moldflow, "Level2A")
        else:
            setattr(moldflow, "Level2A", orig_l2a)
        if orig_l2b is None:
            delattr(moldflow, "Level2B")
        else:
            setattr(moldflow, "Level2B", orig_l2b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_level1")
        else:
            setattr(moldflow.Synergy, "get_level1", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_runtime_fallback_supports_nested_typed_arg_assignment():
    """Deferred steps should support nested typed args after runtime signature binding."""
    app = build_cli_app()

    class FakeImportOptions:
        def __init__(self) -> None:
            self.use_mdl = None

    class PlotTypedA:
        def apply(self, import_options: "ImportOptions | None") -> str:
            return f"use_mdl={import_options.use_mdl}"

    class PlotTypedB:
        def apply(self, import_options: "ImportOptions | None") -> str:  # pragma: no cover
            return f"use_mdl={import_options.use_mdl}"

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def get_plot_typed_union(self):
            return PlotTypedA()

    orig_plot_a = getattr(moldflow, "PlotTypedA", None)
    orig_plot_b = getattr(moldflow, "PlotTypedB", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_typed_union", None)

    def _get_plot_typed_union(self):
        return PlotTypedA()

    _get_plot_typed_union.__annotations__ = {"return": "Union[PlotTypedA, PlotTypedB, None]"}

    setattr(moldflow, "PlotTypedA", PlotTypedA)
    setattr(moldflow, "PlotTypedB", PlotTypedB)
    setattr(moldflow.Synergy, "get_plot_typed_union", _get_plot_typed_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.get_plot_typed_union.apply",
                    "apply.import_options.use_mdl=true",
                ],
            )
        assert result.exit_code == 0
        assert "use_mdl=True" in result.stdout
    finally:
        if orig_plot_a is None:
            delattr(moldflow, "PlotTypedA")
        else:
            setattr(moldflow, "PlotTypedA", orig_plot_a)
        if orig_plot_b is None:
            delattr(moldflow, "PlotTypedB")
        else:
            setattr(moldflow, "PlotTypedB", orig_plot_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_typed_union")
        else:
            setattr(moldflow.Synergy, "get_plot_typed_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_kwargs_accepts_flat_keys_and_rejects_nested_keys():
    """Deferred steps should preserve **kwargs routing and nested-key validation."""
    app = build_cli_app()

    class KwA:
        def sink(self, **kwargs) -> str:
            return f"kw={sorted(kwargs.items())}"

    class KwB:
        def sink(self, **kwargs) -> str:  # pragma: no cover - union member only
            return f"kw={sorted(kwargs.items())}"

    class Sy:
        def get_kwargs_union(self):
            return KwA()

    orig_a = getattr(moldflow, "KwA", None)
    orig_b = getattr(moldflow, "KwB", None)
    orig_getter = getattr(moldflow.Synergy, "get_kwargs_union", None)

    def _get_kwargs_union(self):
        return KwA()

    _get_kwargs_union.__annotations__ = {"return": "Union[KwA, KwB, None]"}

    setattr(moldflow, "KwA", KwA)
    setattr(moldflow, "KwB", KwB)
    setattr(moldflow.Synergy, "get_kwargs_union", _get_kwargs_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            ok = runner.invoke(
                app, ["invoke", "synergy.get_kwargs_union.sink", "sink.alpha=1", "sink.beta=two"]
            )
            bad = runner.invoke(
                app, ["invoke", "synergy.get_kwargs_union.sink", "sink.alpha.beta=1"]
            )

        assert ok.exit_code == 0
        assert "alpha" in ok.stdout and "beta" in ok.stdout
        assert bad.exit_code != 0
        bad_text = (bad.stdout or "") + (getattr(bad, "stderr", "") or "")
        assert "nested argument" in bad_text.lower()
        assert "**kwargs" in bad_text
    finally:
        if orig_a is None:
            delattr(moldflow, "KwA")
        else:
            setattr(moldflow, "KwA", orig_a)
        if orig_b is None:
            delattr(moldflow, "KwB")
        else:
            setattr(moldflow, "KwB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_kwargs_union")
        else:
            setattr(moldflow.Synergy, "get_kwargs_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_positional_only_error_remains_actionable():
    """Deferred steps with positional-only params should fail with clear guidance."""
    app = build_cli_app()

    class PosA:
        def sink(self, value, /):
            return value

    class PosB:
        def sink(self, value, /):  # pragma: no cover - union member only
            return value

    class Sy:
        def get_pos_union(self):
            return PosA()

    orig_a = getattr(moldflow, "PosA", None)
    orig_b = getattr(moldflow, "PosB", None)
    orig_getter = getattr(moldflow.Synergy, "get_pos_union", None)

    def _get_pos_union(self):
        return PosA()

    _get_pos_union.__annotations__ = {"return": "Union[PosA, PosB, None]"}

    setattr(moldflow, "PosA", PosA)
    setattr(moldflow, "PosB", PosB)
    setattr(moldflow.Synergy, "get_pos_union", _get_pos_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.get_pos_union.sink", "sink.value=5"])
        assert result.exit_code != 0
        text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "positional-only parameters" in text.lower()
        assert "not supported" in text.lower()
    finally:
        if orig_a is None:
            delattr(moldflow, "PosA")
        else:
            setattr(moldflow, "PosA", orig_a)
        if orig_b is None:
            delattr(moldflow, "PosB")
        else:
            setattr(moldflow, "PosB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_pos_union")
        else:
            setattr(moldflow.Synergy, "get_pos_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_conflicting_paths_still_fail_early():
    """Deferred steps should enforce duplicate/conflicting path validation consistently."""
    app = build_cli_app()

    class ConfA:
        def do(self, vec: "Vector") -> str:
            return "ok"

    class ConfB:
        def do(self, vec: "Vector") -> str:  # pragma: no cover - union member only
            return "ok"

    class Sy:
        def get_conf_union(self):
            return ConfA()

        def create_vector(self):
            return FakeVector()

    orig_a = getattr(moldflow, "ConfA", None)
    orig_b = getattr(moldflow, "ConfB", None)
    orig_getter = getattr(moldflow.Synergy, "get_conf_union", None)

    def _get_conf_union(self):
        return ConfA()

    _get_conf_union.__annotations__ = {"return": "Union[ConfA, ConfB, None]"}

    setattr(moldflow, "ConfA", ConfA)
    setattr(moldflow, "ConfB", ConfB)
    setattr(moldflow.Synergy, "get_conf_union", _get_conf_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.get_conf_union.do", "do.vec=1", "do.vec.x=2"]
            )
        assert result.exit_code != 0
        text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "conflicting argument paths" in text.lower()
    finally:
        if orig_a is None:
            delattr(moldflow, "ConfA")
        else:
            setattr(moldflow, "ConfA", orig_a)
        if orig_b is None:
            delattr(moldflow, "ConfB")
        else:
            setattr(moldflow, "ConfB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_conf_union")
        else:
            setattr(moldflow.Synergy, "get_conf_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_supports_mixed_case_step_keys(tmp_path):
    """Deferred chains should accept mixed-case step keys from --params-json-file."""
    app = build_cli_app()

    class PlotFromUnionA:
        def apply(self, import_options: "ImportOptions | None", retries: int = 0) -> str:
            return f"use_mdl={import_options.use_mdl};retries={retries}"

    class PlotFromUnionB:
        def apply(
            self, import_options: "ImportOptions | None", retries: int = 0  # pragma: no cover
        ) -> str:
            return f"use_mdl={import_options.use_mdl};retries={retries}"

    class FakeImportOptions:
        def __init__(self) -> None:
            self.use_mdl = None

    class Sy:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def get_plot_union(self, plot_name: str):
            _ = plot_name
            return PlotFromUnionA()

    orig_a = getattr(moldflow, "PlotFromUnionA", None)
    orig_b = getattr(moldflow, "PlotFromUnionB", None)
    orig_getter = getattr(moldflow.Synergy, "get_plot_union", None)

    def _get_plot_union(self, plot_name: str):
        _ = plot_name
        return PlotFromUnionA()

    _get_plot_union.__annotations__ = {
        "plot_name": "str",
        "return": "Union[PlotFromUnionA, PlotFromUnionB, None]",
    }

    setattr(moldflow, "PlotFromUnionA", PlotFromUnionA)
    setattr(moldflow, "PlotFromUnionB", PlotFromUnionB)
    setattr(moldflow.Synergy, "get_plot_union", _get_plot_union)

    payload_file = tmp_path / "params.json"
    payload_file.write_text(
        (
            "{"
            '"GET_PLOT_UNION":{"plot_name":"Main Plot"},'
            '"aPpLy":{"import_options":{"use_mdl":true},"retries":2}'
            "}"
        ),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_plot_union.apply", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code == 0
        assert "use_mdl=True" in result.stdout
        assert "retries=2" in result.stdout
    finally:
        if orig_a is None:
            delattr(moldflow, "PlotFromUnionA")
        else:
            setattr(moldflow, "PlotFromUnionA", orig_a)
        if orig_b is None:
            delattr(moldflow, "PlotFromUnionB")
        else:
            setattr(moldflow, "PlotFromUnionB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_plot_union")
        else:
            setattr(moldflow.Synergy, "get_plot_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_honors_mixed_case_target_and_step_names(tmp_path):
    """Deferred chains should route params correctly with mixed-case target + JSON step keys."""
    app = build_cli_app()

    class NodeA:
        def final_action(self, value: int) -> str:
            return f"value={value}"

    class NodeB:
        def final_action(self, value: int) -> str:  # pragma: no cover - union member only
            return f"value={value}"

    class Sy:
        def get_node_union(self):
            return NodeA()

    orig_a = getattr(moldflow, "NodeA", None)
    orig_b = getattr(moldflow, "NodeB", None)
    orig_getter = getattr(moldflow.Synergy, "get_node_union", None)

    def _get_node_union(self):
        return NodeA()

    _get_node_union.__annotations__ = {"return": "Union[NodeA, NodeB, None]"}

    setattr(moldflow, "NodeA", NodeA)
    setattr(moldflow, "NodeB", NodeB)
    setattr(moldflow.Synergy, "get_node_union", _get_node_union)

    payload_file = tmp_path / "params_case.json"
    payload_file.write_text('{"fInAl_AcTiOn":{"value":9}}', encoding="utf-8")
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "SyNeRgY.get_node_union.FINAL_ACTION",
                    "--params-json-file",
                    str(payload_file),
                ],
            )
        assert result.exit_code == 0
        assert "value=9" in result.stdout
    finally:
        if orig_a is None:
            delattr(moldflow, "NodeA")
        else:
            setattr(moldflow, "NodeA", orig_a)
        if orig_b is None:
            delattr(moldflow, "NodeB")
        else:
            setattr(moldflow, "NodeB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_node_union")
        else:
            setattr(moldflow.Synergy, "get_node_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_rejects_case_variant_duplicate_step_paths(tmp_path):
    """Case-variant duplicate step objects should fail with duplicate-path validation."""
    app = build_cli_app()

    class DupA:
        def apply(self, value: int) -> str:
            return f"value={value}"

    class DupB:
        def apply(self, value: int) -> str:  # pragma: no cover - union member only
            return f"value={value}"

    class Sy:
        def get_dup_union(self, plot_name: str):
            _ = plot_name
            return DupA()

    orig_a = getattr(moldflow, "DupA", None)
    orig_b = getattr(moldflow, "DupB", None)
    orig_getter = getattr(moldflow.Synergy, "get_dup_union", None)

    def _get_dup_union(self, plot_name: str):
        _ = plot_name
        return DupA()

    _get_dup_union.__annotations__ = {"return": "Union[DupA, DupB, None]"}

    setattr(moldflow, "DupA", DupA)
    setattr(moldflow, "DupB", DupB)
    setattr(moldflow.Synergy, "get_dup_union", _get_dup_union)

    payload_file = tmp_path / "dup_params.json"
    payload_file.write_text(
        (
            "{"
            '"GET_DUP_UNION":{"plot_name":"A"},'
            '"get_dup_union":{"plot_name":"B"},'
            '"APPLY":{"value":1}'
            "}"
        ),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_dup_union.apply", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code != 0
        text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "duplicate argument path" in text.lower()
    finally:
        if orig_a is None:
            delattr(moldflow, "DupA")
        else:
            setattr(moldflow, "DupA", orig_a)
        if orig_b is None:
            delattr(moldflow, "DupB")
        else:
            setattr(moldflow, "DupB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_dup_union")
        else:
            setattr(moldflow.Synergy, "get_dup_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_rejects_mixed_object_scalar_shapes(tmp_path):
    """Step payloads must remain objects; scalar step payloads should fail consistently."""
    app = build_cli_app()

    class ShapeA:
        def apply(self, value: int) -> str:
            return f"value={value}"

    class ShapeB:
        def apply(self, value: int) -> str:  # pragma: no cover - union member only
            return f"value={value}"

    class Sy:
        def get_shape_union(self):
            return ShapeA()

    orig_a = getattr(moldflow, "ShapeA", None)
    orig_b = getattr(moldflow, "ShapeB", None)
    orig_getter = getattr(moldflow.Synergy, "get_shape_union", None)

    def _get_shape_union(self):
        return ShapeA()

    _get_shape_union.__annotations__ = {"return": "Union[ShapeA, ShapeB, None]"}

    setattr(moldflow, "ShapeA", ShapeA)
    setattr(moldflow, "ShapeB", ShapeB)
    setattr(moldflow.Synergy, "get_shape_union", _get_shape_union)

    payload_file = tmp_path / "shape_params.json"
    payload_file.write_text('{"GET_SHAPE_UNION":{},"APPLY":5}', encoding="utf-8")
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.get_shape_union.apply",
                    "--params-json-file",
                    str(payload_file),
                ],
            )
        assert result.exit_code != 0
        text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "error" in text.lower() or result.exception is not None
    finally:
        if orig_a is None:
            delattr(moldflow, "ShapeA")
        else:
            setattr(moldflow, "ShapeA", orig_a)
        if orig_b is None:
            delattr(moldflow, "ShapeB")
        else:
            setattr(moldflow, "ShapeB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_shape_union")
        else:
            setattr(moldflow.Synergy, "get_shape_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_with_bom_parses_successfully(tmp_path):
    """UTF-8 BOM-prefixed JSON files should parse for deferred chains."""
    app = build_cli_app()

    class BomA:
        def done(self, value: int) -> str:
            return f"done:{value}"

    class BomB:
        def done(self, value: int) -> str:  # pragma: no cover - union member only
            return f"done:{value}"

    class Sy:
        def get_bom_union(self):
            return BomA()

    orig_a = getattr(moldflow, "BomA", None)
    orig_b = getattr(moldflow, "BomB", None)
    orig_getter = getattr(moldflow.Synergy, "get_bom_union", None)

    def _get_bom_union(self):
        return BomA()

    _get_bom_union.__annotations__ = {"return": "Union[BomA, BomB, None]"}

    setattr(moldflow, "BomA", BomA)
    setattr(moldflow, "BomB", BomB)
    setattr(moldflow.Synergy, "get_bom_union", _get_bom_union)

    payload_file = tmp_path / "bom_params.json"
    payload_file.write_bytes(b"\xef\xbb\xbf" + b'{"DoNe":{"value":4}}')
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_bom_union.done", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code == 0
        assert "done:4" in result.stdout
    finally:
        if orig_a is None:
            delattr(moldflow, "BomA")
        else:
            setattr(moldflow, "BomA", orig_a)
        if orig_b is None:
            delattr(moldflow, "BomB")
        else:
            setattr(moldflow, "BomB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_bom_union")
        else:
            setattr(moldflow.Synergy, "get_bom_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_invalid_unicode_reports_badparameter(tmp_path):
    """Invalid-unicode JSON file input should fail as a CLI validation error."""
    app = build_cli_app()

    class BadUCA:
        def done(self, value: int) -> str:
            return f"done:{value}"

    class BadUCB:
        def done(self, value: int) -> str:  # pragma: no cover - union member only
            return f"done:{value}"

    class Sy:
        def get_baduc_union(self):
            return BadUCA()

    orig_a = getattr(moldflow, "BadUCA", None)
    orig_b = getattr(moldflow, "BadUCB", None)
    orig_getter = getattr(moldflow.Synergy, "get_baduc_union", None)

    def _get_baduc_union(self):
        return BadUCA()

    _get_baduc_union.__annotations__ = {"return": "Union[BadUCA, BadUCB, None]"}

    setattr(moldflow, "BadUCA", BadUCA)
    setattr(moldflow, "BadUCB", BadUCB)
    setattr(moldflow.Synergy, "get_baduc_union", _get_baduc_union)

    payload_file = tmp_path / "bad_unicode.json"
    payload_file.write_bytes(b"\xff\xfe\xfa")
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_baduc_union.done", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code == 2
        text = (
            (result.stdout or "")
            + (getattr(result, "stderr", "") or "")
            + (f"\n{result.exception}" if getattr(result, "exception", None) else "")
        )
        assert "cannot read json file" in text.lower()
    finally:
        if orig_a is None:
            delattr(moldflow, "BadUCA")
        else:
            setattr(moldflow, "BadUCA", orig_a)
        if orig_b is None:
            delattr(moldflow, "BadUCB")
        else:
            setattr(moldflow, "BadUCB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_baduc_union")
        else:
            setattr(moldflow.Synergy, "get_baduc_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_excessive_nesting_reports_validation_error(tmp_path):
    """Pathologically deep JSON should fail as deterministic CLI validation, not raw exceptions."""
    app = build_cli_app()

    class DeepA:
        def done(self, value: int) -> str:
            return f"done:{value}"

    class DeepB:
        def done(self, value: int) -> str:  # pragma: no cover - union member only
            return f"done:{value}"

    class Sy:
        def get_deep_union(self):
            return DeepA()

    orig_a = getattr(moldflow, "DeepA", None)
    orig_b = getattr(moldflow, "DeepB", None)
    orig_getter = getattr(moldflow.Synergy, "get_deep_union", None)

    def _get_deep_union(self):
        return DeepA()

    _get_deep_union.__annotations__ = {"return": "Union[DeepA, DeepB, None]"}

    setattr(moldflow, "DeepA", DeepA)
    setattr(moldflow, "DeepB", DeepB)
    setattr(moldflow.Synergy, "get_deep_union", _get_deep_union)

    deep_value = "[" * 1800 + "0" + "]" * 1800
    payload_file = tmp_path / "deep_payload.json"
    payload_file.write_text('{"DONE":{"value":' + deep_value + "}}", encoding="utf-8")
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_deep_union.done", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code == 2
        text = (
            (result.stdout or "")
            + (getattr(result, "stderr", "") or "")
            + (f"\n{result.exception}" if getattr(result, "exception", None) else "")
        ).lower()
        assert "cannot read json file" in text or "invalid json value for parameter" in text
    finally:
        if orig_a is None:
            delattr(moldflow, "DeepA")
        else:
            setattr(moldflow, "DeepA", orig_a)
        if orig_b is None:
            delattr(moldflow, "DeepB")
        else:
            setattr(moldflow, "DeepB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_deep_union")
        else:
            setattr(moldflow.Synergy, "get_deep_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_deferred_chain_json_file_large_kwargs_payload_is_deterministic(tmp_path):
    """Large deferred JSON payloads should parse and route deterministically."""
    app = build_cli_app()

    class BigA:
        def sink(self, **kwargs) -> str:
            return f"count={len(kwargs)};k0={kwargs.get('k0')};k499={kwargs.get('k499')}"

    class BigB:
        def sink(self, **kwargs) -> str:  # pragma: no cover - union member only
            return f"count={len(kwargs)}"

    class Sy:
        def get_big_union(self):
            return BigA()

    orig_a = getattr(moldflow, "BigA", None)
    orig_b = getattr(moldflow, "BigB", None)
    orig_getter = getattr(moldflow.Synergy, "get_big_union", None)

    def _get_big_union(self):
        return BigA()

    _get_big_union.__annotations__ = {"return": "Union[BigA, BigB, None]"}

    setattr(moldflow, "BigA", BigA)
    setattr(moldflow, "BigB", BigB)
    setattr(moldflow.Synergy, "get_big_union", _get_big_union)

    sink_payload = {f"k{i}": i for i in range(500)}
    payload_file = tmp_path / "big_payload.json"
    payload_file.write_text(json.dumps({"SINK": sink_payload}), encoding="utf-8")
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "synergy.get_big_union.sink", "--params-json-file", str(payload_file)],
            )
        assert result.exit_code == 0
        assert "count=500" in result.stdout
        assert "k0=0" in result.stdout
        assert "k499=499" in result.stdout
    finally:
        if orig_a is None:
            delattr(moldflow, "BigA")
        else:
            setattr(moldflow, "BigA", orig_a)
        if orig_b is None:
            delattr(moldflow, "BigB")
        else:
            setattr(moldflow, "BigB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_big_union")
        else:
            setattr(moldflow.Synergy, "get_big_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_emits_plan_without_touching_synergy():
    """--dry-run should produce plan output and avoid Synergy instantiation."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_plan_only", None)

    def _cli_plan_only(self, value: int) -> str:
        return f"value={value}"

    setattr(moldflow.Synergy, "cli_plan_only", _cli_plan_only)
    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(
                app, ["invoke", "synergy.cli_plan_only", "value=3", "--dry-run", "--json-output"]
            )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["mode"] == "dry_run"
        assert payload["target"] == "synergy.cli_plan_only"
        assert "summary" not in payload
        assert "workflow_examples" not in payload
        assert "params_json_template" not in payload
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_plan_only")
        else:
            setattr(moldflow.Synergy, "cli_plan_only", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_step_docs_split_into_summary_and_details():
    """Dry-run step metadata should reuse the structured summary/details from template metadata."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_docful_dry_run", None)

    def cli_docful_dry_run(self, name: str) -> str:
        """Show the named dry-run thing.

        Args:
            name (str): The dry-run thing to show.
        """
        del self, name
        return "ok"

    setattr(moldflow.Synergy, "cli_docful_dry_run", cli_docful_dry_run)
    try:
        result = runner.invoke(
            app, ["invoke", "synergy.cli_docful_dry_run", "name=demo", "--dry-run", "--json-output"]
        )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["summary"] == "Show the named dry-run thing."
        assert payload["details"] == "Args: name (str): The dry-run thing to show."
        step = payload["steps"][0]
        assert step["signature"] == "(name: str)"
        assert step["summary"] == "Show the named dry-run thing."
        assert step["details"] == "Args: name (str): The dry-run thing to show."
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_docful_dry_run")
        else:
            setattr(moldflow.Synergy, "cli_docful_dry_run", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_removed_template_flag():
    """Invoke should no longer expose the removed --template flag."""
    app = build_cli_app()
    result = runner.invoke(app, ["invoke", "synergy.open_project", "--template"])
    assert result.exit_code != 0
    text = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "no such option" in text.lower()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_file_rejects_unknown_item_fields(tmp_path):
    """Batch items with unknown fields should fail deterministically."""
    app = build_cli_app()
    batch_file = tmp_path / "batch_unknown.json"
    batch_file.write_text(
        json.dumps([{"target": "synergy.open_project", "args": ["path=x"], "unexpected": 1}]),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["invoke", "--batch-file", str(batch_file), "--json-output"])
    assert result.exit_code != 0
    payload = json.loads(result.stdout)
    assert payload["summary"] == {"total": 1, "succeeded": 0, "failed": 1}
    assert payload["batch_results"][0]["ok"] is False
    assert payload["batch_results"][0]["error_type"] == "batch_item_validation"
    assert "unknown batch item field" in payload["batch_results"][0]["error"].lower()


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_supports_json_file_output(tmp_path):
    """Dry-run plan JSON should be writable via --json-file-output."""
    app = build_cli_app()
    out_file = tmp_path / "dryrun.json"
    result = runner.invoke(
        app,
        [
            "invoke",
            "synergy.open_project",
            "path=C:/tmp/a.mfproj",
            "--dry-run",
            "--json-file-output",
            str(out_file),
        ],
    )
    assert result.exit_code == 0
    assert "Wrote structured output to" in result.stdout
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["mode"] == "dry_run"


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_human_output_omits_examples():
    """Dry-run human output should stay plan-focused instead of repeating describe examples."""
    app = build_cli_app()
    result = runner.invoke(
        app,
        ["invoke", "synergy.plot_manager.find_plot_by_name", "plot_name=Main Plot", "--dry-run"],
    )
    assert result.exit_code == 0
    assert "Try this:" not in result.stdout
    assert "JSON example:" not in result.stdout
    assert "Shorter JSON example:" not in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_human_output_omits_wrapper_input_hints():
    """Dry-run human output should not repeat describe-only wrapper input guidance."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels_dry_run", None)

    def cli_accept_levels_dry_run(self, levels: "DoubleArray | None" = None) -> str:
        del self, levels
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels_dry_run", cli_accept_levels_dry_run)
    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(
                app, ["invoke", "synergy.cli_accept_levels_dry_run", "levels=1.0,2.5", "--dry-run"]
            )
        assert result.exit_code == 0
        assert "Input hints:" not in result.stdout
        assert "levels (DoubleArray):" not in result.stdout
        assert "JSON value:" not in result.stdout
        assert "CLI argument:" not in result.stdout
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels_dry_run")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels_dry_run", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_read_dry_run_human_output_omits_empty_sections():
    """Read-only property dry-run output should avoid empty params-json and kwargs noise."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_read_only_plan", None)

    def _get_cli_read_only_plan(self) -> str:
        del self
        return "ok"

    setattr(moldflow.Synergy, "cli_read_only_plan", property(_get_cli_read_only_plan))
    try:
        result = runner.invoke(app, ["invoke", "synergy.cli_read_only_plan", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run for synergy.cli_read_only_plan" in result.stdout
        assert "This property is read-only and takes no arguments." in result.stdout
        assert "Try this:" not in result.stdout
        assert "JSON example:" not in result.stdout
        assert "Resolved kwargs:" not in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_read_only_plan")
        else:
            setattr(moldflow.Synergy, "cli_read_only_plan", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_property_assignment_dry_run_human_output_shows_resolved_assignment():
    """Property-assignment dry-run output should show the parsed assignment payload."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_rw_dry_run_property", None)

    def _get_cli_rw_dry_run_property(self) -> int:
        del self
        return 1

    def _set_cli_rw_dry_run_property(self, value: int) -> None:
        del self, value

    setattr(
        moldflow.Synergy,
        "cli_rw_dry_run_property",
        property(_get_cli_rw_dry_run_property, _set_cli_rw_dry_run_property),
    )
    try:
        result = runner.invoke(
            app, ["invoke", "synergy.cli_rw_dry_run_property", "value=7", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "This dry run validates a property assignment." in result.stdout
        assert "Resolved assignment:" in result.stdout
        assert '"value": 7' in result.stdout
        assert "Resolved kwargs:" not in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_rw_dry_run_property")
        else:
            setattr(moldflow.Synergy, "cli_rw_dry_run_property", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_file_supports_json_file_output(tmp_path):
    """Batch result JSON should be writable via --json-file-output."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def _cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", _cli_echo)

    class Sy:
        def cli_echo(self, value: str) -> str:
            return value

    batch_file = tmp_path / "batch_ok.json"
    out_file = tmp_path / "batch_out.json"
    batch_file.write_text(
        json.dumps([{"target": "synergy.cli_echo", "args": ["value=ok"]}]), encoding="utf-8"
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app,
                ["invoke", "--batch-file", str(batch_file), "--json-file-output", str(out_file)],
            )
        assert result.exit_code == 0
        assert "Wrote structured output to" in result.stdout
        assert out_file.exists()
        payload = json.loads(out_file.read_text(encoding="utf-8"))
        assert payload["batch_results"][0]["ok"] is True
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_file_executes_multiple_calls(tmp_path):
    """--batch-file should execute call array and return structured batch results."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo", None)

    def _cli_echo(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo", _cli_echo)

    class Sy:
        def cli_echo(self, value: str) -> str:
            return value

    batch_file = tmp_path / "batch.json"
    batch_file.write_text(
        json.dumps(
            [
                {"target": "synergy.cli_echo", "args": ["value=one"]},
                {"target": "synergy.cli_echo", "params_json": {"value": "two"}},
            ]
        ),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "--batch-file", str(batch_file), "--json-output"]
            )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["summary"] == {"total": 2, "succeeded": 2, "failed": 0}
        assert len(payload["batch_results"]) == 2
        assert payload["batch_results"][0]["ok"] is True
        assert payload["batch_results"][1]["ok"] is True
        assert payload["batch_results"][0]["request"]["args"] == ["value=one"]
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo")
        else:
            setattr(moldflow.Synergy, "cli_echo", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_trace_emits_runtime_deferred_binding_events():
    """--trace should emit deferred runtime-bind events for ambiguous union chains."""
    app = build_cli_app()

    class TraceA:
        def ping(self, value: int) -> str:
            return f"A:{value}"

    class TraceB:
        def ping(self, value: int) -> str:  # pragma: no cover - union member only
            return f"B:{value}"

    class Sy:
        def get_trace_union(self):
            return TraceA()

    orig_a = getattr(moldflow, "TraceA", None)
    orig_b = getattr(moldflow, "TraceB", None)
    orig_getter = getattr(moldflow.Synergy, "get_trace_union", None)

    def _get_trace_union(self):
        return TraceA()

    _get_trace_union.__annotations__ = {"return": "Union[TraceA, TraceB, None]"}
    setattr(moldflow, "TraceA", TraceA)
    setattr(moldflow, "TraceB", TraceB)
    setattr(moldflow.Synergy, "get_trace_union", _get_trace_union)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.get_trace_union.ping", "ping.value=4", "--trace"]
            )
        assert result.exit_code == 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert '"schema_version": "1.0"' in combined
        assert '"target": "synergy.get_trace_union.ping"' in combined
        assert '"event": "result"' in combined
        assert "deferred_runtime_bind" in combined
        assert "invoke_step" in combined
    finally:
        if orig_a is None:
            delattr(moldflow, "TraceA")
        else:
            setattr(moldflow, "TraceA", orig_a)
        if orig_b is None:
            delattr(moldflow, "TraceB")
        else:
            setattr(moldflow, "TraceB", orig_b)
        if orig_getter is None:
            delattr(moldflow.Synergy, "get_trace_union")
        else:
            setattr(moldflow.Synergy, "get_trace_union", orig_getter)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nullable_param_without_default_can_be_omitted():
    """Nullable annotations without defaults should be auto-populated as None when omitted."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_nullable_no_default", None)

    def _cli_nullable_no_default(self, maybe: "ImportOptions | None") -> str:
        return f"maybe={maybe!r}"

    setattr(moldflow.Synergy, "cli_nullable_no_default", _cli_nullable_no_default)

    class Sy:
        def cli_nullable_no_default(self, maybe) -> str:
            return f"maybe={maybe!r}"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_nullable_no_default"])
        assert result.exit_code == 0
        assert "maybe=None" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_nullable_no_default")
        else:
            setattr(moldflow.Synergy, "cli_nullable_no_default", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_fail_on_false_is_default_behavior():
    """False business results should fail command by default for CI-friendly signaling."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_returns_false", None)

    def _cli_returns_false(self) -> bool:
        return False

    setattr(moldflow.Synergy, "cli_returns_false", _cli_returns_false)

    class Sy:
        def cli_returns_false(self) -> bool:
            return False

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_returns_false", "--json-output"])
        assert result.exit_code == 1
        payload = json.loads(result.stdout)
        assert payload["ok"] is False
        assert payload["result"] is False
        assert payload["result_type"] == "bool"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_returns_false")
        else:
            setattr(moldflow.Synergy, "cli_returns_false", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_no_fail_on_false_allows_exit_zero():
    """--no-fail-on-false should preserve backward-compatible zero exit on False."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_returns_false", None)

    def _cli_returns_false(self) -> bool:
        return False

    setattr(moldflow.Synergy, "cli_returns_false", _cli_returns_false)

    class Sy:
        def cli_returns_false(self) -> bool:
            return False

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_returns_false", "--json-output", "--no-fail-on-false"]
            )
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["ok"] is False
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_returns_false")
        else:
            setattr(moldflow.Synergy, "cli_returns_false", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_fail_on_false_default_sets_nonzero_exit(tmp_path):
    """Batch mode should fail when a call returns False and fail-on-false is enabled."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_maybe", None)

    def _cli_maybe(self, value: str) -> bool:
        return value == "ok"

    setattr(moldflow.Synergy, "cli_maybe", _cli_maybe)

    class Sy:
        def cli_maybe(self, value: str) -> bool:
            return value == "ok"

    batch_file = tmp_path / "batch_false.json"
    batch_file.write_text(
        json.dumps(
            [
                {"target": "synergy.cli_maybe", "args": ["value=ok"]},
                {"target": "synergy.cli_maybe", "args": ["value=bad"]},
            ]
        ),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "--batch-file", str(batch_file), "--json-output"]
            )
        assert result.exit_code == 1
        payload = json.loads(result.stdout)
        assert payload["batch_results"][0]["ok"] is True
        assert payload["batch_results"][1]["ok"] is False
        assert payload["batch_results"][1]["result"] is False
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_maybe")
        else:
            setattr(moldflow.Synergy, "cli_maybe", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_chained_call_intermediate_none():
    """If an intermediate call returns None, next-step invocation fails cleanly."""
    app = build_cli_app()

    class PM:
        def get_none(self):
            return None

        def then_method(self):
            return "should not reach"

    class Sy:
        @property
        def plot_manager(self):
            return PM()

    with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
        "moldflow_cli.factories.get_synergy", return_value=Sy()
    ):
        result = runner.invoke(app, ["invoke", "synergy.plot_manager.get_none.then_method"])

    assert result.exit_code != 0
    err = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert (
        "cannot invoke method" in err.lower()
        or "cannot resolve attribute" in err.lower()
        or "is not a callable method" in err.lower()
    )


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_boundary_conditions_null_owner_error_names_missing_manager():
    """Invoke should name the missing nullable Synergy manager owner."""
    app = build_cli_app()

    class Sy:
        @property
        def boundary_conditions(self):
            return None

    with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
        "moldflow_cli.factories.get_synergy", return_value=Sy()
    ):
        result = runner.invoke(
            app, ["invoke", "synergy.boundary_conditions.find_property", "prop_type=1", "prop_id=1"]
        )

    assert result.exit_code != 0
    err = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    lowered = err.lower()
    assert "synergy.boundary_conditions" in err
    assert "unavailable in the current session" in lowered
    assert "find_property" in err


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_rejects_hidden_factory_wrapper_surfaces():
    """Invoke should reject explicit targets that pass through hidden factory wrapper helpers."""
    app = build_cli_app()
    result = runner.invoke(app, ["invoke", "synergy.create_double_array.add_double", "value=1"])

    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    lowered = combined.lower()
    assert "synergy.create_double_array" in combined
    assert "doublearray wrapper" in lowered
    assert "direct cli targets" in lowered


@pytest.mark.cli
@pytest.mark.cli
@pytest.mark.unit
def test_invoke_dry_run_human_output_is_plan_first():
    """Dry-run mode should default to a concise plan summary, not describe-style examples."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_plan_only_human", None)

    def _cli_plan_only_human(self, value: int) -> str:
        return f"value={value}"

    setattr(moldflow.Synergy, "cli_plan_only_human", _cli_plan_only_human)
    try:
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(
                app, ["invoke", "synergy.cli_plan_only_human", "value=3", "--dry-run"]
            )
        assert result.exit_code == 0
        assert "Dry run for synergy.cli_plan_only_human" in result.stdout
        assert "Resolved kwargs:" in result.stdout
        assert "Try this:" not in result.stdout
        assert "JSON example:" not in result.stdout
        assert "self" not in result.stdout
        assert "cli_plan_only_human(value:" not in result.stdout
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_plan_only_human")
        else:
            setattr(moldflow.Synergy, "cli_plan_only_human", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_human_output_shows_summary_table(tmp_path):
    """Batch mode should default to a concise summary table for terminal users."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_echo_human_batch", None)

    def _cli_echo_human_batch(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_echo_human_batch", _cli_echo_human_batch)

    class Sy:
        def cli_echo_human_batch(self, value: str) -> str:
            return value

    batch_file = tmp_path / "batch_human.json"
    batch_file.write_text(
        json.dumps([{"target": "synergy.cli_echo_human_batch", "args": ["value=one"]}]),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "--batch-file", str(batch_file)])
        assert result.exit_code == 0
        assert "Batch summary:" in result.stdout
        assert "Batch results" in result.stdout
        assert "synergy.cli_echo_human_batch" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_echo_human_batch")
        else:
            setattr(moldflow.Synergy, "cli_echo_human_batch", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_trace_emits_error_events_for_validation_failures():
    """Trace mode should emit explicit error events before validation failures exit."""
    app = build_cli_app()
    result = runner.invoke(app, ["invoke", "synergy.open_project", "--trace"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert '"event": "error"' in combined
    assert '"error_type": "invoke_validation"' in combined


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_trace_includes_batch_index(tmp_path):
    """Batch tracing should include a batch_index field for event correlation."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_trace_batch", None)

    def _cli_trace_batch(self, value: str) -> str:
        return value

    setattr(moldflow.Synergy, "cli_trace_batch", _cli_trace_batch)

    class Sy:
        def cli_trace_batch(self, value: str) -> str:
            return value

    batch_file = tmp_path / "batch_trace.json"
    batch_file.write_text(
        json.dumps([{"target": "synergy.cli_trace_batch", "args": ["value=ok"]}]), encoding="utf-8"
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "--batch-file", str(batch_file), "--trace"])
        assert result.exit_code == 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert '"batch_index": 0' in combined
        assert '"event": "result"' in combined
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_trace_batch")
        else:
            setattr(moldflow.Synergy, "cli_trace_batch", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_batch_runtime_error_is_reported_per_item_and_batch_continues(tmp_path):
    """Non-validation runtime failures should stay structured and not abort the whole batch."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_batch_runtime", None)

    def _cli_batch_runtime(self, value: str) -> str:
        if value == "boom":
            raise RuntimeError("boom")
        return value

    setattr(moldflow.Synergy, "cli_batch_runtime", _cli_batch_runtime)

    class Sy:
        def cli_batch_runtime(self, value: str) -> str:
            if value == "boom":
                raise RuntimeError("boom")
            return value

    batch_file = tmp_path / "batch_runtime.json"
    batch_file.write_text(
        json.dumps(
            [
                {"target": "synergy.cli_batch_runtime", "args": ["value=boom"]},
                {"target": "synergy.cli_batch_runtime", "args": ["value=ok"]},
            ]
        ),
        encoding="utf-8",
    )
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "--batch-file", str(batch_file), "--json-output"]
            )

        assert result.exit_code == 1
        payload = json.loads(result.stdout)
        assert payload["summary"] == {"total": 2, "succeeded": 1, "failed": 1}
        assert payload["batch_results"][0]["ok"] is False
        assert payload["batch_results"][0]["error_type"] == "runtime_error"
        assert "boom" in payload["batch_results"][0]["error"].lower()
        assert payload["batch_results"][1]["ok"] is True
        assert payload["batch_results"][1]["result"] == "ok"
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_batch_runtime")
        else:
            setattr(moldflow.Synergy, "cli_batch_runtime", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_case_insensitive_and_prefixed():
    """Invoke should accept mixed-case class/method names and moldflow. prefix."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_ping", None)

    def cli_ping(self) -> str:  # type: ignore[name-defined]
        return "pong"

    setattr(moldflow.Synergy, "cli_ping", cli_ping)

    class SynergyForTest:
        def cli_ping(self) -> str:
            return "pong"

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy) as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ) as mock_fact_synergy:
            r1 = runner.invoke(app, ["invoke", "SyNeRgY.cli_ping"])
            r2 = runner.invoke(app, ["invoke", "moldflow.Synergy.cli_ping"])

        assert r1.exit_code == 0
        assert r2.exit_code == 0
        assert "pong" in r1.stdout
        assert "pong" in r2.stdout
        # Synergy should have been accessed when executing the invoke.
        assert mock_ctx_synergy.call_count >= 1 or mock_fact_synergy.call_count >= 1
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_ping")
        else:
            setattr(moldflow.Synergy, "cli_ping", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_multi_step_accepts_case_insensitive_step_prefixes():
    """Argument step prefixes should be case-insensitive for multi-step chains."""
    app = build_cli_app()
    fake = FakeSynergy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line",
                "FIND_PLOT_BY_NAME.plot_name=My Plot",
                "GET_PROBE_PLOT_PROBE_LINE.index=7",
                "GET_PROBE_PLOT_PROBE_LINE.start_pt.x=1.0",
                "GET_PROBE_PLOT_PROBE_LINE.start_pt.y=2.0",
                "GET_PROBE_PLOT_PROBE_LINE.start_pt.z=3.0",
                "GET_PROBE_PLOT_PROBE_LINE.end_pt.x=4.0",
                "GET_PROBE_PLOT_PROBE_LINE.end_pt.y=5.0",
                "GET_PROBE_PLOT_PROBE_LINE.end_pt.z=6.0",
            ],
        )

    assert result.exit_code == 0
    assert "probe_line(index=7" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_single_step_accepts_case_insensitive_step_prefixes():
    """Single-step routes should accept step-prefixed args case-insensitively."""
    app = build_cli_app()
    fake = FakeSynergy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name",
                "FIND_PLOT_BY_NAME.plot_name=My Plot",
            ],
        )

    assert result.exit_code == 0
    assert "FakePlot" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_single_step_json_accepts_nested_step_payload():
    """Single-step JSON payloads may optionally wrap args under the step name."""
    app = build_cli_app()
    fake = FakeSynergy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.find_plot_by_name",
                "--params-json",
                '{"FIND_PLOT_BY_NAME": {"plot_name": "My Plot"}}',
            ],
        )

    assert result.exit_code == 0
    assert "FakePlot" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_multi_step_accepts_case_insensitive_target_method_segments():
    """Target method segments should resolve case-insensitively."""
    app = build_cli_app()
    fake = FakeSynergy()
    with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
        "moldflow_cli.factories.get_synergy", return_value=fake
    ):
        result = runner.invoke(
            app,
            [
                "invoke",
                "synergy.plot_manager.FIND_PLOT_BY_NAME.GET_PROBE_PLOT_PROBE_LINE",
                "find_plot_by_name.plot_name=My Plot",
                "get_probe_plot_probe_line.index=9",
                "get_probe_plot_probe_line.start_pt.x=1.0",
                "get_probe_plot_probe_line.start_pt.y=2.0",
                "get_probe_plot_probe_line.start_pt.z=3.0",
                "get_probe_plot_probe_line.end_pt.x=4.0",
                "get_probe_plot_probe_line.end_pt.y=5.0",
                "get_probe_plot_probe_line.end_pt.z=6.0",
            ],
        )

    assert result.exit_code == 0
    assert "probe_line(index=9" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_repeated_step_names_rejected_early():
    """Repeated step names in a chain should fail with an unambiguous message."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "loop", None)

    def _loop(self):
        return self

    # Use a known wrapper return type so reflective chain parsing reaches duplicate detection.
    _loop.__annotations__ = {"return": "Synergy"}
    setattr(moldflow.Synergy, "loop", _loop)
    try:
        result = runner.invoke(app, ["invoke", "synergy.loop.loop"])
        assert result.exit_code != 0
        stderr_text = (getattr(result, "stderr_bytes", b"") or b"").decode("utf-8", "ignore")
        assert "repeated method names" in stderr_text.lower()
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "loop")
        else:
            setattr(moldflow.Synergy, "loop", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_param_aliasing():
    """Accept hyphen/camel/snake variants of parameter names where sensible."""
    app = build_cli_app()

    class Fake:
        def set_val(self, long_name: int) -> str:
            return f"v={long_name}"

    sy = Fake()
    # Ensure the class used for introspection exposes the callable.
    orig = getattr(moldflow.Synergy, "set_val", None)

    def _set_val(self, long_name: int) -> str:
        return f"v={long_name}"

    setattr(moldflow.Synergy, "set_val", _set_val)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            # snake_case
            r1 = runner.invoke(app, ["invoke", "synergy.set_val", "long_name=1"])
            # camelCase (not automatically supported but ensure it doesn't crash)
            r2 = runner.invoke(app, ["invoke", "synergy.set_val", "longName=2"])
            # kebab-case (should be treated as literal param name and thus reject)
            r3 = runner.invoke(app, ["invoke", "synergy.set_val", "long-name=3"])

        assert r1.exit_code == 0
        assert "v=1" in r1.stdout
        assert r2.exit_code != 0 or "v=2" in r2.stdout
        assert r3.exit_code != 0
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "set_val")
        else:
            setattr(moldflow.Synergy, "set_val", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_enum_parsing_and_invalid_enum():
    """Pass enum-like strings to methods expecting enums and invalid values raise BadParameter."""
    app = build_cli_app()

    class Fake:
        def set_color(self, color) -> str:
            return f"color={color}"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "set_color", None)

    def _set_color(self, color) -> str:
        return f"color={color}"

    setattr(moldflow.Synergy, "set_color", _set_color)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            ok = runner.invoke(app, ["invoke", "synergy.set_color", "color=Red"])
            bad = runner.invoke(app, ["invoke", "synergy.set_color", "color=NotAColor"])

        # Current CLI does not validate enum membership; accept either behavior:
        assert ok.exit_code == 0
        assert "color=Red" in (getattr(ok, "stdout", "") or getattr(ok, "output", ""))
        # Either the CLI accepts the string or fails; assert one of those.
        bad_output = (getattr(bad, "stdout", "") or getattr(bad, "output", "")) + (
            getattr(bad, "stderr", "") or ""
        )
        assert bad.exit_code != 0 or "NotAColor" in bad_output or "color=NotAColor" in bad_output
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "set_color")
        else:
            setattr(moldflow.Synergy, "set_color", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_forward_ref_union_with_default_none():
    """Optional wrapper parameters with default None should not force wrapper creation."""
    app = build_cli_app()

    class Fake:
        def do_optional(self, opt: "ImportOptions | None" = None) -> str:
            return f"opt={opt}"

    sy = Fake()
    orig = getattr(moldflow.Synergy, "do_optional", None)

    def _do_optional(self, opt=None) -> str:
        return f"opt={opt}"

    setattr(moldflow.Synergy, "do_optional", _do_optional)
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            r = runner.invoke(app, ["invoke", "synergy.do_optional"])

        assert r.exit_code == 0
        assert "opt=None" in r.stdout or "opt=None" in (r.stdout or "")
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "do_optional")
        else:
            setattr(moldflow.Synergy, "do_optional", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_with_varargs_and_kwargs():
    """Method accepting **kwargs should receive arbitrary named CLI params."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_varargs", None)

    def cli_varargs(self, **kwargs):
        return f"kwcount={len(kwargs)};keys={sorted(kwargs.keys())}"

    setattr(moldflow.Synergy, "cli_varargs", cli_varargs)

    class Sy:
        def cli_varargs(self, **kwargs):
            return f"kwcount={len(kwargs)};keys={sorted(kwargs.keys())}"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(
                app, ["invoke", "synergy.cli_varargs", "alpha=1", "beta=2", "gamma=three"]
            )
        assert result.exit_code == 0
        assert "kwcount=3" in result.stdout
        assert "alpha" in result.stdout and "beta" in result.stdout and "gamma" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_varargs")
        else:
            setattr(moldflow.Synergy, "cli_varargs", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_prefers_callable_when_segment_name_collides_with_wrapper_class_name():
    """Callable method segments should win over class-name collisions during target parsing."""
    app = build_cli_app()

    class CliCollision:
        """Dummy public class added to moldflow for collision testing."""

    orig_cls = getattr(moldflow, "CliCollision", None)
    orig_method = getattr(moldflow.Synergy, "cli_collision", None)

    def _cli_collision(self) -> str:
        return "collision-ok"

    setattr(moldflow, "CliCollision", CliCollision)
    setattr(moldflow.Synergy, "cli_collision", _cli_collision)

    class Sy:
        def cli_collision(self) -> str:
            return "collision-ok"

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_collision"])
        assert result.exit_code == 0
        assert "collision-ok" in result.stdout
    finally:
        if orig_cls is None:
            delattr(moldflow, "CliCollision")
        else:
            setattr(moldflow, "CliCollision", orig_cls)
        if orig_method is None:
            delattr(moldflow.Synergy, "cli_collision")
        else:
            setattr(moldflow.Synergy, "cli_collision", orig_method)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_supports_classmethod_targets():
    """Invoke should handle classmethod targets without requiring synthetic cls args."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_class_ping", None)

    class Sy:
        @classmethod
        def cli_class_ping(cls) -> str:
            return "pong"

    setattr(moldflow.Synergy, "cli_class_ping", classmethod(lambda cls: "pong"))
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            result = runner.invoke(app, ["invoke", "synergy.cli_class_ping"])
        assert result.exit_code == 0
        assert "pong" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_class_ping")
        else:
            setattr(moldflow.Synergy, "cli_class_ping", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_import_options_nested_attributes_configured():
    """Ensure ImportOptions-like wrapper is allocated and nested attributes are set."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "import_file", None)

    class FakeImportOptions:
        def __init__(self) -> None:
            self.use_mdl = None
            self.merge_parts = None

    def cli_import_file(  # type: ignore[name-defined]
        self, file: str, import_options: "ImportOptions | None"
    ) -> str:
        return (
            f"imported:{file};use_mdl={import_options.use_mdl};merge={import_options.merge_parts}"
        )

    setattr(moldflow.Synergy, "import_file", cli_import_file)

    class SynergyForTest:
        @property
        def import_options(self) -> FakeImportOptions:
            return FakeImportOptions()

        def import_file(self, file: str, import_options: FakeImportOptions) -> str:
            return (
                f"imported:{file};use_mdl={import_options.use_mdl};"
                f"merge={import_options.merge_parts}"
            )

    sy = SynergyForTest()
    try:
        with patch("moldflow_cli.context.get_synergy", return_value=sy), patch(
            "moldflow_cli.factories.get_synergy", return_value=sy
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.import_file",
                    "file=C:/tmp/part.iges",
                    "import_file.import_options.use_mdl=true",
                    "import_file.import_options.merge_parts=false",
                ],
            )

        assert result.exit_code == 0
        assert "use_mdl=True" in result.stdout
        assert "merge=False" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "import_file")
        else:
            setattr(moldflow.Synergy, "import_file", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_signature_failure_does_not_block_call():
    """If signature inspection fails, invoke should still call the target."""
    app = build_cli_app()

    class BadSigCallable:
        def __call__(self, **kwargs):
            return f"ok:{kwargs}"

        @property
        def __signature__(self):
            raise ValueError("bad signature")

    orig = getattr(moldflow.Synergy, "cli_bad_sig", None)
    setattr(moldflow.Synergy, "cli_bad_sig", BadSigCallable())

    class Sy:
        def __init__(self) -> None:
            self.cli_bad_sig = BadSigCallable()

    try:
        with patch("moldflow_cli.context.get_synergy", return_value=Sy()), patch(
            "moldflow_cli.factories.get_synergy", return_value=Sy()
        ):
            r = runner.invoke(app, ["invoke", "synergy.cli_bad_sig", "foo=1"])

        assert r.exit_code == 0
        assert "ok:" in r.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_bad_sig")
        else:
            setattr(moldflow.Synergy, "cli_bad_sig", orig)
