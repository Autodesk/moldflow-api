# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import shlex

import click
import typer
from moldflow.i18n import get_text

from .output_utils import get_console


_T = get_text()

_BUILTIN_COMMANDS = ("help", "?", "exit", "quit", "clear", "reset")

_BUILTIN_HELP_ENTRIES: list[dict[str, object]] = [
	{
		"names": ["help", "?"],
		"summary": _T("Shows available commands and usage information."),
		"detail": _T("Use 'help <command>' for detailed help on a specific command."),
	},
	{
		"names": ["exit", "quit"],
		"summary": _T("Exits the REPL."),
		"detail": _T("Ctrl+D also exits."),
	},
	{
		"names": ["clear"],
		"summary": _T("Clears the terminal screen and redraws the banner."),
	},
	{
		"names": ["reset"],
		"summary": _T("Closes Synergy and resets the session for a fresh start."),
		"detail": _T("Tab completion targets are refreshed automatically."),
	},
]

_BUILTIN_NAMES = frozenset(
	name for entry in _BUILTIN_HELP_ENTRIES for name in entry["names"]
)


def _get_version() -> str:
	try:
		from importlib.metadata import PackageNotFoundError, version

		return version("moldflow")
	except PackageNotFoundError:
		return "unknown"


def _get_cli_command_names(app) -> list[str]:
	"""Derive registered command names from the Typer app's Click metadata."""
	from typer.main import get_command

	click_app = get_command(app)
	return sorted(name for name in click_app.commands if name != "repl")


def _get_cli_help_entries(app) -> list[tuple[str, str]]:
	"""Get (name, help_text) pairs for help display, derived from the app."""
	from typer.main import get_command

	click_app = get_command(app)
	entries = []
	for name in sorted(click_app.commands):
		if name == "repl":
			continue
		cmd = click_app.commands[name]
		help_text = (cmd.help or cmd.short_help or "").split("\n")[0]
		entries.append((name, help_text))
	return entries


def _print_banner(console) -> None:
	from rich.panel import Panel

	hint = _T("Type 'help' for available commands, 'exit' to quit.")
	console.print(
		Panel(
			f"[bold]moldflow[/bold] {_T('interactive shell')} [dim]v{_get_version()}[/dim]\n"
			f"[dim]{hint}[/dim]",
			border_style="blue",
		)
	)


def _print_help(console, cli_entries: list[tuple[str, str]]) -> None:
	console.print(f"\n[bold]{_T('Commands:')}[/bold]")
	for name, help_text in cli_entries:
		console.print(f"  [green]{name:<20s}[/green] {help_text}")
	console.print()
	console.print(f"[bold]{_T('Session:')}[/bold]")
	session_items = [
		("reset", _T("Close Synergy and reset the session")),
		("clear", _T("Clear the screen")),
		("help", _T("Show this help message")),
		("help <command>", _T("Show detailed help for a command")),
		("exit / quit", _T("Exit the REPL")),
	]
	for label, desc in session_items:
		console.print(f"  [green]{label:<20s}[/green] {desc}")
	console.print()


def _print_builtin_help(console, subcmd: str) -> None:
	for entry in _BUILTIN_HELP_ENTRIES:
		if subcmd in entry["names"]:
			aliases = " / ".join(f"[green]{n}[/green]" for n in entry["names"])
			console.print(f"\n  {aliases}")
			console.print(f"    {entry['summary']}")
			detail = entry.get("detail")
			if detail:
				console.print(f"    [dim]{detail}[/dim]")
			console.print()
			return


def _import_readline(console=None):
	"""Try to import a readline-compatible module.

	Returns the module, or ``None`` when no implementation is available.
	"""
	try:
		import readline

		return readline
	except ImportError:
		pass
	try:
		import pyreadline3 as readline  # Windows fallback

		return readline
	except ImportError:
		if console is not None:
			console.print(
				"[dim]"
				+ _T("Tip: install pyreadline3 for tab completion support on Windows.")
				+ "[/dim]"
			)
		return None


def _bind_tab_complete(readline) -> None:
	"""Bind the tab key using the syntax appropriate for the readline backend."""
	# macOS ships libedit instead of GNU readline; it needs different syntax.
	if getattr(readline, "__doc__", "") and "libedit" in (readline.__doc__ or ""):
		readline.parse_and_bind("bind ^I rl_complete")
	else:
		readline.parse_and_bind("tab: complete")


def _build_completer(readline, all_commands: list[str], load_targets):
	"""Return a readline-compatible completer function."""

	def completer(text: str, state: int) -> str | None:
		try:
			buffer = readline.get_line_buffer().lstrip()
			has_context = True
		except AttributeError:
			# Without the full line buffer we cannot distinguish first-word
			# from second-word completion, so only command names are offered.
			buffer = text
			has_context = False
		parts = buffer.split()

		if len(parts) <= 1 and not buffer.endswith(" "):
			options = [c + " " for c in all_commands if c.startswith(text)]
		elif has_context and parts[0] in ("describe", "invoke") and not text.startswith("-"):
			targets = load_targets()
			options = [t + " " for t in targets if t.startswith(text)]
		else:
			options = []

		return options[state] if state < len(options) else None

	return completer


def _setup_completion(all_commands: list[str], console=None):
	"""Best-effort readline setup for tab completion and history.

	Returns a callable that invalidates the cached target list, or a
	no-op lambda when readline is unavailable.
	"""
	readline = _import_readline(console)
	if readline is None:
		return lambda: None

	_targets: list[str] | None = None

	def invalidate_targets() -> None:
		nonlocal _targets
		_targets = None

	def _load_targets() -> list[str]:
		nonlocal _targets
		if _targets is None:
			try:
				from .commands import collect_list_rows

				_targets = [r["target"] for r in collect_list_rows(None)]
			except (ImportError, AttributeError, KeyError, TypeError) as exc:
				logging.getLogger(__name__).debug(
					"Failed to load completion targets: %s", exc
				)
				_targets = []
		return _targets

	readline.set_completer(_build_completer(readline, all_commands, _load_targets))
	readline.set_completer_delims(" \t\n")
	_bind_tab_complete(readline)
	return invalidate_targets


def _normalise_args(args: list[str]) -> list[str] | None:
	"""Strip a leading ``moldflow`` prefix and reject ``repl`` re-entry.

	Returns the cleaned arg list, an empty list when the command should be
	silently skipped, or ``None`` when the REPL re-entry message should be
	shown.
	"""
	if not args:
		return []
	if args[0].lower() == "moldflow":
		args = args[1:]
	if not args:
		return []
	if args[0].lower() == "repl":
		return None
	return args


def _run_app_safely(app, console, args: list[str], *, debug: bool) -> None:
	"""Invoke the Typer/Click app and translate exceptions to user messages."""
	try:
		app(args, standalone_mode=False)
	except SystemExit as exc:
		# 0/None = success; 1 = app-level failure (already reported);
		# 2 = Click usage error (already printed).  Only surface unexpected codes.
		if exc.code not in (0, None, 1, 2):
			console.print(
				f"[red]{_T('Command exited with status {code}').format(code=exc.code)}[/red]"
			)
	except KeyboardInterrupt:
		console.print(f"\n[dim]{_T('Interrupted.')}[/dim]")
	except click.exceptions.Abort:
		console.print(f"\n[dim]{_T('Aborted.')}[/dim]")
	except click.exceptions.ClickException as exc:
		exc.show()
	except Exception as exc:
		if debug:
			console.print_exception()
		else:
			console.print(f"[red]{_T('Error:')}[/red] {exc}")


def _dispatch(app, console, args: list[str], *, debug: bool = False) -> None:
	"""Dispatch pre-parsed args to the Typer/Click app."""
	args = _normalise_args(args)
	if args is None:
		console.print(f"[dim]{_T('You are already in the REPL.')}[/dim]")
		return
	if not args:
		return
	_run_app_safely(app, console, args, debug=debug)


def _read_line(console) -> str | None:
	"""Read one line of input.  Returns ``None`` on EOF (exit)."""
	try:
		return input("moldflow> ")
	except EOFError:
		console.print(f"\n{_T('Goodbye!')}")
		return None
	except KeyboardInterrupt:
		console.print()
		return ""


def _handle_help(console, parts, cli_command_names, cli_help_entries, app, *, debug):
	"""Process ``help`` / ``?`` commands."""
	if len(parts) <= 1:
		_print_help(console, cli_help_entries)
		return
	subcmd = parts[1].lower()
	if subcmd in _BUILTIN_NAMES:
		_print_builtin_help(console, subcmd)
	elif subcmd in cli_command_names:
		_dispatch(app, console, [parts[1], "--help"], debug=debug)
	else:
		console.print(f"[yellow]{_T('Unknown command:')}[/yellow] {parts[1]}")
		console.print(f"[dim]{_T('Type help to see available commands.')}[/dim]")


def _handle_reset(console, reset_synergy, invalidate_completion_cache, *, debug):
	"""Process the ``reset`` command."""
	try:
		reset_synergy()
		invalidate_completion_cache()
		console.print(f"[dim]{_T('Synergy session reset.')}[/dim]")
	except Exception as exc:
		if debug:
			console.print_exception()
		else:
			console.print(f"[red]{_T('Failed to reset session:')}[/red] {exc}")


def _parse_input(console, line: str) -> list[str] | None:
	"""Strip and tokenise a raw input line.  Returns ``None`` on parse error."""
	line = line.strip()
	if not line:
		return []
	try:
		return shlex.split(line)
	except ValueError as exc:
		console.print(f"[red]{_T('Parse error:')}[/red] {exc}")
		return None


def repl_cmd(
	debug: bool = typer.Option(
		False,
		"--debug",
		help=_T("Show full tracebacks on errors instead of short messages."),
	),
) -> None:
	"""Start an interactive moldflow shell session."""
	from .commands import build_cli_app
	from .context import reset_synergy

	console = get_console()
	app = build_cli_app()

	cli_command_names = _get_cli_command_names(app)
	cli_help_entries = _get_cli_help_entries(app)

	all_commands = sorted(set(list(_BUILTIN_COMMANDS) + cli_command_names))
	invalidate_completion_cache = _setup_completion(all_commands, console)
	_print_banner(console)

	while True:
		line = _read_line(console)
		if line is None:
			break

		parts = _parse_input(console, line)
		if parts is None or not parts:
			continue

		first = parts[0].lower()

		if first in ("exit", "quit"):
			console.print(_T("Goodbye!"))
			break

		if first in ("help", "?"):
			_handle_help(console, parts, cli_command_names, cli_help_entries, app, debug=debug)
		elif first == "clear":
			console.clear()
			_print_banner(console)
		elif first == "reset":
			_handle_reset(console, reset_synergy, invalidate_completion_cache, debug=debug)
		else:
			_dispatch(app, console, parts, debug=debug)
