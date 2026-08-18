# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Callable, Optional
import inspect

import typer

from .constants import CLI_FIELD_VALUE, CLI_KIND_PROPERTY, CLI_KIND_PROPERTY_GETTER, CLI_MODE_PROPERTY_ASSIGNMENT
from .invoke_engine import (
	_PlannedPropertyAssignment,
	_ResolvedInvokeTarget,
	_UNHANDLED_INVOKE_RESULT,
)
from .invoke_trace import _trace_result_payload
from .target_resolution import ResolvedInvokeReadTarget
from moldflow.i18n import get_text


_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _resolve_property_assignment_owner(
	*,
	invoke_target: _ResolvedInvokeTarget,
	call_target: str,
	property_name: str,
	trace_hook: Any | None,
	execute_invoke_chain: Callable[..., Any],
) -> tuple[Any, property]:
	owner_parts = invoke_target.parts[:-1]
	owner_target = ".".join(owner_parts) if owner_parts else invoke_target.parts[0]
	owner_obj = execute_invoke_chain(
		owner_parts,
		invoke_target.cli_to_class,
		[],
		{},
		owner_target,
		trace_hook=trace_hook,
	)
	if owner_obj is None:
		raise typer.BadParameter(
			_tr(
				"Cannot assign property '{property_name}' while resolving target '{target}' "
				"because the owner object resolved to None.",
				property_name=property_name,
				target=call_target,
			)
		)

	raw_attr = inspect.getattr_static(type(owner_obj), property_name, None)
	if not isinstance(raw_attr, property) or raw_attr.fset is None:
		raise typer.BadParameter(
			_tr(
				"Target '{target}' resolves to property '{property_name}' "
				"(getter) and does not accept arguments.",
				target=call_target,
				property_name=property_name,
			)
		)
	return owner_obj, raw_attr


def _plan_property_assignment(
	*,
	call_target: str,
	invoke_target: _ResolvedInvokeTarget,
	property_name: str,
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	parse_terminal_property_assignment_value: Callable[[list[str], Optional[str], Optional[str]], Any],
	execute_invoke_chain: Callable[..., Any],
) -> _PlannedPropertyAssignment:
	_resolve_property_assignment_owner(
		invoke_target=invoke_target,
		call_target=call_target,
		property_name=property_name,
		trace_hook=None,
		execute_invoke_chain=execute_invoke_chain,
	)
	return _PlannedPropertyAssignment(
		target=call_target,
		invoke_target=invoke_target,
		property_name=property_name,
		assignment_value=parse_terminal_property_assignment_value(
			raw_args,
			json_input,
			json_file_input,
		),
	)


def _property_assignment_plan_payload(
	planned_assignment: _PlannedPropertyAssignment,
	*,
	build_invoke_template_for_target: Callable[[str], dict[str, Any]],
	to_serializable: Callable[[Any], Any],
	schema_version: str,
) -> dict[str, Any]:
	template_payload = build_invoke_template_for_target(planned_assignment.target)
	return {
		"schema_version": schema_version,
		"mode": "dry_run",
		"target": planned_assignment.target,
		"terminal_target": {
			"kind": CLI_KIND_PROPERTY,
			"property": planned_assignment.property_name,
			"assignment": True,
		},
		"assignment": {CLI_FIELD_VALUE: to_serializable(planned_assignment.assignment_value)},
		"workflow_examples": template_payload.get("workflow_examples", {}),
		"params_json_template": template_payload.get("params_json_template", {}),
	}


def _execute_planned_property_assignment(
	planned_assignment: _PlannedPropertyAssignment,
	*,
	trace_hook: Any | None,
	execute_invoke_chain: Callable[..., Any],
) -> Any:
	owner_obj, _ = _resolve_property_assignment_owner(
		invoke_target=planned_assignment.invoke_target,
		call_target=planned_assignment.target,
		property_name=planned_assignment.property_name,
		trace_hook=trace_hook,
		execute_invoke_chain=execute_invoke_chain,
	)

	if trace_hook is not None:
		trace_hook(
			"property_assign",
			{
				"target": planned_assignment.target,
				"property": planned_assignment.property_name,
				CLI_FIELD_VALUE: planned_assignment.assignment_value,
			},
		)
	try:
		setattr(owner_obj, planned_assignment.property_name, planned_assignment.assignment_value)
	except (AttributeError, TypeError, ValueError) as exc:
		raise typer.BadParameter(
			_tr(
				"Cannot set property '{property_name}' on target '{target}': {error}",
				property_name=planned_assignment.property_name,
				target=planned_assignment.target,
				error=exc,
			)
		) from exc

	try:
		return getattr(owner_obj, planned_assignment.property_name)
	except (AttributeError, TypeError, ValueError):
		return None


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
	parse_terminal_property_assignment_value: Callable[[list[str], Optional[str], Optional[str]], Any],
	execute_invoke_chain: Callable[..., Any],
) -> Any:
	planned_assignment = _plan_property_assignment(
		call_target=call_target,
		invoke_target=_ResolvedInvokeTarget(
			canonical_target=call_target,
			parts=parts,
			cli_to_class=cli_to_class,
			method_steps=[],
			terminal_target_info={"kind": CLI_KIND_PROPERTY_GETTER, "name": property_name},
		),
		property_name=property_name,
		raw_args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		parse_terminal_property_assignment_value=parse_terminal_property_assignment_value,
		execute_invoke_chain=execute_invoke_chain,
	)
	return _execute_planned_property_assignment(
		planned_assignment,
		trace_hook=trace_hook,
		execute_invoke_chain=execute_invoke_chain,
	)


def _build_property_assignment_plan(
	*,
	call_target: str,
	property_name: str,
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	parse_terminal_property_assignment_value: Callable[[list[str], Optional[str], Optional[str]], Any],
	build_invoke_template_for_target: Callable[[str], dict[str, Any]],
	to_serializable: Callable[[Any], Any],
	schema_version: str,
	execute_invoke_chain: Callable[..., Any],
) -> dict[str, Any]:
	planned_assignment = _plan_property_assignment(
		call_target=call_target,
		invoke_target=_ResolvedInvokeTarget(
			canonical_target=call_target,
			parts=call_target.split("."),
			cli_to_class={},
			method_steps=[],
			terminal_target_info={"kind": CLI_KIND_PROPERTY_GETTER, "name": property_name},
		),
		property_name=property_name,
		raw_args=raw_args,
		json_input=json_input,
		json_file_input=json_file_input,
		parse_terminal_property_assignment_value=parse_terminal_property_assignment_value,
		execute_invoke_chain=execute_invoke_chain,
	)
	return _property_assignment_plan_payload(
		planned_assignment,
		build_invoke_template_for_target=build_invoke_template_for_target,
		to_serializable=to_serializable,
		schema_version=schema_version,
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
	terminal_property_wrapper_class: Callable[[ResolvedInvokeReadTarget], type | None],
	parse_terminal_property_assignment_value: Callable[[list[str], Optional[str], Optional[str]], Any],
	build_invoke_template_for_target: Callable[[str], dict[str, Any]],
	to_serializable: Callable[[Any], Any],
	schema_version: str,
	execute_invoke_chain: Callable[..., Any],
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> Any:
	_ = get_text()
	if invoke_target.method_steps:
		return _UNHANDLED_INVOKE_RESULT

	wrapper_property_class = terminal_property_wrapper_class(resolved_target)
	if wrapper_property_class is not None:
		raise typer.BadParameter(
			_(
				"Target '{target}' resolves to a {class_name} wrapper property. Continue to one of its members, for example 'describe {target}.<member>'."
			).format(target=call_target, class_name=wrapper_property_class.__name__)
		)

	if not (call_args or call_json_input is not None or call_json_file_input is not None):
		return _UNHANDLED_INVOKE_RESULT

	if (
		invoke_target.terminal_target_info is not None
		and invoke_target.terminal_target_info.get("kind") == CLI_KIND_PROPERTY_GETTER
	):
		if dry_run:
			property_name = invoke_target.terminal_target_info["name"]
			raw_attr = resolved_target.resolved_object
			if not isinstance(raw_attr, property) or raw_attr.fset is None:
				raise typer.BadParameter(
					_tr(
						"Target '{target}' resolves to property '{property_name}' "
						"(getter) and does not accept arguments.",
						target=call_target,
						property_name=property_name,
					)
				)
			planned_assignment = _PlannedPropertyAssignment(
				target=call_target,
				invoke_target=invoke_target,
				property_name=property_name,
				assignment_value=parse_terminal_property_assignment_value(
					call_args,
					call_json_input,
					call_json_file_input,
				),
			)
			plan = _property_assignment_plan_payload(
				planned_assignment,
				build_invoke_template_for_target=build_invoke_template_for_target,
				to_serializable=to_serializable,
				schema_version=schema_version,
			)
			if trace_hook is not None:
				trace_hook("plan", plan)
				trace_hook(
					"result",
					_trace_result_payload(
						plan,
						mode="dry_run",
						build_invoke_envelope=build_invoke_envelope,
					),
				)
			return plan
		planned_assignment = _plan_property_assignment(
			call_target=call_target,
			invoke_target=invoke_target,
			property_name=invoke_target.terminal_target_info["name"],
			raw_args=call_args,
			json_input=call_json_input,
			json_file_input=call_json_file_input,
			parse_terminal_property_assignment_value=parse_terminal_property_assignment_value,
			execute_invoke_chain=execute_invoke_chain,
		)
		property_result = _execute_planned_property_assignment(
			planned_assignment,
			trace_hook=trace_hook,
			execute_invoke_chain=execute_invoke_chain,
		)
		if trace_hook is not None:
			trace_hook(
				"result",
				_trace_result_payload(
					property_result,
					mode=CLI_MODE_PROPERTY_ASSIGNMENT,
					build_invoke_envelope=build_invoke_envelope,
				),
			)
		return property_result

	raise typer.BadParameter(
		_(
			"Target '{target}' resolves to a property/attribute and does not accept arguments."
		).format(target=call_target)
	)
