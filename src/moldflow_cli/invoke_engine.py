# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Optional

import typer

from .invoke_trace import (
	_emit_invoke_trace_event,
	_make_invoke_trace_hook,
	_trace_error_payload,
	_trace_result_payload,
)


MethodStep = dict[str, Any]
_UNHANDLED_INVOKE_RESULT = object()


@dataclass(frozen=True)
class _ResolvedInvokeTarget:
	canonical_target: str
	parts: list[str]
	cli_to_class: dict[str, type]
	method_steps: list[MethodStep]
	terminal_target_info: dict[str, str] | None


@dataclass(frozen=True)
class _PlannedInvokeCall:
	target: str
	invoke_target: _ResolvedInvokeTarget
	kwargs_per_step: dict[str, dict[str, Any]]
	summarized_steps: list[dict[str, Any]]


@dataclass(frozen=True)
class _PlannedPropertyAssignment:
	target: str
	invoke_target: _ResolvedInvokeTarget
	property_name: str
	assignment_value: Any


def _invoke_plan_payload(planned_call: _PlannedInvokeCall) -> dict[str, Any]:
	payload = {
		"target": planned_call.target,
		"parts": planned_call.invoke_target.parts,
		"steps": planned_call.summarized_steps,
		"kwargs_per_step": planned_call.kwargs_per_step,
	}
	if planned_call.invoke_target.terminal_target_info is not None:
		payload["terminal_target"] = planned_call.invoke_target.terminal_target_info
	return payload


def _execute_planned_invoke_call(
	planned_call: _PlannedInvokeCall,
	*,
	execute_invoke_chain: Callable[..., Any],
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
	trace_hook: Any | None = None,
) -> Any:
	runtime_result = execute_invoke_chain(
		planned_call.invoke_target.parts,
		planned_call.invoke_target.cli_to_class,
		planned_call.invoke_target.method_steps,
		planned_call.kwargs_per_step,
		planned_call.target,
		trace_hook=trace_hook,
	)
	if trace_hook is not None:
		trace_hook(
			"result",
			_trace_result_payload(runtime_result, build_invoke_envelope=build_invoke_envelope),
		)
	return runtime_result


def _execute_invoke_request(
	*,
	call_target: str,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
	dry_run: bool,
	trace_hook: Any | None,
	resolve_invoke_steps: Callable[[str], _ResolvedInvokeTarget],
	make_resolved_invoke_read_target: Callable[..., Any],
	dispatch_terminal_invoke_target: Callable[..., Any],
	plan_invoke_method_call: Callable[..., _PlannedInvokeCall],
	build_dry_run_method_plan: Callable[[_PlannedInvokeCall], dict[str, Any]],
	execute_invoke_chain: Callable[..., Any],
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> Any:
	invoke_target = resolve_invoke_steps(call_target)
	canonical_call_target = invoke_target.canonical_target
	resolved_target = make_resolved_invoke_read_target(
		requested_target=canonical_call_target,
		invoke_target=invoke_target,
	)
	terminal_result = dispatch_terminal_invoke_target(
		call_target=canonical_call_target,
		invoke_target=invoke_target,
		resolved_target=resolved_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		dry_run=dry_run,
		trace_hook=trace_hook,
	)
	if terminal_result is not _UNHANDLED_INVOKE_RESULT:
		return terminal_result
	planned_call = plan_invoke_method_call(
		call_target=canonical_call_target,
		invoke_target=invoke_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		dry_run=dry_run,
	)
	plan_payload = _invoke_plan_payload(planned_call)
	if trace_hook is not None:
		trace_hook("plan", plan_payload)
	if dry_run:
		plan = build_dry_run_method_plan(planned_call)
		if trace_hook is not None:
			trace_hook(
				"result",
				_trace_result_payload(
					plan,
					mode="dry_run",
					build_invoke_envelope=build_invoke_envelope,
				),
			)
		return plan
	return _execute_planned_invoke_call(
		planned_call,
		execute_invoke_chain=execute_invoke_chain,
		build_invoke_envelope=build_invoke_envelope,
		trace_hook=trace_hook,
	)


def _invoke_request_with_error_trace(
	*,
	call_target: str,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
	dry_run: bool,
	trace_hook: Any | None,
	resolve_invoke_steps: Callable[[str], _ResolvedInvokeTarget],
	make_resolved_invoke_read_target: Callable[..., Any],
	dispatch_terminal_invoke_target: Callable[..., Any],
	plan_invoke_method_call: Callable[..., _PlannedInvokeCall],
	build_dry_run_method_plan: Callable[[_PlannedInvokeCall], dict[str, Any]],
	execute_invoke_chain: Callable[..., Any],
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> Any:
	try:
		return _execute_invoke_request(
			call_target=call_target,
			call_args=call_args,
			call_json_input=call_json_input,
			call_json_file_input=call_json_file_input,
			dry_run=dry_run,
			trace_hook=trace_hook,
			resolve_invoke_steps=resolve_invoke_steps,
			make_resolved_invoke_read_target=make_resolved_invoke_read_target,
			dispatch_terminal_invoke_target=dispatch_terminal_invoke_target,
			plan_invoke_method_call=plan_invoke_method_call,
			build_dry_run_method_plan=build_dry_run_method_plan,
			execute_invoke_chain=execute_invoke_chain,
			build_invoke_envelope=build_invoke_envelope,
		)
	except Exception as exc:
		if trace_hook is not None:
			error_type = "invoke_validation" if isinstance(exc, typer.BadParameter) else "runtime_error"
			trace_hook("error", _trace_error_payload(exc, error_type=error_type))
		raise


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
	canonicalize_invoke_target: Callable[[str], str],
	serialize_trace_payload: Callable[[Any], Any],
	schema_version: str,
	resolve_invoke_steps: Callable[[str], _ResolvedInvokeTarget],
	make_resolved_invoke_read_target: Callable[..., Any],
	dispatch_terminal_invoke_target: Callable[..., Any],
	plan_invoke_method_call: Callable[..., _PlannedInvokeCall],
	build_dry_run_method_plan: Callable[[_PlannedInvokeCall], dict[str, Any]],
	execute_invoke_chain: Callable[..., Any],
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> Any:
	canonical_target = canonicalize_invoke_target(call_target)
	trace_hook = _make_invoke_trace_hook(
		trace_enabled=trace_enabled,
		trace_state=trace_state,
		call_target=canonical_target,
		emit_invoke_trace_event=partial(
			_emit_invoke_trace_event,
			serialize_payload=serialize_trace_payload,
			schema_version=schema_version,
		),
		batch_index=batch_index,
	)
	return _invoke_request_with_error_trace(
		call_target=canonical_target,
		call_args=call_args,
		call_json_input=call_json_input,
		call_json_file_input=call_json_file_input,
		dry_run=dry_run,
		trace_hook=trace_hook,
		resolve_invoke_steps=resolve_invoke_steps,
		make_resolved_invoke_read_target=make_resolved_invoke_read_target,
		dispatch_terminal_invoke_target=dispatch_terminal_invoke_target,
		plan_invoke_method_call=plan_invoke_method_call,
		build_dry_run_method_plan=build_dry_run_method_plan,
		execute_invoke_chain=execute_invoke_chain,
		build_invoke_envelope=build_invoke_envelope,
	)