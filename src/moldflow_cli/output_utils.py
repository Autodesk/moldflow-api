# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from contextlib import nullcontext
from typing import Any
import json as _json
import os
import sys
import textwrap
import typer
from moldflow.i18n import get_text


_T = get_text()


_console_singleton = None
_console_no_color = False


def should_use_ascii_output(*, stderr: bool = False) -> bool:
	"""Return True when output should avoid Unicode box-drawing characters."""
	stream = sys.stderr if stderr else sys.stdout
	isatty = getattr(stream, "isatty", None)
	try:
		is_terminal = bool(isatty()) if callable(isatty) else False
	except (OSError, ValueError):
		is_terminal = False
	if not is_terminal:
		return True
	return os.environ.get("TERM", "").lower() == "dumb"


def configure_console(*, no_color: bool) -> None:
	"""Configure the shared Rich console used by CLI commands."""
	global _console_no_color, _console_singleton
	if _console_singleton is not None and _console_no_color != no_color:
		_console_singleton = None
	_console_no_color = no_color


def get_console():
	"""Return a shared rich Console instance."""
	global _console_singleton
	if _console_singleton is None:
		from rich.console import Console

		_console_singleton = Console(no_color=_console_no_color)
	return _console_singleton


def human_output_pager(console: Any):
	"""Return a pager context for human terminal output when stdout is interactive."""
	if not bool(getattr(console, "is_terminal", False)):
		return nullcontext()
	if bool(getattr(console, "is_dumb_terminal", False)):
		return nullcontext()
	try:
		return console.pager(styles=False)
	except (AttributeError, OSError, RuntimeError):
		return nullcontext()


def human_table_kwargs(console: Any) -> dict[str, Any]:
	"""Return table kwargs that stay readable in the active human-output environment."""
	from rich import box

	if should_use_ascii_output() or bool(getattr(console, "is_dumb_terminal", False)):
		return {"box": box.ASCII, "safe_box": True}
	if sys.platform != "win32":
		return {}
	if not bool(getattr(console, "is_terminal", False)):
		return {}
	if bool(getattr(console, "is_dumb_terminal", False)):
		return {"box": box.ASCII, "safe_box": True}

	# Rich's Windows pager path can backslash-escape box-drawing characters when the
	# console code page cannot encode them, so prefer ASCII table borders there.
	return {"box": box.ASCII, "safe_box": True}


def to_json_text(payload: Any, *, context: str, default: Any | None = None) -> str:
	"""Serialize payload to JSON with consistent error handling for CLI UX."""
	try:
		if default is None:
			return _json.dumps(payload, indent=2, ensure_ascii=False)
		return _json.dumps(payload, indent=2, default=default, ensure_ascii=False)
	except (TypeError, ValueError) as exc:
		raise typer.BadParameter(
			_T("Failed to render JSON output for {context}: {error}").format(
				context=context, error=exc
			)
		) from exc


def emit_yaml_text(payload: Any, *, context: str) -> str:
	"""Serialize payload to YAML with consistent error handling."""
	try:
		import yaml  # type: ignore
	except ModuleNotFoundError as exc:  # pragma: no cover - dependent on PyYAML availability
		raise typer.BadParameter(
			_T("--yaml requested but PyYAML is not installed: {error}").format(error=exc)
		) from exc
	try:
		return yaml.safe_dump(payload, sort_keys=False)
	except Exception as exc:  # pragma: no cover - serializer-specific failure
		raise typer.BadParameter(
			_T("Failed to render YAML output for {context}: {error}").format(
				context=context, error=exc
			)
		) from exc


def print_wrapped_command(console: Any, command: str, *, indent: str = "  ") -> None:
	"""Render a CLI command with a hanging indent for easier terminal scanning."""
	width = getattr(console, "width", None)
	if not isinstance(width, int):
		width = 80
	width = max(width, len(indent) + 20)
	console.print(
		textwrap.fill(
			command,
			width=width,
			initial_indent=indent,
			subsequent_indent=indent,
		),
		markup=False,
	)


def _vector_text(value: dict[str, Any]) -> str | None:
	if not all(axis in value for axis in ("x", "y", "z")):
		return None
	return f"({value['x']}, {value['y']}, {value['z']})"


def _render_list_text(console: Any, values: list[Any], *, context: str, heading: str) -> None:
	console.print(heading, markup=False)
	if not values:
		console.print("[]", markup=False)
		return
	if all(isinstance(item, (str, int, float, bool)) or item is None for item in values):
		for index, item in enumerate(values, start=1):
			console.print(f"{index}. {item}", markup=False)
		return
	console.print(to_json_text(values, context=context), markup=False)


def render_serialized_value(console: Any, value: Any, *, context: str) -> None:
	"""Render a serialized invoke payload in a concise human-readable form."""
	if isinstance(value, str):
		console.print(value, markup=False)
		return
	if isinstance(value, (int, float, bool)) or value is None:
		console.print(value)
		return
	if isinstance(value, list):
		_render_list_text(console, value, context=context, heading=_T("List result:"))
		return
	if not isinstance(value, dict):
		console.print(repr(value), markup=False)
		return

	if isinstance(value.get("string"), str) and "size" in value:
		console.print(
			_T("{type_name} ({size} items): {value}").format(
				type_name=value.get("type", _T("Selection")),
				size=value.get("size", "?"),
				value=value["string"],
			),
			markup=False,
		)
		return

	vector_text = _vector_text(value)
	if vector_text is not None:
		console.print(
			"{type_name}: {value}".format(
				type_name=value.get("type", _T("Vector")),
				value=vector_text,
			),
			markup=False,
		)
		return

	array_values = value.get("values")
	if isinstance(array_values, list):
		heading = _T("{type_name} values ({count} items):").format(
			type_name=value.get("type", _T("Array")),
			count=len(array_values),
		)
		if all(isinstance(item, dict) for item in array_values):
			vector_items = [_vector_text(item) for item in array_values]
			if all(isinstance(item, str) for item in vector_items):
				console.print(heading, markup=False)
				for index, item in enumerate(vector_items, start=1):
					console.print(f"{index}. {item}", markup=False)
				return
		_render_list_text(console, array_values, context=context, heading=heading)
		return

	if all(field in value for field in ("id", "name", "prop_type")):
		console.print(
			_T("Property {name} (id={id}, type={prop_type})").format(
				name=value["name"],
				id=value["id"],
				prop_type=value["prop_type"],
			),
			markup=False,
		)
		return

	attributes = value.get("attributes")
	if isinstance(attributes, dict):
		console.print(
			_T("{type_name} attributes:").format(
				type_name=value.get("type", _T("Object")),
			),
			markup=False,
		)
		console.print(to_json_text(attributes, context=context), markup=False)
		return

	type_name = value.get("type")
	if isinstance(type_name, str) and type_name:
		console.print(_T("{type_name} result:").format(type_name=type_name), markup=False)
	console.print(to_json_text(value, context=context), markup=False)

