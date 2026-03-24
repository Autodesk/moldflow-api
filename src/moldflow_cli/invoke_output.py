# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Callable, Optional

import typer

from .constants import CLI_KIND_PROPERTY, CLI_KIND_PROPERTY_GETTER
from .output_utils import (
	human_output_pager,
	human_table_kwargs,
	render_serialized_value,
	to_json_text,
)
from .presentation import human_signature_text as _shared_human_signature_text
from moldflow.i18n import get_text


_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _build_invoke_envelope(
	result: Any,
	*,
	schema_version: str,
	serialize_result: Callable[[Any], Any],
) -> dict[str, Any]:
	"""Create stable JSON envelope for invoke results."""
	ok = bool(result) if isinstance(result, bool) else True
	envelope = {
		"schema_version": schema_version,
		"ok": ok,
		"result_type": type(result).__name__ if result is not None else "NoneType",
		"result": serialize_result(result),
	}
	if isinstance(result, bool) and result is False:
		envelope["diagnostics"] = [
			_T("The target returned False, which indicates a business-level failure.")
		]
	return envelope


def _render_invoke_result(
	console: Any,
	result: Any,
	json_output: bool,
	json_file_output: Optional[str],
	*,
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
	envelope = build_invoke_envelope(result)
	serializable_result = envelope
	if json_file_output:
		try:
			with open(json_file_output, "w", encoding="utf-8") as output_file:
				output_file.write(to_json_text(serializable_result, context="invoke", default=str))
		except (OSError, TypeError, ValueError) as exc:
			raise typer.BadParameter(
				_tr("Cannot write JSON file '{path}': {error}", path=json_file_output, error=exc)
			) from exc

	if json_output:
		typer.echo(to_json_text(serializable_result, context="invoke", default=str))
		return envelope
	with human_output_pager(console):
		render_serialized_value(console, envelope["result"], context="invoke-human")
		for diagnostic in envelope.get("diagnostics", []):
			console.print(diagnostic, markup=False)
		if json_file_output:
			_emit_json_file_written_notice(console, json_file_output)
	return envelope


def _emit_structured_json(
	payload: Any,
	*,
	context: str,
	json_file_output: Optional[str],
	emit_stdout: bool = True,
) -> None:
	json_text = to_json_text(payload, context=context, default=str)
	if json_file_output:
		try:
			with open(json_file_output, "w", encoding="utf-8") as output_file:
				output_file.write(json_text)
		except (OSError, TypeError, ValueError) as exc:
			raise typer.BadParameter(
				_tr("Cannot write JSON file '{path}': {error}", path=json_file_output, error=exc)
			) from exc
	if emit_stdout:
		typer.echo(json_text)


def _emit_json_file_written_notice(console: Any, json_file_output: str) -> None:
	"""Tell human-mode users where the structured payload was written."""
	console.print(
		_T("Wrote structured output to {path}.").format(path=json_file_output),
		markup=False,
	)


def _build_dry_run_template_command(payload: dict[str, Any]) -> str | None:
	"""Build a compact placeholder command summary for dry-run human output."""
	target = payload.get("target")
	if not isinstance(target, str) or not target:
		return None
	steps = payload.get("steps")
	if not isinstance(steps, list):
		return f"invoke {target}"
	command_parts = ["invoke", target]
	multi_step = len(steps) > 1
	for step in steps:
		if not isinstance(step, dict):
			continue
		step_name = step.get("name")
		params = step.get("params")
		if not isinstance(params, list):
			continue
		for param in params:
			if isinstance(param, dict):
				param_name = param.get("name")
				param_kind = param.get("kind")
				if param_kind in {"VAR_POSITIONAL", "VAR_KEYWORD"}:
					continue
			elif isinstance(param, str):
				param_name = param
			else:
				continue
			if not isinstance(param_name, str) or not param_name:
				continue
			prefix = f"{step_name}." if multi_step and isinstance(step_name, str) and step_name else ""
			command_parts.append(f"{prefix}{param_name}=<{param_name}>")
	return " ".join(command_parts)


def _render_dry_run_human_output(console: Any, payload: dict[str, Any]) -> None:
	console.print(
		_T("Dry run for {target}").format(target=payload.get("target", "<unknown>")),
		markup=False,
	)
	template_command = _build_dry_run_template_command(payload)
	if isinstance(template_command, str) and template_command:
		console.print(_T("Template summary:"), markup=False)
		console.print(template_command, markup=False)
	terminal_target = payload.get("terminal_target")
	if isinstance(terminal_target, dict) and terminal_target.get("kind") in {CLI_KIND_PROPERTY, CLI_KIND_PROPERTY_GETTER}:
		assignment = terminal_target.get("assignment") is True
		if assignment:
			console.print(_T("This dry run validates a property assignment."), markup=False)
		else:
			console.print(_T("This property is read-only and takes no arguments."), markup=False)
	steps = payload.get("steps")
	if isinstance(steps, list) and steps:
		show_steps = len(steps) > 1 or any(
			isinstance(step, dict) and bool(step.get("deferred")) for step in steps
		)
		if show_steps:
			console.print(_T("Planned steps:"), markup=False)
			for step in steps:
				if isinstance(step, dict):
					name = step.get("name", "<step>")
					signature = _shared_human_signature_text(step.get("signature", "(...)")) or "(...)"
					if step.get("deferred"):
						console.print(f"- {name} [deferred] {signature}", markup=False)
					else:
						console.print(f"- {name}{signature}", markup=False)
	assignment = payload.get("assignment")
	if isinstance(assignment, dict) and assignment:
		console.print(_T("Resolved assignment:"), markup=False)
		console.print(to_json_text(assignment, context="invoke-dry-run-assignment"), markup=False)
	kwargs_per_step = payload.get("kwargs_per_step")
	if kwargs_per_step:
		console.print(_T("Resolved kwargs:"), markup=False)
		console.print(to_json_text(kwargs_per_step, context="invoke-dry-run-human"), markup=False)


def _render_batch_human_output(console: Any, payload: dict[str, Any]) -> None:
	from rich.table import Table

	summary = payload.get("summary") if isinstance(payload, dict) else None
	if isinstance(summary, dict):
		console.print(
			_T("Batch summary: {succeeded}/{total} succeeded, {failed} failed.").format(
				succeeded=summary.get("succeeded", 0),
				total=summary.get("total", 0),
				failed=summary.get("failed", 0),
			),
			markup=False,
		)
	table = Table(title=_T("Batch results"), **human_table_kwargs(console))
	table.add_column(_T("Index"))
	table.add_column(_T("Target"))
	table.add_column(_T("Status"))
	table.add_column(_T("Detail"))
	for result in payload.get("batch_results", []):
		if not isinstance(result, dict):
			continue
		status = _T("ok") if result.get("ok") else _T("failed")
		detail = result.get("result_type") or result.get("error_type") or ""
		table.add_row(
			str(result.get("index", "")),
			str(result.get("target", "")),
			status,
			str(detail),
		)
	console.print(table)
	for result in payload.get("batch_results", []):
		if isinstance(result, dict) and result.get("ok") is False and result.get("error"):
			console.print(
				_T("Batch item {index} error: {error}").format(
					index=result.get("index", "?"),
					error=result.get("error"),
				),
				markup=False,
			)


def _emit_structured_or_human(
	*,
	console: Any,
	payload: dict[str, Any],
	context: str,
	json_output: bool,
	json_file_output: Optional[str],
	human_renderer: Callable[[Any, dict[str, Any]], None],
) -> None:
	_emit_structured_json(
		payload,
		context=context,
		json_file_output=json_file_output,
		emit_stdout=json_output,
	)
	if not json_output:
		with human_output_pager(console):
			human_renderer(console, payload)
			if json_file_output:
				_emit_json_file_written_notice(console, json_file_output)
