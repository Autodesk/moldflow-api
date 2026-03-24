# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from copy import deepcopy
from functools import partial
from typing import Any, Callable, List, Optional

import typer

from .invoke_binding import (
	_annotation_allows_none,
	_bucket_items_by_step,
	_build_kwargs_per_step,
	_parse_invoke_items,
	_parse_terminal_property_assignment_value,
)
from .invoke_batching import (
	_build_batch_summary,
	_load_batch_payload,
	_run_batch_invoke as _run_batched_calls,
	_validate_batch_mode_inputs,
)
from .invoke_engine import (
	_PlannedInvokeCall,
	_PlannedPropertyAssignment,
	_ResolvedInvokeTarget,
	_invoke_single_target as _invoke_single_target_engine,
)
from .invoke_output import (
	_emit_structured_or_human,
	_render_batch_human_output,
	_render_dry_run_human_output,
	_render_invoke_result,
)
from .invoke_planning import (
	_build_dry_run_method_plan as _build_dry_run_method_plan_base,
	_make_resolved_invoke_read_target as _make_resolved_invoke_read_target_base,
	_plan_invoke_method_call as _plan_invoke_method_call_base,
	_resolve_invoke_read_target as _resolve_invoke_read_target_base,
	_summarize_steps as _summarize_steps_base,
	_terminal_property_wrapper_class as _terminal_property_wrapper_class_base,
	build_invoke_template_for_target as _build_invoke_template_for_target_base,
)
from .invoke_terminal import (
	_assign_terminal_property_target as _assign_terminal_property_target_base,
	_build_property_assignment_plan as _build_property_assignment_plan_base,
	_dispatch_terminal_invoke_target as _dispatch_terminal_invoke_target_base,
	_execute_planned_property_assignment as _execute_planned_property_assignment_base,
	_plan_property_assignment as _plan_property_assignment_base,
	_property_assignment_plan_payload as _property_assignment_plan_payload_base,
	_resolve_property_assignment_owner as _resolve_property_assignment_owner_base,
)
from .invoke_serialization import (
	_build_invoke_envelope as _build_invoke_envelope_serialization_base,
	_serialize_trace_payload as _serialize_trace_payload_base,
	_to_serializable,
)
from .invoke_resolution import (
	_canonicalize_invoke_target,
	_resolve_invoke_steps,
	_resolve_return_class,
)
from .invoke_runtime import (
	_execute_invoke_chain,
)
from .invoke_templates import (
	_apply_step_doc_fields as _apply_step_doc_fields_base,
	_build_invoke_template as _build_invoke_template_base,
	_build_property_target_template as _build_property_target_template_base,
	_format_step_signature as _format_step_signature_base,
	_property_return_wrapper_class as _property_return_wrapper_class_base,
	_target_doc_fields_from_obj as _target_doc_fields_from_obj_base,
)
from .invoke_trace import (
	_emit_batch_invoke_trace,
	_emit_invoke_trace_event,
)
from .output_utils import (
	get_console,
)
from .presentation import render_input_hints_summary as _shared_render_input_hints_summary
from .presentation import render_workflow_examples as _shared_render_workflow_examples
from .target_resolution import (
	ResolvedInvokeReadTarget,
	resolve_target_for_introspection,
)
from moldflow.i18n import get_text


SCHEMA_VERSION = "1.0"
ParsedItem = tuple[list[str], Any, str]
MethodStep = dict[str, Any]
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _example_scalar_value(annotation_text: str | None, param_name: str) -> Any:
	normalized = (annotation_text or "").lower()
	name_lower = param_name.lower()
	if "bool" in normalized:
		return True
	if "int" in normalized:
		return 1
	if any(token in normalized for token in ("float", "double")):
		return 1.0
	if name_lower == "path" or name_lower.endswith("_path"):
		return f"<{param_name}>"
	if "path" in name_lower:
		return f"<{param_name}>"
	return f"<{param_name}>"


def _example_cli_value(annotation_text: str | None, param_name: str) -> str:
	value = _example_scalar_value(annotation_text, param_name)
	return str(value).lower() if isinstance(value, bool) else str(value)


def _example_param_values(
	*,
	step_name: str,
	param_name: str,
	annotation_text: str | None,
	input_hints: dict[str, Any] | None,
	multi_step: bool,
) -> tuple[str | None, Any | None]:
	examples = input_hints.get("examples") if isinstance(input_hints, dict) else None
	preferred_non_json = examples.get("preferred_non_json") if isinstance(examples, dict) else None
	preferred_params_json = examples.get("preferred_params_json") if isinstance(examples, dict) else None
	cli_arg: str
	if isinstance(preferred_non_json, str) and preferred_non_json:
		cli_arg = preferred_non_json
	else:
		cli_prefix = f"{step_name}." if multi_step else ""
		cli_arg = f"{cli_prefix}{param_name}={_example_cli_value(annotation_text, param_name)}"
	if multi_step and not cli_arg.startswith(f"{step_name}."):
		cli_arg = f"{step_name}.{cli_arg}"
	if isinstance(preferred_params_json, dict) and preferred_params_json:
		if param_name in preferred_params_json:
			return cli_arg, preferred_params_json[param_name]
		if len(preferred_params_json) == 1:
			return cli_arg, next(iter(preferred_params_json.values()))
	return cli_arg, _example_scalar_value(annotation_text, param_name)


def _is_variadic_param_kind(kind: str | None) -> bool:
	return kind in {"VAR_POSITIONAL", "VAR_KEYWORD"}


def _include_param_in_example(param: dict[str, Any], *, include_optional: bool) -> bool:
	if _is_variadic_param_kind(param.get("kind")):
		return False
	if bool(param.get("required")):
		return True
	return include_optional


def _build_example_payload(
	*,
	steps: list[dict[str, Any]],
	include_optional: bool,
) -> tuple[list[str], dict[str, Any]]:
	multi_step = len(steps) > 1
	cli_args: list[str] = []
	params_json: dict[str, Any] = {}
	for step in steps:
		step_json: dict[str, Any] = {}
		for param in step.get("params", []):
			if not _include_param_in_example(param, include_optional=include_optional):
				continue
			cli_arg, json_value = _example_param_values(
				step_name=step["name"],
				param_name=param["name"],
				annotation_text=param.get("annotation"),
				input_hints=param.get("input_hints")
				if isinstance(param.get("input_hints"), dict)
				else None,
				multi_step=multi_step,
			)
			if cli_arg is not None:
				cli_args.append(cli_arg)
			if json_value is not None:
				step_json[param["name"]] = json_value
		if multi_step:
			params_json[step["name"]] = step_json
		else:
			params_json.update(step_json)
	return cli_args, params_json


def _build_workflow_examples(
	*,
	target: str,
	steps: list[dict[str, Any]],
	mode: str,
) -> dict[str, Any]:
	multi_step = len(steps) > 1
	minimal_cli_args, minimal_params_json = _build_example_payload(
		steps=steps,
		include_optional=False,
	)
	preferred_cli_args, preferred_params_json = _build_example_payload(
		steps=steps,
		include_optional=True,
	)
	command = f"invoke {target}"
	minimal_command = command
	preferred_command = command
	if minimal_cli_args:
		minimal_command = f"{command} {' '.join(minimal_cli_args)}"
	if preferred_cli_args:
		preferred_command = f"{command} {' '.join(preferred_cli_args)}"
	workflow_examples: dict[str, Any] = {
		"mode": mode,
		"cli_command": preferred_command,
		"cli_args": preferred_cli_args,
	}
	if preferred_params_json:
		workflow_examples["params_json"] = deepcopy(preferred_params_json)
	if minimal_cli_args and minimal_command != preferred_command:
		workflow_examples["minimal_command"] = minimal_command
		workflow_examples["minimal_args"] = minimal_cli_args
	if minimal_params_json and minimal_params_json != preferred_params_json:
		workflow_examples["minimal_params_json"] = deepcopy(minimal_params_json)
	if multi_step:
		workflow_examples["notes"] = [
			_T("For multi-step targets, group params-json fields by step name."),
		]
	return workflow_examples

def _property_return_wrapper_class(
	raw_attr: property,
	cli_to_class: dict[str, type],
) -> type | None:
	return _property_return_wrapper_class_base(
		raw_attr,
		cli_to_class,
		resolve_return_class=_resolve_return_class,
	)


def _build_property_target_template(
	*,
	target: str,
	property_name: str,
	raw_attr: property,
	cli_to_class: dict[str, type],
) -> dict[str, Any]:
	return _build_property_target_template_base(
		target=target,
		property_name=property_name,
		raw_attr=raw_attr,
		cli_to_class=cli_to_class,
		resolve_return_class=_resolve_return_class,
		annotation_allows_none=_annotation_allows_none,
		build_workflow_examples=_build_workflow_examples,
		schema_version=SCHEMA_VERSION,
	)


def _apply_step_doc_fields(step_payload: dict[str, Any], *, callable_obj: Any, obj_type: str | None = None) -> None:
	return _apply_step_doc_fields_base(step_payload, callable_obj=callable_obj, obj_type=obj_type)


def _target_doc_fields_from_obj(obj: Any, *, obj_type: str | None = None) -> tuple[str | None, str | None]:
	return _target_doc_fields_from_obj_base(obj, obj_type=obj_type)


def _assign_terminal_property_target(
	*,
	parts: list[str],
	cli_to_class: dict[str, type],
	call_target: str,
	property_name: str,
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	trace_hook: Any | None,
) -> Any:
	"""Assign a value to a terminal property target and return the updated value."""
	return _assign_terminal_property_target_base(
		parts=parts,
		cli_to_class=cli_to_class,
		call_target=call_target,
		property_name=property_name,
		raw_args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		trace_hook=trace_hook,
		parse_terminal_property_assignment_value=_parse_terminal_property_assignment_value,
		execute_invoke_chain=_execute_invoke_chain,
	)


def _build_property_assignment_plan(
	*,
	call_target: str,
	property_name: str,
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
) -> dict[str, Any]:
	return _build_property_assignment_plan_base(
		call_target=call_target,
		property_name=property_name,
		raw_args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		parse_terminal_property_assignment_value=_parse_terminal_property_assignment_value,
		build_invoke_template_for_target=build_invoke_template_for_target,
		to_serializable=_to_serializable,
		schema_version=SCHEMA_VERSION,
		execute_invoke_chain=_execute_invoke_chain,
	)


def _plan_property_assignment(
	*,
	call_target: str,
	invoke_target: _ResolvedInvokeTarget,
	property_name: str,
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
) -> _PlannedPropertyAssignment:
	return _plan_property_assignment_base(
		call_target=call_target,
		invoke_target=invoke_target,
		property_name=property_name,
		raw_args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		parse_terminal_property_assignment_value=_parse_terminal_property_assignment_value,
		execute_invoke_chain=_execute_invoke_chain,
	)


def _property_assignment_plan_payload(
	planned_assignment: _PlannedPropertyAssignment,
) -> dict[str, Any]:
	return _property_assignment_plan_payload_base(
		planned_assignment,
		build_invoke_template_for_target=build_invoke_template_for_target,
		to_serializable=_to_serializable,
		schema_version=SCHEMA_VERSION,
	)


def _resolve_property_assignment_owner(
	*,
	invoke_target: _ResolvedInvokeTarget,
	call_target: str,
	property_name: str,
	trace_hook: Any | None,
) -> tuple[Any, property]:
	return _resolve_property_assignment_owner_base(
		invoke_target=invoke_target,
		call_target=call_target,
		property_name=property_name,
		trace_hook=trace_hook,
		execute_invoke_chain=_execute_invoke_chain,
	)


def _execute_planned_property_assignment(
	planned_assignment: _PlannedPropertyAssignment,
	*,
	trace_hook: Any | None,
) -> Any:
	return _execute_planned_property_assignment_base(
		planned_assignment,
		trace_hook=trace_hook,
		execute_invoke_chain=_execute_invoke_chain,
	)
def _build_invoke_envelope(result: Any) -> dict[str, Any]:
	return _build_invoke_envelope_serialization_base(result, schema_version=SCHEMA_VERSION)


def _serialize_trace_payload(payload: Any) -> Any:
	return _serialize_trace_payload_base(payload, schema_version=SCHEMA_VERSION)


def _format_step_signature(signature: Any) -> str:
	return _format_step_signature_base(signature)


def _build_invoke_template(target: str, method_steps: list[MethodStep]) -> dict[str, Any]:
	return _build_invoke_template_base(
		target,
		method_steps,
		annotation_allows_none=_annotation_allows_none,
		build_workflow_examples=_build_workflow_examples,
		schema_version=SCHEMA_VERSION,
	)


def _make_resolved_invoke_read_target(
	*,
	requested_target: str,
	invoke_target: _ResolvedInvokeTarget,
) -> ResolvedInvokeReadTarget:
	return _make_resolved_invoke_read_target_base(
		requested_target=requested_target,
		invoke_target=invoke_target,
		resolve_target_for_introspection=resolve_target_for_introspection,
	)


def _resolve_invoke_read_target(target: str) -> ResolvedInvokeReadTarget:
	return _resolve_invoke_read_target_base(
		target,
		resolve_invoke_steps=_resolve_invoke_steps,
		resolve_target_for_introspection=resolve_target_for_introspection,
	)


def build_invoke_template_for_target(target: str) -> dict[str, Any]:
	"""Build template metadata for a target, including terminal property targets."""
	return _build_invoke_template_for_target_base(
		target,
		resolve_invoke_read_target=_resolve_invoke_read_target,
		build_invoke_template=_build_invoke_template,
		target_doc_fields_from_obj=_target_doc_fields_from_obj,
		build_property_target_template=_build_property_target_template,
		schema_version=SCHEMA_VERSION,
	)


def _terminal_property_wrapper_class(
	resolved_target: ResolvedInvokeReadTarget,
) -> type | None:
	return _terminal_property_wrapper_class_base(
		resolved_target,
		property_return_wrapper_class=_property_return_wrapper_class,
	)


def _summarize_steps(method_steps: list[MethodStep]) -> list[dict[str, Any]]:
	return _summarize_steps_base(
		method_steps,
		format_step_signature=_format_step_signature,
		apply_step_doc_fields=lambda payload, callable_obj: _apply_step_doc_fields(
			payload,
			callable_obj=callable_obj,
		),
	)


def _plan_invoke_method_call(
	*,
	call_target: str,
	invoke_target: _ResolvedInvokeTarget,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
	dry_run: bool,
) -> _PlannedInvokeCall:
	return _plan_invoke_method_call_base(
		call_target=call_target,
		invoke_target=invoke_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		dry_run=dry_run,
		parse_invoke_items=_parse_invoke_items,
		bucket_items_by_step=_bucket_items_by_step,
		build_kwargs_per_step=_build_kwargs_per_step,
		summarize_steps=_summarize_steps,
	)


def _build_dry_run_method_plan(planned_call: _PlannedInvokeCall) -> dict[str, Any]:
	return _build_dry_run_method_plan_base(
		planned_call,
		build_invoke_template_for_target=build_invoke_template_for_target,
		serialize_value=_to_serializable,
		schema_version=SCHEMA_VERSION,
	)


def _dispatch_terminal_invoke_target(
	*,
	call_target: str,
	invoke_target: _ResolvedInvokeTarget,
	resolved_target: ResolvedInvokeReadTarget,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
	dry_run: bool,
	trace_hook: Any | None,
) -> Any:
	return _dispatch_terminal_invoke_target_base(
		call_target=call_target,
		invoke_target=invoke_target,
		resolved_target=resolved_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		dry_run=dry_run,
		trace_hook=trace_hook,
		terminal_property_wrapper_class=_terminal_property_wrapper_class,
		parse_terminal_property_assignment_value=_parse_terminal_property_assignment_value,
		build_invoke_template_for_target=build_invoke_template_for_target,
		to_serializable=_to_serializable,
		schema_version=SCHEMA_VERSION,
		execute_invoke_chain=_execute_invoke_chain,
		build_invoke_envelope=_build_invoke_envelope,
	)


def _invoke_single_target(
	call_target: str,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
	batch_index: Optional[int] = None,
	*,
	dry_run: bool,
	trace_enabled: bool,
	trace_state: dict[str, int],
) -> Any:
	return _invoke_single_target_engine(
		call_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		batch_index=batch_index,
		dry_run=dry_run,
		trace_enabled=trace_enabled,
		trace_state=trace_state,
		canonicalize_invoke_target=_canonicalize_invoke_target,
		serialize_trace_payload=_serialize_trace_payload,
		schema_version=SCHEMA_VERSION,
		resolve_invoke_steps=_resolve_invoke_steps,
		make_resolved_invoke_read_target=_make_resolved_invoke_read_target,
		dispatch_terminal_invoke_target=_dispatch_terminal_invoke_target,
		plan_invoke_method_call=_plan_invoke_method_call,
		build_dry_run_method_plan=_build_dry_run_method_plan,
		execute_invoke_chain=_execute_invoke_chain,
		build_invoke_envelope=_build_invoke_envelope,
	)


def _render_workflow_example_summary(console: Any, workflow_examples: dict[str, Any]) -> None:
	_shared_render_workflow_examples(
		console,
		workflow_examples,
		params_json_context="invoke-workflow-example",
		minimal_params_json_context="invoke-workflow-example-minimal",
	)


def _render_input_hints_summary(console: Any, payload: dict[str, Any]) -> None:
	"""Render wrapper-specific input hints for human describe/template flows."""
	_shared_render_input_hints_summary(console, payload)


def _build_batch_trace_emitter(
	*,
	trace_enabled: bool,
	trace_state: dict[str, int],
) -> Callable[[int, str | None, str, dict[str, Any]], None] | None:
	if not trace_enabled:
		return None
	return partial(
		_emit_batch_invoke_trace,
		emit_invoke_trace_event=partial(
			_emit_invoke_trace_event,
			serialize_payload=_serialize_trace_payload,
			schema_version=SCHEMA_VERSION,
		),
		trace_enabled=trace_enabled,
		trace_state=trace_state,
	)


def _run_batch_invoke_request(
	*,
	batch_payload: list[Any],
	dry_run: bool,
	fail_on_false: bool,
	trace_enabled: bool,
	trace_state: dict[str, int],
) -> tuple[list[dict[str, Any]], bool]:
	return _run_batched_calls(
		batch_payload=batch_payload,
		invoke_once=partial(
			_invoke_single_target,
			dry_run=dry_run,
			trace_enabled=trace_enabled,
			trace_state=trace_state,
		),
		dry_run=dry_run,
		fail_on_false=fail_on_false,
		build_invoke_envelope=_build_invoke_envelope,
		emit_batch_trace=_build_batch_trace_emitter(
			trace_enabled=trace_enabled,
			trace_state=trace_state,
		),
	)


def _handle_batch_invoke_mode(
	*,
	console: Any,
	batch_file: str,
	target: Optional[str],
	args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	dry_run: bool,
	fail_on_false: bool,
	trace_enabled: bool,
	trace_state: dict[str, int],
	json_output: bool,
	json_file_output: Optional[str],
	translate: Any,
) -> None:
	_validate_batch_mode_inputs(
		target=target,
		args=args,
		json_input=json_input,
		json_file_input=json_file_input,
		translate=translate,
	)
	batch_payload = _load_batch_payload(batch_file)
	results, any_error = _run_batch_invoke_request(
		batch_payload=batch_payload,
		dry_run=dry_run,
		fail_on_false=fail_on_false,
		trace_enabled=trace_enabled,
		trace_state=trace_state,
	)
	_emit_structured_or_human(
		console=console,
		payload={
			"schema_version": SCHEMA_VERSION,
			"summary": _build_batch_summary(results),
			"batch_results": results,
		},
		context="invoke-batch",
		json_output=json_output,
		json_file_output=json_file_output,
		human_renderer=_render_batch_human_output,
	)
	if any_error:
		raise typer.Exit(code=1)


def _handle_single_invoke_mode(
	*,
	console: Any,
	target: Optional[str],
	args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	dry_run: bool,
	fail_on_false: bool,
	trace_enabled: bool,
	trace_state: dict[str, int],
	json_output: bool,
	json_file_output: Optional[str],
	translate: Any,
) -> None:
	if target is None:
		raise typer.BadParameter(translate("TARGET is required unless --batch-file is used."))
	result = _invoke_single_target(
		target,
		args,
		json_input,
		json_file_input,
		dry_run=dry_run,
		trace_enabled=trace_enabled,
		trace_state=trace_state,
	)
	if dry_run:
		_emit_structured_or_human(
			console=console,
			payload=result,
			context="invoke-dry-run",
			json_output=json_output,
			json_file_output=json_file_output,
			human_renderer=_render_dry_run_human_output,
		)
		return
	envelope = _render_invoke_result(
		console,
		result,
		json_output,
		json_file_output,
		build_invoke_envelope=_build_invoke_envelope,
	)
	if fail_on_false and envelope["ok"] is False:
		raise typer.Exit(code=1)


def invoke_cmd(
	target: Optional[str] = typer.Argument(
		None,
		help=_T(
			"Dotted path to a method or function, optionally chained, for example 'synergy.new_project' or 'synergy.plot_manager.find_plot_by_name'."
		),
	),
	args: List[str] = typer.Argument(
		None,
		help=_T(
			"Duplicate/conflicting paths are rejected. Arguments are passed as key=value or "
			"param.attr=value. For chained targets, prefix the parameter with the method name, "
			"e.g. find_plot_by_name.plot_name=\"My Plot\". Nested routing uses step.param.attr=value "
			"(param=1 conflicts with param.attr=2). Methods with positional-only parameters are "
			"not supported by named CLI routing."
		),
	),
	json_input: Optional[str] = typer.Option(
		None,
		"--params-json",
		help=_T(
			"JSON object containing parameter mappings (overrides positional args). Top-level arrays/scalars are not allowed."
		),
	),
	json_file_input: Optional[str] = typer.Option(
		None,
		"--params-json-file",
		"-J",
		help=_T(
			"Path to a JSON file containing parameter mappings (overrides positional args). The top-level payload must be an object, not arrays/scalars."
		),
	),
	json_output: bool = typer.Option(
		False,
		"--json",
		"--json-output",
		help=_T(
			"Emit structured result JSON to stdout. Use --json as the canonical flag; "
			"--json-output is a legacy alias kept for compatibility."
		),
	),
	json_file_output: Optional[str] = typer.Option(
		None,
		"--json-file-output",
		help=_T("Write JSON output to the given file path without changing stdout mode."),
	),
	dry_run: bool = typer.Option(
		False,
		"--dry-run",
		help=_T("Parse/validate/build kwargs and emit a template summary call plan without executing invoke steps."),
	),
	batch_file: Optional[str] = typer.Option(
		None,
		"--batch-file",
		help=_T("Path to a JSON file containing an array of invoke calls for batch execution."),
	),
	trace: bool = typer.Option(
		False,
		"--trace",
		help=_T("Emit line-delimited JSON trace events to stderr for target resolution and runtime invoke binding."),
	),
	fail_on_false: bool = typer.Option(
		True,
		"--fail-on-false/--no-fail-on-false",
		help=_T(
			"Treat False return values as CLI failures (exit 1). This is enabled by default for automation-friendly behavior."
		),
	),
) -> None:
	"Invoke a moldflow target with named parameters."
	_ = get_text()
	console = get_console()
	trace_state = {"sequence": 0}
	raw_args: list[str] = args or []

	if batch_file is not None:
		_handle_batch_invoke_mode(
			console=console,
			batch_file=batch_file,
			target=target,
			args=raw_args,
			json_input=json_input,
			json_file_input=json_file_input,
			dry_run=dry_run,
			fail_on_false=fail_on_false,
			trace_enabled=trace,
			trace_state=trace_state,
			json_output=json_output,
			json_file_output=json_file_output,
			translate=_,
		)
		return

	_handle_single_invoke_mode(
		console=console,
		target=target,
		args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		dry_run=dry_run,
		fail_on_false=fail_on_false,
		trace_enabled=trace,
		trace_state=trace_state,
		json_output=json_output,
		json_file_output=json_file_output,
		translate=_,
	)

