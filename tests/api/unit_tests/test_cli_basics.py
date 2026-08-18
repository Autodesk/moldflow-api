# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused basic command behavior tests for moldflow CLI."""

from __future__ import annotations

from unittest.mock import call, patch

import pytest
from typer.testing import CliRunner
import moldflow

from moldflow_cli.commands import build_cli_app
from tests.api.unit_tests.conftest import strip_ansi

runner = CliRunner()


@pytest.mark.cli
@pytest.mark.unit
class TestUnitCLI:
    """Unit tests for the moldflow CLI entrypoints."""

    def test_help_runs_without_synergy(self):
        """Ensure global help runs without instantiating Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["--no-color", "--help"])
        assert result.exit_code == 0
        # Help should not need to touch Synergy/COM at all.
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
        output = strip_ansi(result.stdout)
        assert "Moldflow command-line interface" in output
        assert "Start with 'list' to discover targets" in output
        assert "describe <target>" in output
        assert "invoke <target>" in output

    def test_help_shows_global_no_color_option(self):
        """Global help should advertise the output-styling toggle."""
        app = build_cli_app()
        result = runner.invoke(app, ["--no-color", "--help"])
        assert result.exit_code == 0
        assert "--no-color" in strip_ansi(result.stdout)

    def test_subcommand_help_runs_without_synergy(self):
        """Subcommand help should be available without creating Synergy/COM objects."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            list_help = runner.invoke(app, ["--no-color", "list", "--help"])
            describe_help = runner.invoke(app, ["--no-color", "describe", "--help"])
            invoke_help = runner.invoke(app, ["--no-color", "invoke", "--help"])

        assert list_help.exit_code == 0
        assert describe_help.exit_code == 0
        assert invoke_help.exit_code == 0
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
        list_output = strip_ansi(list_help.stdout)
        describe_output = strip_ansi(describe_help.stdout)
        invoke_output = strip_ansi(invoke_help.stdout)
        assert "Discover invokable targets and the next command to run for each one" in list_output
        assert "--json" in list_output
        assert "--with-describe" in list_output
        assert (
            "Inspect a target's signature, docs, examples, and structured invoke template"
            in describe_output
        )
        assert "Run a Moldflow target with named parameters or JSON input" in invoke_output

    def test_global_no_color_option_configures_cli_output(self):
        """Global --no-color should reconfigure shared console output before dispatch."""
        with patch("moldflow_cli.commands.configure_console") as mock_configure_console:
            app = build_cli_app()
            result = runner.invoke(app, ["--no-color", "version"])

        assert result.exit_code == 0
        assert mock_configure_console.call_args_list == [call(no_color=False), call(no_color=True)]

    def test_version_command_is_registered(self):
        """Ensure explicit 'version' subcommand is available."""
        app = build_cli_app()
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert moldflow.__version__ in result.stdout

    def test_list_does_not_instantiate_synergy(self):
        """Ensure 'list' reflects targets without touching Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["list", "--filter", "synergy"])
        assert result.exit_code == 0
        # Listing invokable targets is based on reflection only.
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
        # Should at least mention a Synergy-related target.
        assert "synergy" in result.stdout.lower()

    def test_describe_uses_signature_without_synergy(self):
        """Ensure 'describe' uses introspection only and does not touch Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            # Synergy.open_project is a simple, well-known method to describe.
            result = runner.invoke(app, ["describe", "synergy.open_project"])
        assert result.exit_code == 0
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()
        # Signature line should include the parameter name.
        assert "open_project" in result.stdout
        assert "path" in result.stdout

    def test_invoke_missing_required_param_fails_before_synergy(self):
        """Ensure invoke validates required parameters before creating Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["invoke", "synergy.open_project"])
        # Should fail due to missing arguments.
        assert result.exit_code != 0
        # Should not instantiate Synergy when arguments are invalid.
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()

    def test_invoke_simple_scalar_method_calls_mock(self):
        """Invoke a simple scalar-argument method and ensure the mock is called correctly."""
        app = build_cli_app()

        class FakeSynergyWindow:
            """Fake Synergy exposing set_application_window_pos."""

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, int, int]] = []

            def set_application_window_pos(
                self, x: int, y: int, size_x: int, size_y: int
            ) -> bool:  # noqa: D401
                """Mock implementation that records call arguments."""
                self.calls.append((x, y, size_x, size_y))
                return True

        fake = FakeSynergyWindow()
        with patch("moldflow_cli.context.get_synergy", return_value=fake), patch(
            "moldflow_cli.factories.get_synergy", return_value=fake
        ):
            result = runner.invoke(
                app,
                [
                    "invoke",
                    "synergy.set_application_window_pos",
                    "x=10",
                    "y=20",
                    "size_x=800",
                    "size_y=600",
                ],
            )

        assert result.exit_code == 0
        assert fake.calls == [(10, 20, 800, 600)]

    def test_invoke_unknown_target_does_not_instantiate_synergy(self):
        """Unknown target should fail fast without creating Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["invoke", "synergy.no_such_method"])
        assert result.exit_code != 0
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()

    def test_describe_unknown_target_shows_actionable_error(self):
        """Unknown describe target should fail with a clear message and no Synergy usage."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["describe", "synergy.no_such_method"])

        assert result.exit_code != 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "no attribute" in combined.lower() or "cannot resolve" in combined.lower()
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()

    def test_invoke_unknown_parameter_does_not_instantiate_synergy(self):
        """Unknown parameter name should be reported without creating Synergy/COM."""
        app = build_cli_app()
        with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
            "moldflow_cli.factories.get_synergy"
        ) as mock_fact_synergy:
            result = runner.invoke(app, ["invoke", "synergy.open_project", "bad_param=foo"])
        assert result.exit_code != 0
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "Run 'describe" in combined
        assert "inspect accepted parameters and JSON examples" in combined
        mock_ctx_synergy.assert_not_called()
        mock_fact_synergy.assert_not_called()

    def test_invoke_nested_args_missing_required_param_does_not_instantiate_synergy(self):
        """Nested args still fail required-arg checks before Synergy/COM."""
        app = build_cli_app()
        orig = getattr(moldflow.Synergy, "cli_test_nested_required", None)

        def cli_test_nested_required(self, required: str, options: "Vector | None" = None) -> str:
            del self, required, options
            return "ok"

        setattr(moldflow.Synergy, "cli_test_nested_required", cli_test_nested_required)
        try:
            with patch("moldflow_cli.context.get_synergy") as mock_ctx_synergy, patch(
                "moldflow_cli.factories.get_synergy"
            ) as mock_fact_synergy:
                result = runner.invoke(
                    app, ["invoke", "synergy.cli_test_nested_required", "options.x=1"]
                )

            assert result.exit_code != 0
            out = (result.stdout or "") + (getattr(result, "stderr", "") or "")
            assert "missing required parameter" in out.lower()
            mock_ctx_synergy.assert_not_called()
            mock_fact_synergy.assert_not_called()
        finally:
            if orig is None:
                delattr(moldflow.Synergy, "cli_test_nested_required")
            else:
                setattr(moldflow.Synergy, "cli_test_nested_required", orig)
