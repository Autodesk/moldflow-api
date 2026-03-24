# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any
import inspect
import re

import typer
from moldflow.i18n import get_text

from .constants import (
	CLI_MODE_PROPERTY_ASSIGNMENT,
	CLI_ROOT_MOLDFLOW,
	CLI_ROOT_SYNERGY,
)
from .introspection import (
	get_docstring,
	get_signature_string,
	split_structured_doc,
)
from .invoke_handlers import (
	SCHEMA_VERSION,
	build_invoke_template_for_target,
	invoke_cmd,
)
from .listing import (
	collect_list_rows,
	has_list_filters,
	human_list_kind,
	human_list_target,
	render_filtered_list_matches,
)
from .output_utils import (
	configure_console,
	emit_yaml_text,
	get_console,
	human_output_pager,
	human_table_kwargs,
	should_use_ascii_output,
	to_json_text,
)
from .presentation import human_signature_text as _shared_human_signature_text
from .presentation import render_input_hints_summary as _shared_render_input_hints_summary
from .presentation import render_workflow_examples as _shared_render_workflow_examples
from .target_resolution import (
	canonicalize_describe_target_parts,
	resolve_describe_read_target,
)
from .type_annotations import format_annotation_text, format_signature_for_display


_T = get_text()


__all__ = [
	"build_cli_app",
	"describe_cmd",
	"invoke_cmd",
	"list_public_cmd",
	"version_cmd",
]


def _configure_typer_rich_output(*, no_color: bool) -> None:
	"""Align Typer's Rich help/error rendering with Moldflow CLI output settings."""
	import typer.rich_utils as rich_utils
	from rich import box

	if not hasattr(rich_utils, "_moldflow_original_panel"):
		rich_utils._moldflow_original_panel = rich_utils.Panel
		rich_utils._moldflow_original_color_system = getattr(rich_utils, "COLOR_SYSTEM", None)

	original_panel = rich_utils._moldflow_original_panel
	original_color_system = rich_utils._moldflow_original_color_system
	use_ascii = should_use_ascii_output() or should_use_ascii_output(stderr=True)

	if use_ascii:
		def _ascii_panel(*args: Any, **kwargs: Any):
			kwargs.setdefault("box", box.ASCII)
			return original_panel(*args, **kwargs)

		rich_utils.Panel = _ascii_panel
	else:
		rich_utils.Panel = original_panel

	rich_utils.COLOR_SYSTEM = None if no_color else original_color_system


def _configure_global_output_options(ctx: typer.Context, no_color: bool) -> None:
	"""Apply global CLI output settings before help/errors are rendered."""
	configure_console(no_color=no_color)
	_configure_typer_rich_output(no_color=no_color)
	ctx.color = not no_color


def _canonical_annotation_text(annotation: Any) -> str | None:
	"""Return stable, tool-friendly annotation text."""
	return format_annotation_text(annotation)


_RST_FIELD_LINE = re.compile(r"^:[A-Za-z_][\w-]*:\s*")


_MAX_FILTERED_MATCH_SUMMARY_ROWS = 10


def _normalize_human_doc(doc: str, *, obj_type: str | None) -> str:
	"""Clean doc text for terminal display without changing structured output."""
	if not doc:
		return doc
	lines = [line.rstrip() for line in doc.splitlines()]
	if obj_type == "property":
		lines = [line for line in lines if not _RST_FIELD_LINE.match(line.strip())]
	cleaned: list[str] = []
	previous_blank = False
	for line in lines:
		is_blank = not line.strip()
		if is_blank and previous_blank:
			continue
		cleaned.append(line)
		previous_blank = is_blank
	while cleaned and not cleaned[0].strip():
		cleaned.pop(0)
	while cleaned and not cleaned[-1].strip():
		cleaned.pop()
	return "\n".join(cleaned)


def _validate_describe_target_parts(target_parts: list[str], target: str) -> str:
	return canonicalize_describe_target_parts(target_parts, target=target, translate=_T)


def _validate_describe_output_modes(
	json_output: bool,
	yaml_output: bool,
	schema_output: bool,
) -> None:
	if (json_output and yaml_output) or (schema_output and (json_output or yaml_output)):
		raise typer.BadParameter(_T("Only one of --json, --yaml, or --schema may be specified."))


def _safe_describe_template_payload(target: str) -> dict[str, Any]:
	"""Best-effort invoke guidance for describe output without weakening introspection."""
	candidates = [target]
	normalized_target = target.strip()
	if normalized_target.lower().startswith(f"{CLI_ROOT_MOLDFLOW}."):
		bare_target = normalized_target.split(".", 1)[1]
		if not bare_target.lower().startswith(f"{CLI_ROOT_SYNERGY}."):
			candidates.append(f"{CLI_ROOT_SYNERGY}.{bare_target}")
			candidates.append(f"{CLI_ROOT_MOLDFLOW}.{CLI_ROOT_SYNERGY}.{bare_target}")
	elif not normalized_target.lower().startswith(f"{CLI_ROOT_SYNERGY}."):
		candidates.append(f"{CLI_ROOT_SYNERGY}.{normalized_target}")

	for candidate in candidates:
		try:
			return build_invoke_template_for_target(candidate)
		except (AttributeError, TypeError, ValueError, typer.BadParameter):
			continue

	return {
		"schema_version": SCHEMA_VERSION,
		"target": target,
		"workflow_examples": {},
		"params_json_template": {},
	}


def _human_signature_text(signature_value: str | None) -> str:
	"""Remove return annotations from human-facing signature strings."""
	return _shared_human_signature_text(signature_value)


def _structured_return_annotation(annotation: Any) -> str | None:
	"""Return a structured return-type label without Python signature punctuation."""
	if annotation is inspect.Parameter.empty or annotation is None:
		return None
	text = _canonical_annotation_text(annotation)
	if not isinstance(text, str):
		return text
	if text.strip().strip("'\"") in {"None", "NoneType"}:
		return None
	return text


def _strip_receiver_from_signature(sig_obj: inspect.Signature | None) -> inspect.Signature | None:
	"""Remove an implicit self/cls receiver from an inspect.Signature."""
	if sig_obj is None:
		return None
	params = list(sig_obj.parameters.values())
	if params and params[0].name in {"self", "cls"}:
		return sig_obj.replace(parameters=params[1:])
	return sig_obj


def _describe_signature_payload(
	obj: Any,
	sig: str,
) -> tuple[str | None, str | None, list[dict[str, Any]], list[str], dict[str, Any], str | None]:
	try:
		sig_obj = _strip_receiver_from_signature(inspect.signature(obj))
	except (TypeError, ValueError):
		sig_obj = None

	_ = sig
	signature_value = None
	return_value = None
	params: list[dict[str, Any]] = []
	required_params: list[str] = []
	properties: dict[str, Any] = {}
	obj_type: str | None = None

	if sig_obj is None:
		if isinstance(obj, property):
			obj_type = "property"
		elif not callable(obj):
			obj_type = "attribute"
		return signature_value, return_value, params, required_params, properties, obj_type

	signature_value = format_signature_for_display(sig_obj, empty_as_none=True)
	return_value = _structured_return_annotation(sig_obj.return_annotation)

	for name, param in sig_obj.parameters.items():
		annotation = _canonical_annotation_text(param.annotation)
		default_value = repr(param.default) if param.default is not inspect._empty else None
		params.append(
			{
				"name": name,
				"annotation": annotation,
				"default": default_value,
			}
		)
		properties[name] = {
			"kind": param.kind.name,
			"annotation": annotation,
			"default": default_value,
		}
		if (
			param.default is inspect._empty
			and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
		):
			required_params.append(name)

	return signature_value, return_value, params, required_params, properties, obj_type


def _build_describe_structured_output(
	*,
	normalized_target: str,
	summary_value: str | None,
	details_value: str | None,
	signature_value: str | None,
	return_value: str | None,
	params: list[dict[str, Any]],
	required_params: list[str],
	properties: dict[str, Any],
	obj_type: str | None,
	template_payload: dict[str, Any],
	schema_output: bool,
) -> dict[str, Any]:
	structured_params = list(params)
	mode = template_payload.get("mode")
	if not structured_params and mode == CLI_MODE_PROPERTY_ASSIGNMENT:
		steps = template_payload.get("steps")
		if isinstance(steps, list) and steps:
			first_step = steps[0]
			step_params = first_step.get("params") if isinstance(first_step, dict) else None
			if isinstance(step_params, list):
				for param in step_params:
					if not isinstance(param, dict):
						continue
					param_name = param.get("name")
					if not isinstance(param_name, str) or not param_name:
						continue
					structured_params.append(
						{
							"name": param_name,
							"annotation": param.get("annotation"),
							"default": param.get("default"),
							"synthetic": True,
						}
					)
	out = {
		"schema_version": SCHEMA_VERSION,
		"target": normalized_target,
		"signature": signature_value,
		"summary": summary_value,
		"params": structured_params,
		"params_json_template": template_payload.get("params_json_template", {}),
		"invoke_examples": template_payload.get("workflow_examples", {}),
	}
	next_command = _next_command_from_template_payload(template_payload)
	if isinstance(next_command, str) and next_command:
		out["next_command"] = next_command
	if details_value is not None:
		out["details"] = details_value
	if return_value is not None:
		out["returns"] = return_value
	if obj_type is not None:
		out["type"] = obj_type
	terminal_target = template_payload.get("terminal_target")
	if isinstance(terminal_target, dict):
		out["terminal_target"] = terminal_target
	if isinstance(mode, str):
		out["mode"] = mode

	if schema_output:
		return {
			"schema_version": SCHEMA_VERSION,
			"target": normalized_target,
			"type": "object",
			"required": required_params,
			"properties": properties,
			"examples": template_payload.get("workflow_examples", {}),
		}
	return out


def _next_command_from_template_payload(template_payload: dict[str, Any]) -> str | None:
	"""Return the best machine-friendly next command from a describe/template payload."""
	workflow_examples = template_payload.get("workflow_examples")
	if not isinstance(workflow_examples, dict):
		return None
	for key in (
		"cli_command",
		"preferred_cli_command",
		"read_command",
		"read_cli_command",
		"minimal_command",
		"minimal_cli_command",
	):
		value = workflow_examples.get(key)
		if isinstance(value, str) and value:
			return value
	return None


def _list_structured_rows(
	rows: list[dict[str, Any]],
	*,
	include_describe: bool,
	max_results: int | None,
) -> list[dict[str, Any]]:
	"""Return list rows optionally enriched with structured describe metadata."""
	if isinstance(max_results, int):
		rows = rows[:max_results]
	structured_rows: list[dict[str, Any]] = []
	for row in rows:
		structured_row = dict(row)
		next_command = structured_row.get("suggested_command")
		if isinstance(next_command, str) and next_command:
			structured_row["next_command"] = next_command
		if include_describe:
			describe_payload = _describe_target(str(row["target"]))
			structured_row["describe"] = _build_describe_structured_output(
				normalized_target=describe_payload["normalized_target"],
				summary_value=describe_payload["summary_value"],
				details_value=describe_payload["details_value"],
				signature_value=describe_payload["signature_value"],
				return_value=describe_payload["return_value"],
				params=describe_payload["params"],
				required_params=describe_payload["required_params"],
				properties=describe_payload["properties"],
				obj_type=describe_payload["obj_type"],
				template_payload=describe_payload["template_payload"],
				schema_output=False,
			)
		structured_rows.append(structured_row)
	return structured_rows


def version_cmd() -> None:
	"Print the installed moldflow package version."
	import moldflow

	typer.echo(moldflow.__version__)


def list_public_cmd(
	filter_: list[str] = typer.Option(
		None,
		"--filter",
		"-f",
		help=_T(
			"Filter by substring or wildcard pattern (* and ?). Repeat to keep targets matching any filter."
		),
	),
	json_output: bool = typer.Option(
		False,
		"--json",
		help=_T("Emit structured JSON for scripting or agent use."),
	),
	yaml_output: bool = typer.Option(
		False,
		"--yaml",
		help=_T("Emit structured YAML for scripting or agent use (requires PyYAML)."),
	),
	include_describe: bool = typer.Option(
		False,
		"--with-describe",
		help=_T("Include describe-style metadata for each listed target (JSON/YAML only)."),
	),
	max_results: int | None = typer.Option(
		None,
		"--max-results",
		help=_T("Limit the number of targets returned after filtering."),
	),
) -> None:
	"List directly invokable targets exported by moldflow."
	from rich.table import Table

	if json_output and yaml_output:
		raise typer.BadParameter(_T("Only one of --json or --yaml may be specified."))
	if include_describe and not (json_output or yaml_output):
		raise typer.BadParameter(_T("--with-describe requires --json or --yaml."))
	if isinstance(max_results, int) and max_results < 0:
		raise typer.BadParameter(_T("--max-results must be greater than or equal to 0."))

	rows = collect_list_rows(filter_)
	if isinstance(max_results, int):
		rows = rows[:max_results]
	has_filters = has_list_filters(filter_)
	if json_output or yaml_output:
		structured_rows = _list_structured_rows(
			rows,
			include_describe=include_describe,
			max_results=max_results,
		)
		if json_output:
			typer.echo(to_json_text(structured_rows, context="list"))
			return
		typer.echo(emit_yaml_text(structured_rows, context="list"))
		return

	console = get_console()
	with human_output_pager(console):
		table = Table(
			title=_T("Moldflow invokable targets"),
			expand=True,
			**human_table_kwargs(console),
		)
		table.add_column(_T("Target"), overflow="fold", ratio=6)
		table.add_column(_T("Type"), overflow="fold", ratio=2, min_width=13)
		for row in rows:
			table.add_row(
				human_list_target(row),
				human_list_kind(row),
			)
		console.print(table)
		if has_filters and not rows:
			message = _T("No invokable targets matched this filter.")
			if len([value for value in filter_ if value]) > 1:
				message = _T("No invokable targets matched these filters.")
			console.print(message, markup=False)
			console.print(
				_T("Try a broader --filter, or rerun list --json for canonical target strings."),
				markup=False,
			)
			return
		if any(row.get("target", "").lower().startswith(f"{CLI_ROOT_SYNERGY}.") for row in rows):
			console.print(
				_T("Targets are shown without the leading 'synergy.' prefix. Describe and invoke accept either form."),
				markup=False,
			)
		if has_filters:
			render_filtered_list_matches(console, rows)
			if len(rows) > _MAX_FILTERED_MATCH_SUMMARY_ROWS:
				console.print(
					_T(
						"Showing the compact table for {count} filtered matches. Narrow the filter or use --json for canonical target strings."
					).format(count=len(rows)),
					markup=False,
				)
		if isinstance(max_results, int) and rows:
			console.print(
				_T("Showing up to {count} targets due to --max-results.").format(count=max_results),
				markup=False,
			)
		console.print(
			_T(
				"Use describe <target> to inspect parameters, examples, and property behavior before invoking."
			),
			markup=False,
		)


def _describe_target(target: str) -> dict[str, Any]:
	"""Resolve one describe target into shared human and structured metadata."""
	resolved_target = resolve_describe_read_target(target, translate=_T)
	normalized_target = resolved_target.canonical_target
	obj = resolved_target.resolved_object
	sig = get_signature_string(obj)
	signature_value, return_value, params, required_params, properties, obj_type = _describe_signature_payload(obj, sig)
	doc = get_docstring(obj)
	human_doc = _normalize_human_doc(doc, obj_type=obj_type) if doc else doc
	structured_summary, structured_details = split_structured_doc(doc, obj_type=obj_type) if doc else (None, None)
	template_payload = _safe_describe_template_payload(normalized_target)
	return {
		"normalized_target": normalized_target,
		"signature_value": signature_value,
		"return_value": return_value,
		"params": params,
		"required_params": required_params,
		"properties": properties,
		"obj_type": obj_type,
		"human_doc": human_doc,
		"summary_value": structured_summary,
		"details_value": structured_details,
		"template_payload": template_payload,
	}


def _render_describe_target(console: Any, describe_payload: dict[str, Any]) -> None:
	"""Render one describe target in human-readable form."""
	console.print(
		f"{describe_payload['normalized_target']}{_human_signature_text(describe_payload['signature_value'])}",
		markup=False,
	)
	human_doc = describe_payload.get("human_doc")
	if human_doc:
		console.print(human_doc, markup=False)
	workflow_examples = describe_payload["template_payload"].get("workflow_examples")
	if isinstance(workflow_examples, dict):
		_render_describe_workflow_examples(console, workflow_examples)
	_render_input_hints_summary(console, describe_payload["template_payload"])


def _render_describe_workflow_examples(console: Any, workflow_examples: dict[str, Any]) -> None:
	"""Render preferred and minimal invoke examples for describe human output."""
	_shared_render_workflow_examples(
		console,
		workflow_examples,
		params_json_context="describe-example",
		minimal_params_json_context="describe-example-minimal",
	)


def _render_input_hints_summary(console: Any, payload: dict[str, Any]) -> None:
	"""Compatibility wrapper for shared input-hint rendering."""
	_shared_render_input_hints_summary(console, payload)


def describe_cmd(
	targets: list[str] = typer.Argument(
		...,
		help=_T("One or more dotted targets, for example synergy.new_project."),
	),
	json_output: bool = typer.Option(
		False,
		"--json",
		help=_T("Emit structured JSON for scripting or agent use."),
	),
	yaml_output: bool = typer.Option(
		False,
		"--yaml",
		help=_T("Emit structured YAML for scripting or agent use (requires PyYAML)."),
	),
	schema_output: bool = typer.Option(
		False,
		"--schema",
		help=_T("Emit a JSON schema-like representation of target parameters."),
	),
) -> None:
	"Show signature and documentation for one or more targets."
	_validate_describe_output_modes(json_output, yaml_output, schema_output)
	describe_payloads = [_describe_target(target) for target in targets]

	if json_output or yaml_output or schema_output:
		structured_output: dict[str, Any] | list[dict[str, Any]] = [
			_build_describe_structured_output(
				normalized_target=describe_payload["normalized_target"],
				summary_value=describe_payload["summary_value"],
				details_value=describe_payload["details_value"],
				signature_value=describe_payload["signature_value"],
				return_value=describe_payload["return_value"],
				params=describe_payload["params"],
				required_params=describe_payload["required_params"],
				properties=describe_payload["properties"],
				obj_type=describe_payload["obj_type"],
				template_payload=describe_payload["template_payload"],
				schema_output=schema_output,
			)
			for describe_payload in describe_payloads
		]
		if len(structured_output) == 1:
			structured_output = structured_output[0]
		if json_output or schema_output:
			context = "describe-schema" if schema_output else "describe"
			typer.echo(to_json_text(structured_output, context=context))
		else:
			typer.echo(emit_yaml_text(structured_output, context="describe"))
		return

	console = get_console()
	with human_output_pager(console):
		for index, describe_payload in enumerate(describe_payloads):
			if index:
				console.print()
			_render_describe_target(console, describe_payload)


def build_cli_app():
	configure_console(no_color=False)
	_configure_typer_rich_output(no_color=False)
	app = typer.Typer(
		help=_T(
			"Moldflow command-line interface.\n\n"
			"Start with 'list' to discover targets, 'describe <target>' to inspect usage, "
			"then 'invoke <target> ...' to run it."
		)
	)

	@app.callback()
	def _cli_callback(
		ctx: typer.Context,
		no_color: bool = typer.Option(
			False,
			"--no-color",
			help=_T("Disable ANSI color/styling in CLI output."),
			is_eager=True,
		),
	) -> None:
		"""Apply global CLI options before dispatching subcommands."""
		_configure_global_output_options(ctx, no_color)

	app.command("version", help=_T("Print the installed moldflow package version."))(version_cmd)
	app.command(
		"list",
		help=_T("Discover invokable targets and the next command to run for each one."),
	)(
		list_public_cmd
	)
	app.command(
		"describe",
		help=_T("Inspect a target's signature, docs, examples, and structured invoke template."),
	)(describe_cmd)
	app.command(
		"invoke",
		help=_T(
			"Run a Moldflow target with named parameters or JSON input. Bare targets are treated as synergy.<target>."
		),
	)(invoke_cmd)
	return app

