# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused describe command tests for moldflow CLI."""

from __future__ import annotations

# Test module uses small inline doubles for targeted behavior checks.
# pylint: disable=too-few-public-methods,too-many-lines

from unittest.mock import patch
import importlib.util
import json

import pytest
from typer.testing import CliRunner
import moldflow

from moldflow_cli.commands import build_cli_app
from moldflow_cli import target_resolution

runner = CliRunner()


def _has_yaml() -> bool:
    return importlib.util.find_spec("yaml") is not None


@pytest.mark.cli
@pytest.mark.unit
def test_iter_static_members_falls_back_without_getmembers_static():
    """Static member lookup should stay descriptor-safe on Python 3.10."""

    class ExplosiveDescriptor:
        """Descriptor used to verify the fallback does not execute descriptors."""

        def __get__(self, obj, owner=None):
            raise RuntimeError("descriptor should not execute during static lookup")

    class CliExplosive:
        """Class containing a descriptor and regular method for static lookup tests."""

        danger = ExplosiveDescriptor()

        def safe_method(self) -> str:
            """Simple method used to confirm regular members are still returned."""
            return "ok"

    with patch.object(
        target_resolution.inspect,
        "getmembers_static",
        create=True,
        side_effect=AttributeError("getmembers_static unavailable"),
    ):
        members = dict(target_resolution.iter_static_members(CliExplosive))

    assert "danger" in members
    assert "safe_method" in members
    assert isinstance(members["danger"], ExplosiveDescriptor)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_case_insensitive_and_prefixed():
    """Ensure describe is case-insensitive and accepts 'moldflow.' prefixes."""
    app = build_cli_app()

    with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
        "moldflow_cli.factories.get_synergy"
    ) as mock_fact_synergy:
        result_mixed = runner.invoke(app, ["describe", "SyNeRgY.NeW_PrOjEcT"])
        result_prefixed = runner.invoke(app, ["describe", "moldflow.Synergy.new_project"])

    # Neither call should touch Synergy/COM.
    mock_ctx_synergy.assert_not_called()
    mock_fact_synergy.assert_not_called()
    assert result_mixed.exit_code == 0
    assert result_prefixed.exit_code == 0


@pytest.mark.cli
@pytest.mark.unit
def test_describe_multi_step_signature_rendering():
    """Describe on a chained target should show signatures for each step (introspection only)."""
    app = build_cli_app()
    res = runner.invoke(app, ["describe", "plot_manager.find_plot_by_name"])
    assert res.exit_code == 0
    assert "find_plot_by_name" in res.stdout or "plot_manager" in res.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_help_and_describe_show_snake_case_targets():
    """Ensure help for `describe` shows snake_case example targets."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "--help"])
    assert result.exit_code == 0
    assert "synergy.new_project" in result.stdout
    lowered = result.stdout.lower()
    assert "structured invoke template" in lowered or "examples" in lowered


@pytest.mark.cli
@pytest.mark.unit
def test_list_help_mentions_type_and_describe_first_guidance():
    """List help should advertise discovery-first guidance for first-time users."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    lowered = result.stdout.lower()
    assert "discover invokable targets" in lowered
    assert "next command" in lowered
    assert "wildcard" in lowered


@pytest.mark.cli
@pytest.mark.unit
@pytest.mark.skipif(not _has_yaml(), reason="PyYAML not installed")
def test_describe_yaml_output():
    """Describe should emit YAML when requested."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project", "--yaml"])
    assert result.exit_code == 0
    assert "signature" in result.stdout or "params" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_multiple_targets_human_output():
    """Describe should accept multiple targets and render each target block in order."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.new_project", "synergy.open_project"])
    assert result.exit_code == 0
    assert "synergy.new_project" in result.stdout
    assert "synergy.open_project(path: str)" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_multiple_targets_json_output_emits_list_payload():
    """Structured describe should emit a list payload when multiple targets are requested."""
    app = build_cli_app()
    result = runner.invoke(
        app, ["describe", "synergy.new_project", "synergy.open_project", "--json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert [item["target"] for item in payload] == ["synergy.new_project", "synergy.open_project"]
    assert payload[0]["schema_version"] == payload[1]["schema_version"]


@pytest.mark.cli
@pytest.mark.unit
def test_describe_rejects_unresolvable_chained_target_suffix():
    """Describe should fail when extra chained segments cannot be resolved."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project.nonexistent_tail"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    lowered = combined.lower()
    assert "has no attribute" in lowered or all(
        token in lowered for token in ("returns", "non-wrapper", "value")
    )
    assert all(token in lowered for token in ("cannot", "continue", "nonexistent_tail"))


@pytest.mark.cli
@pytest.mark.unit
def test_describe_rejects_empty_target_segment():
    """Describe should reject malformed dotted targets with empty segments."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy..open_project"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "empty path segment" in combined.lower()


@pytest.mark.cli
@pytest.mark.unit
def test_describe_rejects_invalid_target_identifier_segment():
    """Describe should reject target segments that are not valid identifiers."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open-project"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "must be a valid identifier" in combined.lower()


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_handles_uninspectable_signature():
    """Describe --json should not crash when inspect.signature fails."""
    app = build_cli_app()

    class BadSigCallable:
        """Callable object whose signature introspection fails."""

        @property
        def __signature__(self):
            raise ValueError("bad signature")

        def __call__(self, *args, **kwargs):  # pragma: no cover - not invoked here
            return None

    orig = getattr(moldflow.Synergy, "cli_bad_sig_describe", None)
    setattr(moldflow.Synergy, "cli_bad_sig_describe", BadSigCallable())
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_bad_sig_describe", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["target"] == "synergy.cli_bad_sig_describe"
        assert payload["params"] == []
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_bad_sig_describe")
        else:
            setattr(moldflow.Synergy, "cli_bad_sig_describe", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_on_property_returns_structured_payload():
    """Structured describe should not fail on non-callable properties."""

    class CLITestDummy:
        """Test dummy class for describe command."""

        @property
        def foobar(self) -> str:
            """Example property."""
            return "bar"

    orig_cls = getattr(moldflow, "CLITestDummy", None)
    setattr(moldflow, "CLITestDummy", CLITestDummy)
    app = build_cli_app()
    try:
        result = runner.invoke(app, ["describe", "CLITestDummy.foobar", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["signature"] is None
        assert payload["type"] == "property"
        assert payload["summary"] == "Example property."
        assert "details" not in payload
    finally:
        if orig_cls is None:
            delattr(moldflow, "CLITestDummy")
        else:
            setattr(moldflow, "CLITestDummy", orig_cls)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_settable_property_json_exposes_synthetic_value_param():
    """Settable property JSON should include synthetic 'value' param metadata for clarity."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.study_doc.mesh_type", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    params = payload.get("params", [])
    assert isinstance(params, list)
    assert any(
        isinstance(param, dict) and param.get("name") == "value" and param.get("synthetic") is True
        for param in params
    )


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_preserves_docstring_markup_like_text():
    """Structured describe output must not interpret rich-like markup tokens."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_markup_doc", None)

    def cli_markup_doc(self):
        """Literal doc with [bold]tokens[/bold] should round-trip unchanged."""
        del self

    setattr(moldflow.Synergy, "cli_markup_doc", cli_markup_doc)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_markup_doc", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert (
            payload["summary"]
            == "Literal doc with [bold]tokens[/bold] should round-trip unchanged."
        )
        assert "details" not in payload
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_markup_doc")
        else:
            setattr(moldflow.Synergy, "cli_markup_doc", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_omits_empty_paren_signature_for_zero_arg_methods():
    """Structured describe should not emit a bare empty-paren signature for zero-arg callables."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_zero_arg_doc", None)

    def cli_zero_arg_doc(self) -> str:
        """Create a sentinel value."""
        del self
        return "ok"

    setattr(moldflow.Synergy, "cli_zero_arg_doc", cli_zero_arg_doc)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_zero_arg_doc", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["signature"] is None
        assert payload["returns"] == "str"
        assert payload["summary"] == "Create a sentinel value."
        assert payload["params"] == []
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_zero_arg_doc")
        else:
            setattr(moldflow.Synergy, "cli_zero_arg_doc", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_flattens_multiline_docstrings():
    """Structured describe output should not contain embedded newline escapes in doc text."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_multiline_doc", None)

    def cli_multiline_doc(self):
        """Show the given plot.

        Args:
            plot (Plot | None): The plot to show.
        """
        del self

    setattr(moldflow.Synergy, "cli_multiline_doc", cli_multiline_doc)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_multiline_doc", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert "\n" not in payload["summary"]
        assert payload["summary"] == "Show the given plot."
        assert payload["details"] == "Args: plot (Plot | None): The plot to show."
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_multiline_doc")
        else:
            setattr(moldflow.Synergy, "cli_multiline_doc", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_schema_emits_json_schema_like_contract():
    """describe --schema should emit required/properties payload."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project", "--schema"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["type"] == "object"
    assert "properties" in payload and "required" in payload
    assert "path" in payload["properties"]


@pytest.mark.cli
@pytest.mark.unit
def test_describe_schema_is_mutually_exclusive_with_json_and_yaml():
    """describe --schema should be exclusive with --json/--yaml."""
    app = build_cli_app()
    r1 = runner.invoke(app, ["describe", "synergy.open_project", "--schema", "--json"])
    r2 = runner.invoke(app, ["describe", "synergy.open_project", "--schema", "--yaml"])
    assert r1.exit_code != 0
    assert r2.exit_code != 0


@pytest.mark.cli
@pytest.mark.unit
def test_describe_trims_target_whitespace_before_resolution():
    """Describe should normalize leading/trailing spaces in target input."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", " synergy.open_project "])
    assert result.exit_code == 0
    assert "synergy.open_project" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_json_includes_invoke_examples_and_template():
    """Structured describe should show the preferred invoke form and params-json shape."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    invoke_examples = payload.get("invoke_examples")
    assert isinstance(invoke_examples, dict)
    assert payload.get("signature") == "(path: str)"
    assert payload.get("returns") == "bool"
    assert payload.get("summary")
    assert invoke_examples.get("cli_command") == "invoke synergy.open_project path=<path>"
    assert payload.get("next_command") == "invoke synergy.open_project path=<path>"
    assert payload.get("params_json_template", {}).get("path") is None
    assert invoke_examples.get("params_json", {}).get("path") == "<path>"
    assert "kind" not in payload["params"][0]


@pytest.mark.cli
@pytest.mark.unit
def test_describe_yaml_avoids_anchor_noise_in_invoke_examples():
    """YAML describe output should not emit anchors for duplicated invoke example payloads."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project", "--yaml"])
    assert result.exit_code == 0
    assert "&id" not in result.stdout
    assert "*id" not in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_omits_receiver_params_from_human_and_json_output():
    """Describe output should hide Python receiver parameters such as self/cls."""
    app = build_cli_app()

    human = runner.invoke(app, ["describe", "synergy.new_project"])
    structured = runner.invoke(app, ["describe", "synergy.new_project", "--json"])

    assert human.exit_code == 0
    assert structured.exit_code == 0
    assert "(self" not in human.stdout
    payload = json.loads(structured.stdout)
    assert "self" not in payload["signature"]
    assert payload.get("returns") == "bool"
    assert all(param["name"] != "self" for param in payload["params"])


@pytest.mark.cli
@pytest.mark.unit
def test_describe_human_output_includes_examples():
    """Human describe output should show the preferred invoke command and JSON shape."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "synergy.open_project"])
    assert result.exit_code == 0
    assert "Try this:" in result.stdout
    assert "JSON example:" in result.stdout
    assert "synergy.open_project(path: str)" in result.stdout
    assert "-> None" not in result.stdout
    assert "invoke synergy.open_project path=<path>" in result.stdout
    assert '"path": "<path>"' in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_human_output_includes_wrapper_input_hints():
    """Describe should surface wrapper-specific JSON and non-JSON input guidance directly."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels", None)

    def cli_accept_levels(self, levels: "DoubleArray | None") -> str:
        """Return a simple sentinel for wrapper-hint coverage."""
        del self, levels
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels", cli_accept_levels)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_accept_levels"])
        assert result.exit_code == 0
        assert "Input hints:" in result.stdout
        assert "levels (DoubleArray):" in result.stdout
        assert "JSON value:" in result.stdout
        assert "CLI argument: levels=1.0,2.5" in result.stdout
        assert '"levels": {' in result.stdout
        assert '"values": [' in result.stdout
        assert "levels=1.0,2.5" in result.stdout
        assert "levels.values=1.0,2.5" in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_wrapper_input_hints_normalize_alias_annotations_to_canonical_name():
    """Describe should normalize alias annotations to canonical wrapper names."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_accept_levels_alias", None)

    def cli_accept_levels_alias(self, levels: "double_array | None") -> str:
        """Return a simple sentinel for alias-normalization coverage."""
        del self, levels
        return "ok"

    setattr(moldflow.Synergy, "cli_accept_levels_alias", cli_accept_levels_alias)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_accept_levels_alias"])
        assert result.exit_code == 0
        assert "levels (DoubleArray):" in result.stdout
        assert "levels (double_array):" not in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_accept_levels_alias")
        else:
            setattr(moldflow.Synergy, "cli_accept_levels_alias", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_human_output_includes_minimal_examples_when_they_differ():
    """Describe should surface both preferred and minimal examples when both are useful."""
    app = build_cli_app()

    orig = getattr(moldflow.Synergy, "cli_optional_describe", None)

    def cli_optional_describe(self, required_name: str, dataset_name: str | None = None) -> str:
        """Return a simple sentinel for describe example coverage."""
        del self, required_name, dataset_name
        return "ok"

    setattr(moldflow.Synergy, "cli_optional_describe", cli_optional_describe)
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_optional_describe"])
        assert result.exit_code == 0
        assert "Try this:" in result.stdout
        assert "Shorter form:" in result.stdout
        assert "dataset_name=<dataset_name>" in result.stdout
        assert '"required_name": "<required_name>"' in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_optional_describe")
        else:
            setattr(moldflow.Synergy, "cli_optional_describe", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_human_output_uses_concise_wrapper_type_names_and_omits_bare_minimal_form():
    """Describe should keep wrapper names concise and hide bare minimal examples."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "boundary_conditions.create_edge_loads"])
    assert result.exit_code == 0
    normalized = " ".join(result.stdout.split())
    assert (
        "synergy.boundary_conditions.create_edge_loads(nodes: EntList | None, force: Vector | None)"
        in normalized
    )
    assert "moldflow.ent_list.EntList" not in result.stdout
    assert "moldflow.vector.Vector" not in result.stdout
    assert "Shorter form:" not in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_rejects_hidden_transient_wrapper_factory_targets():
    """Describe should reject wrapper-factory helpers hidden by library CLI metadata."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "boundary_conditions.create_entity_list"])

    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    lowered = combined.lower()
    assert "hidden from the cli" in lowered
    assert "boundary_conditions.create_entity_list" in combined
    assert "entlist wrapper" in lowered


@pytest.mark.cli
@pytest.mark.unit
def test_describe_resolves_synergy_property_reachable_methods():
    """Describe should follow Synergy properties to their wrapper methods."""
    app = build_cli_app()

    class CLITestManager:
        """Wrapper reachable from a Synergy property for describe resolution."""

        def run(self, label: str) -> str:
            """Run the test manager action."""
            del label
            return "ok"

    orig_cls = getattr(moldflow, "CLITestManager", None)
    orig_attr = getattr(moldflow.Synergy, "cli_test_manager", None)

    def _get_cli_test_manager(self) -> CLITestManager:
        del self
        return CLITestManager()

    setattr(moldflow, "CLITestManager", CLITestManager)
    setattr(moldflow.Synergy, "cli_test_manager", property(_get_cli_test_manager))
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_test_manager.run"])
        assert result.exit_code == 0
        assert "synergy.cli_test_manager.run(" in result.stdout
        assert "label" in result.stdout
        assert "Try this:" in result.stdout
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
def test_describe_bare_synergy_property_prefers_property_over_wrapper_class_alias():
    """Bare describe should prefer the matching Synergy property when one exists."""
    app = build_cli_app()
    result = runner.invoke(app, ["describe", "cad_diagnostic"])
    assert result.exit_code == 0
    normalized = "".join(result.stdout.split())
    assert "synergy.cad_diagnostic" in result.stdout
    assert "_cad_diagnostic" not in result.stdout
    assert "Wrapper for CADDiagnostic class of Moldflow Synergy." not in result.stdout
    assert "Continuewithdescribesynergy.cad_diagnostic.<member>" in normalized
    assert "Try this:" not in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_describe_property_human_output_strips_rst_field_list_lines():
    """Human describe output should not expose raw reStructuredText property fields."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_doc_property", None)

    def _get_cli_doc_property(self) -> str:
        """Show a clean description.

        :getter: Get the current value.
        :type: str
        """
        del self
        return "ok"

    setattr(moldflow.Synergy, "cli_doc_property", property(_get_cli_doc_property))
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_doc_property"])
        assert result.exit_code == 0
        assert "Show a clean description." in result.stdout
        assert ":getter:" not in result.stdout
        assert ":type:" not in result.stdout
        assert "JSON example:" not in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_doc_property")
        else:
            setattr(moldflow.Synergy, "cli_doc_property", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_property_json_output_strips_rst_field_list_lines():
    """Structured describe output should not expose raw property RST field-list lines."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_doc_property_json", None)

    def _get_cli_doc_property_json(self) -> str:
        """Show a clean structured description.

        :getter: Get the current value.
        :type: str
        """
        del self
        return "ok"

    setattr(moldflow.Synergy, "cli_doc_property_json", property(_get_cli_doc_property_json))
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_doc_property_json", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert ":getter:" not in payload["summary"]
        assert ":type:" not in payload["summary"]
        assert "Show a clean structured description." in payload["summary"]
        assert "details" not in payload
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_doc_property_json")
        else:
            setattr(moldflow.Synergy, "cli_doc_property_json", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_readwrite_property_human_output_shows_read_and_assignment_guidance():
    """Describe should show both read and assignment guidance for read/write properties."""
    app = build_cli_app()
    orig = getattr(moldflow.Synergy, "cli_rw_property_doc", None)

    def _get_cli_rw_property_doc(self) -> str:
        del self
        return "Fusion"

    def _set_cli_rw_property_doc(self, value: str) -> None:
        del self, value

    setattr(
        moldflow.Synergy,
        "cli_rw_property_doc",
        property(_get_cli_rw_property_doc, _set_cli_rw_property_doc),
    )
    try:
        result = runner.invoke(app, ["describe", "synergy.cli_rw_property_doc"])
        assert result.exit_code == 0
        assert "Read current value:" in result.stdout
        assert "invoke synergy.cli_rw_property_doc" in result.stdout
        assert "Set it with:" in result.stdout
        assert '"value": "<value>"' in result.stdout
    finally:
        if orig is None:
            delattr(moldflow.Synergy, "cli_rw_property_doc")
        else:
            setattr(moldflow.Synergy, "cli_rw_property_doc", orig)


@pytest.mark.cli
@pytest.mark.unit
def test_describe_human_output_wraps_long_commands_with_indentation():
    """Wrapped describe command examples should keep continuation lines indented."""
    app = build_cli_app()
    result = runner.invoke(
        app, ["describe", "synergy.plot_manager.find_plot_by_name"], terminal_width=78
    )
    assert result.exit_code == 0
    assert any(
        line.startswith("  dataset_name=<dataset_name>") for line in result.stdout.splitlines()
    )


@pytest.mark.cli
@pytest.mark.unit
def test_list_does_not_execute_class_descriptors_during_introspection():
    """list should be descriptor-safe and not trigger class-level side effects."""
    app = build_cli_app()

    class ExplosiveDescriptor:
        """Descriptor used to ensure list introspection stays side-effect free."""

        def __get__(self, obj, owner=None):
            raise RuntimeError("descriptor should not execute during list")

    class CliExplosive:
        """Class containing a descriptor that must not be executed by list."""

        danger = ExplosiveDescriptor()

        def safe_method(self) -> str:
            """Simple callable used to keep class publicly invokable."""
            return "ok"

    orig_cls = getattr(moldflow, "CliExplosive", None)
    setattr(moldflow, "CliExplosive", CliExplosive)
    try:
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
    finally:
        if orig_cls is None:
            delattr(moldflow, "CliExplosive")
        else:
            setattr(moldflow, "CliExplosive", orig_cls)


@pytest.mark.cli
@pytest.mark.unit
def test_list_filter_regex_and_prefix():
    """list --filter supports partial and case-insensitive matches."""
    app = build_cli_app()
    with patch("moldflow_cli.context.get_synergy"), patch("moldflow_cli.factories.get_synergy"):
        r = runner.invoke(app, ["list", "--filter", "NEW_PROJ"])
    normalized = "".join(r.stdout.lower().split())
    assert r.exit_code == 0
    assert "new_project" in r.stdout.lower()
    assert "synergy.new_project" not in r.stdout.lower()
    assert "describeandinvokeaccepteitherform" in normalized


@pytest.mark.cli
@pytest.mark.unit
def test_list_filter_supports_wildcard_patterns():
    """list --filter should treat * as a wildcard pattern, not as a literal character."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--filter", "*_diag"])
    assert result.exit_code == 0
    lowered = result.stdout.lower()
    assert "cad_diagnostic" in lowered
    assert "diagnosis_manager" in lowered


@pytest.mark.cli
@pytest.mark.unit
def test_list_multiple_filters_are_additive():
    """Repeated list filters should match targets satisfying any provided filter."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--json", "--filter", "NEW_PROJ", "--filter", "*_diag"])
    assert result.exit_code == 0
    targets = {row["target"] for row in json.loads(result.stdout)}
    assert "synergy.new_project" in targets
    assert any(target.startswith("synergy.cad_diagnostic.") for target in targets)


@pytest.mark.cli
@pytest.mark.unit
def test_list_human_output_shows_explicit_message_for_empty_filtered_results():
    """Filtered human list output should explain when no invokable targets match."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--filter", "animation_export_options.size_x"])
    assert result.exit_code == 0
    assert "No invokable targets matched this filter." in result.stdout
    assert "rerun list --json for canonical target strings" in result.stdout
    assert "Use the Target value with the action shown above" not in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_list_with_describe_requires_structured_output():
    """Expanded list metadata should stay opt-in for JSON/YAML flows only."""
    app = build_cli_app()
    result = runner.invoke(app, ["--no-color", "list", "--with-describe"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "--with-describe requires --json or --yaml" in combined


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_honors_max_results():
    """Structured list output should honor --max-results to cap discovery volume."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--json", "--max-results", "2"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 2


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_allows_zero_max_results():
    """Structured list output should allow a zero cap for callers that want no rows."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--json", "--max-results", "0"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


@pytest.mark.cli
@pytest.mark.unit
def test_list_rejects_negative_max_results():
    """List should reject negative result caps explicitly."""
    app = build_cli_app()
    result = runner.invoke(app, ["--no-color", "list", "--json", "--max-results", "-1"])
    assert result.exit_code != 0
    combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
    assert "--max-results must be greater than or equal to 0" in combined


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_includes_invokable_synergy_property_targets():
    """List output should include rooted property targets that invoke supports."""
    app = build_cli_app()
    orig_readonly = getattr(moldflow.Synergy, "cli_readonly_property", None)
    orig_settable = getattr(moldflow.Synergy, "cli_settable_property", None)

    def _get_cli_readonly_property(self) -> str:
        del self
        return "2027"

    def _get_cli_settable_property(self) -> str:
        del self
        return "Fusion"

    def _set_cli_settable_property(self, value: str) -> None:
        del self, value

    setattr(moldflow.Synergy, "cli_readonly_property", property(_get_cli_readonly_property))
    setattr(
        moldflow.Synergy,
        "cli_settable_property",
        property(_get_cli_settable_property, _set_cli_settable_property),
    )
    try:
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        rows_by_target = {row["target"]: row for row in payload}
        readonly = rows_by_target["synergy.cli_readonly_property"]
        readwrite = rows_by_target["synergy.cli_settable_property"]
        assert readonly["owner_class"] == "Synergy"
        assert readonly["kind"] == "property"
        assert readonly["suggested_command"] == "describe synergy.cli_readonly_property"
        assert readonly["commands"] == {
            "describe": "describe synergy.cli_readonly_property",
            "invoke": "invoke synergy.cli_readonly_property",
        }
        assert readwrite["kind"] == "settable_property"
        assert readwrite["suggested_command"] == "describe synergy.cli_settable_property"
        assert readwrite["commands"] == {
            "describe": "describe synergy.cli_settable_property",
            "invoke": "invoke synergy.cli_settable_property",
        }
    finally:
        if orig_readonly is None:
            delattr(moldflow.Synergy, "cli_readonly_property")
        else:
            setattr(moldflow.Synergy, "cli_readonly_property", orig_readonly)
        if orig_settable is None:
            delattr(moldflow.Synergy, "cli_settable_property")
        else:
            setattr(moldflow.Synergy, "cli_settable_property", orig_settable)


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_roots_synergy_reachable_wrapper_targets():
    """List should emit Synergy-rooted targets when a wrapper is reachable from Synergy."""
    app = build_cli_app()

    class CLITestManager:
        """Fixture wrapper reachable from Synergy through a property."""

        def run(self) -> str:
            """Return a sentinel value."""
            return "ok"

    orig_cls = getattr(moldflow, "CLITestManager", None)
    orig_attr = getattr(moldflow.Synergy, "cli_test_manager", None)
    setattr(moldflow, "CLITestManager", CLITestManager)

    def _get_cli_test_manager(self) -> CLITestManager:
        del self
        return CLITestManager()

    setattr(moldflow.Synergy, "cli_test_manager", property(_get_cli_test_manager))
    try:
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        rows_by_target = {row["target"]: row for row in payload}
        assert "synergy.cli_test_manager" not in rows_by_target
        row = rows_by_target["synergy.cli_test_manager.run"]
        assert row["owner_class"] == "CLITestManager"
        assert row["suggested_command"] == "describe synergy.cli_test_manager.run"
        assert row["commands"] == {
            "describe": "describe synergy.cli_test_manager.run",
            "invoke": "invoke synergy.cli_test_manager.run",
        }
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
def test_list_json_with_describe_embeds_structured_target_metadata():
    """List should optionally include describe-like structured payloads for each target."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--json", "--with-describe", "--filter", "open_project"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    rows_by_target = {row["target"]: row for row in payload}
    row = rows_by_target["synergy.open_project"]
    assert row["next_command"] == "describe synergy.open_project"
    assert isinstance(row.get("describe"), dict)
    assert row["describe"]["target"] == "synergy.open_project"
    assert row["describe"]["next_command"] == "invoke synergy.open_project path=<path>"
    assert (
        row["describe"]["invoke_examples"]["cli_command"]
        == "invoke synergy.open_project path=<path>"
    )
    assert row["describe"]["params_json_template"]["path"] is None


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_hides_builder_style_settable_properties_but_keeps_methods():
    """Builder-style wrappers should list their action methods, not each configuration knob."""
    app = build_cli_app()

    class CLITestGenerator:
        """Builder-style wrapper with one action method and several settable properties."""

        def generate(self) -> bool:
            """Run the generator."""
            return True

        @property
        def width(self) -> float:
            """Get the configured width."""
            return 1.0

        @width.setter
        def width(self, value: float) -> None:
            del value

        @property
        def height(self) -> float:
            """Get the configured height."""
            return 1.0

        @height.setter
        def height(self, value: float) -> None:
            del value

        @property
        def depth(self) -> float:
            """Get the configured depth."""
            return 1.0

        @depth.setter
        def depth(self, value: float) -> None:
            del value

    orig_cls = getattr(moldflow, "CLITestGenerator", None)
    orig_attr = getattr(moldflow.Synergy, "cli_test_generator", None)
    setattr(moldflow, "CLITestGenerator", CLITestGenerator)

    def _get_cli_test_generator(self) -> CLITestGenerator:
        del self
        return CLITestGenerator()

    setattr(moldflow.Synergy, "cli_test_generator", property(_get_cli_test_generator))
    try:
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        rows_by_target = {row["target"]: row for row in payload}
        assert "synergy.cli_test_generator.width" not in rows_by_target
        assert "synergy.cli_test_generator.height" not in rows_by_target
        assert "synergy.cli_test_generator.depth" not in rows_by_target
        row = rows_by_target["synergy.cli_test_generator.generate"]
        assert row["owner_class"] == "CLITestGenerator"
        assert row["commands"] == {
            "describe": "describe synergy.cli_test_generator.generate",
            "invoke": "invoke synergy.cli_test_generator.generate",
        }
    finally:
        if orig_cls is None:
            delattr(moldflow, "CLITestGenerator")
        else:
            setattr(moldflow, "CLITestGenerator", orig_cls)
        if orig_attr is None:
            delattr(moldflow.Synergy, "cli_test_generator")
        else:
            setattr(moldflow.Synergy, "cli_test_generator", orig_attr)


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_hides_config_only_rooted_option_surfaces():
    """Config-only rooted wrappers should not flood list output with option properties."""
    app = build_cli_app()

    class CLITestOptions:
        """Option-bag wrapper with only settable properties."""

        @property
        def width(self) -> float:
            """Get the configured width."""
            return 1.0

        @width.setter
        def width(self, value: float) -> None:
            del value

        @property
        def height(self) -> float:
            """Get the configured height."""
            return 1.0

        @height.setter
        def height(self, value: float) -> None:
            del value

        @property
        def depth(self) -> float:
            """Get the configured depth."""
            return 1.0

        @depth.setter
        def depth(self, value: float) -> None:
            del value

    orig_cls = getattr(moldflow, "CLITestOptions", None)
    orig_attr = getattr(moldflow.Synergy, "cli_test_options", None)
    setattr(moldflow, "CLITestOptions", CLITestOptions)

    def _get_cli_test_options(self) -> CLITestOptions:
        del self
        return CLITestOptions()

    setattr(moldflow.Synergy, "cli_test_options", property(_get_cli_test_options))
    try:
        result = runner.invoke(app, ["list", "--json"])
        assert result.exit_code == 0
        rows_by_target = {row["target"]: row for row in json.loads(result.stdout)}
        assert "synergy.cli_test_options.width" not in rows_by_target
        assert "synergy.cli_test_options.height" not in rows_by_target
        assert "synergy.cli_test_options.depth" not in rows_by_target
    finally:
        if orig_cls is None:
            delattr(moldflow, "CLITestOptions")
        else:
            setattr(moldflow, "CLITestOptions", orig_cls)
        if orig_attr is None:
            delattr(moldflow.Synergy, "cli_test_options")
        else:
            setattr(moldflow.Synergy, "cli_test_options", orig_attr)


@pytest.mark.cli
@pytest.mark.unit
def test_list_json_hides_synergy_create_factory_helper_surfaces():
    """Synergy create_* helper wrappers should not appear as top-level list targets."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--json"])
    assert result.exit_code == 0
    rows_by_target = {row["target"]: row for row in json.loads(result.stdout)}
    assert "synergy.boundary_conditions.create_entity_list" not in rows_by_target
    assert "synergy.create_double_array.add_double" not in rows_by_target
    assert "synergy.create_double_array.from_list" not in rows_by_target
    assert "synergy.create_double_array.size" not in rows_by_target


@pytest.mark.cli
@pytest.mark.unit
def test_list_human_output_includes_type_and_describe_guidance():
    """Human list output should stay discovery-first and point people to describe."""
    app = build_cli_app()
    orig_prop = getattr(moldflow.Synergy, "cli_settable_property", None)

    def _get_cli_settable_property(self) -> str:
        del self
        return "Fusion"

    def _set_cli_settable_property(self, value: str) -> None:
        del self, value

    setattr(
        moldflow.Synergy,
        "cli_settable_property",
        property(_get_cli_settable_property, _set_cli_settable_property),
    )
    try:
        result = runner.invoke(
            app, ["list", "--filter", "cli_settable_property"], terminal_width=120
        )
        normalized = "".join(result.stdout.split())
        assert result.exit_code == 0
        assert "Type" in result.stdout
        assert "Start" not in result.stdout
        assert "cli_settable_property" in result.stdout
        assert "Filtered matches:" in result.stdout
        assert "Use describe <target> to inspect parameters" in result.stdout
        assert "cli_settable_property" in normalized
    finally:
        if orig_prop is None:
            delattr(moldflow.Synergy, "cli_settable_property")
        else:
            setattr(moldflow.Synergy, "cli_settable_property", orig_prop)


@pytest.mark.cli
@pytest.mark.unit
def test_list_human_output_preserves_readwrite_kind_under_narrow_widths():
    """Human list output should keep the read/write distinction visible on narrow tables."""
    app = build_cli_app()
    orig_prop = getattr(moldflow.Synergy, "cli_settable_property_narrow", None)

    def _get_cli_settable_property_narrow(self) -> str:
        del self
        return "Fusion"

    def _set_cli_settable_property_narrow(self, value: str) -> None:
        del self, value

    setattr(
        moldflow.Synergy,
        "cli_settable_property_narrow",
        property(_get_cli_settable_property_narrow, _set_cli_settable_property_narrow),
    )
    try:
        result = runner.invoke(
            app, ["list", "--filter", "cli_settable_property_narrow"], terminal_width=72
        )
        assert result.exit_code == 0
        assert "settable" in result.stdout
        assert "rw-prop" not in result.stdout
        assert "..." not in result.stdout
    finally:
        if orig_prop is None:
            delattr(moldflow.Synergy, "cli_settable_property_narrow")
        else:
            setattr(moldflow.Synergy, "cli_settable_property_narrow", orig_prop)


@pytest.mark.cli
@pytest.mark.unit
def test_list_human_output_avoids_large_filtered_match_duplication():
    """Broad filtered lists should avoid duplicating exact-match summaries for every row."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--filter", "plot_manager"])
    assert result.exit_code == 0
    assert "Filtered matches:" not in result.stdout
    assert "Start" not in result.stdout
    assert "Class" not in result.stdout
    assert "Showing the compact table for" in result.stdout
    assert "canonical target strings" in result.stdout
    assert "describe" in result.stdout


@pytest.mark.cli
@pytest.mark.unit
def test_list_human_output_wraps_long_targets_without_exact_target_loss():
    """Human list tables should keep long target text visible instead of ellipsizing it away."""
    app = build_cli_app()
    orig_prop = getattr(moldflow.Synergy, "cli_extremely_descriptive_mesh_type_property", None)

    def _get_cli_extremely_descriptive_mesh_type_property(self) -> str:
        del self
        return "Fusion"

    setattr(
        moldflow.Synergy,
        "cli_extremely_descriptive_mesh_type_property",
        property(_get_cli_extremely_descriptive_mesh_type_property),
    )
    try:
        result = runner.invoke(
            app, ["list", "--filter", "extremely_descriptive_mesh_type_property"], terminal_width=72
        )
        normalized = "".join(result.stdout.split())
        assert result.exit_code == 0
        assert "cli_extremely_descriptive_mesh_type_property" in normalized
        assert "..." not in result.stdout
    finally:
        if orig_prop is None:
            delattr(moldflow.Synergy, "cli_extremely_descriptive_mesh_type_property")
        else:
            setattr(moldflow.Synergy, "cli_extremely_descriptive_mesh_type_property", orig_prop)


@pytest.mark.cli
@pytest.mark.unit
@pytest.mark.skipif(not _has_yaml(), reason="PyYAML not installed")
def test_list_yaml_output():
    """List should emit YAML when requested."""
    app = build_cli_app()
    result = runner.invoke(app, ["list", "--yaml"])
    assert result.exit_code == 0
    assert "target" in result.stdout
