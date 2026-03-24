# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any

from moldflow.i18n import get_text

from .output_utils import print_wrapped_command, to_json_text


_T = get_text()


def human_signature_text(signature: str | None) -> str:
	"""Remove return annotations from human-facing signature strings."""
	if not isinstance(signature, str) or not signature:
		return ""
	return signature.rsplit(" -> ", 1)[0]


def render_workflow_examples(
	console: Any,
	workflow_examples: dict[str, Any],
	*,
	params_json_context: str,
	minimal_params_json_context: str,
) -> None:
	"""Render preferred and minimal workflow examples for human CLI output."""
	read_command = workflow_examples.get("read_command") or workflow_examples.get("read_cli_command")
	primary_command = workflow_examples.get("cli_command") or workflow_examples.get("preferred_cli_command")
	minimal_command = workflow_examples.get("minimal_command") or workflow_examples.get("minimal_cli_command")
	if isinstance(read_command, str) and read_command and read_command != primary_command:
		console.print(_T("Read current value:"), markup=False)
		print_wrapped_command(console, read_command)
	if isinstance(primary_command, str) and primary_command:
		primary_label = _T("Set it with:") if read_command else _T("Try this:")
		console.print(primary_label, markup=False)
		print_wrapped_command(console, primary_command)
	if isinstance(minimal_command, str) and minimal_command and minimal_command != primary_command:
		minimal_label = _T("Shorter form:")
		console.print(minimal_label, markup=False)
		print_wrapped_command(console, minimal_command)
	primary_params_json = workflow_examples.get("params_json") or workflow_examples.get("preferred_params_json")
	if isinstance(primary_params_json, dict) and primary_params_json:
		console.print(_T("JSON example:"), markup=False)
		console.print(to_json_text(primary_params_json, context=params_json_context), markup=False)
	minimal_params_json = workflow_examples.get("minimal_params_json")
	if (
		isinstance(minimal_params_json, dict)
		and minimal_params_json
		and minimal_params_json != primary_params_json
	):
		console.print(_T("Shorter JSON example:"), markup=False)
		console.print(
			to_json_text(minimal_params_json, context=minimal_params_json_context),
			markup=False,
		)
	for note in workflow_examples.get("notes", []):
		if isinstance(note, str):
			console.print(note, markup=False)


def render_input_hints_summary(console: Any, payload: dict[str, Any]) -> None:
	"""Render wrapper-specific input hints for human describe and template flows."""
	steps = payload.get("steps")
	if not isinstance(steps, list) or not steps:
		return
	multi_step = len(steps) > 1
	rendered_header = False
	for step in steps:
		if not isinstance(step, dict):
			continue
		step_name = step.get("name")
		params = step.get("params")
		if not isinstance(params, list):
			continue
		for param in params:
			if not isinstance(param, dict):
				continue
			param_name = param.get("name")
			input_hints = param.get("input_hints")
			if not isinstance(param_name, str) or not isinstance(input_hints, dict):
				continue
			wrapper_type = input_hints.get("wrapper_type")
			examples = input_hints.get("examples") if isinstance(input_hints.get("examples"), dict) else {}
			preferred_non_json = examples.get("preferred_non_json")
			explicit_field_non_json = examples.get("explicit_field_non_json")
			preferred_params_json = examples.get("preferred_params_json")
			if not any(
				isinstance(value, (str, dict)) and bool(value)
				for value in (preferred_non_json, explicit_field_non_json, preferred_params_json)
			):
				continue
			if not rendered_header:
				console.print(_T("Input hints:"), markup=False)
				rendered_header = True
			label = param_name
			if multi_step and isinstance(step_name, str) and step_name:
				label = f"{step_name}.{param_name}"
			if isinstance(wrapper_type, str) and wrapper_type:
				console.print(
					"{label} ({wrapper_type}):".format(
						label=label,
						wrapper_type=wrapper_type,
					),
					markup=False,
				)
			else:
				console.print("{label}:".format(label=label), markup=False)
			if isinstance(preferred_params_json, dict) and preferred_params_json:
				console.print(_T("JSON value:"), markup=False)
				console.print(
					to_json_text(preferred_params_json, context="input-hint"),
					markup=False,
				)
			if isinstance(preferred_non_json, str) and preferred_non_json:
				console.print(_T("CLI argument: {value}").format(value=preferred_non_json), markup=False)
			if (
				isinstance(explicit_field_non_json, str)
				and explicit_field_non_json
				and explicit_field_non_json != preferred_non_json
			):
				console.print(
					_T("Explicit field form: {value}").format(value=explicit_field_non_json),
					markup=False,
				)