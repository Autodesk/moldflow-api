# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Callable

from .constants import CLI_KIND_PROPERTY_GETTER
from .invoke_engine import _PlannedInvokeCall, _ResolvedInvokeTarget
from .target_resolution import ResolvedInvokeReadTarget


def _make_resolved_invoke_read_target(
	*,
	requested_target: str,
	invoke_target: _ResolvedInvokeTarget,
	resolve_target_for_introspection: Callable[[str], Any],
) -> ResolvedInvokeReadTarget:
	resolved_object = None
	if invoke_target.terminal_target_info is not None:
		resolved_object = resolve_target_for_introspection(invoke_target.canonical_target)
	return ResolvedInvokeReadTarget(
		requested_target=requested_target,
		canonical_target=invoke_target.canonical_target,
		parts=invoke_target.parts,
		cli_to_class=invoke_target.cli_to_class,
		method_steps=invoke_target.method_steps,
		terminal_target_info=invoke_target.terminal_target_info,
		resolved_object=resolved_object,
	)


def _resolve_invoke_read_target(
	target: str,
	*,
	resolve_invoke_steps: Callable[[str], _ResolvedInvokeTarget],
	resolve_target_for_introspection: Callable[[str], Any],
) -> ResolvedInvokeReadTarget:
	invoke_target = resolve_invoke_steps(target)
	return _make_resolved_invoke_read_target(
		requested_target=target,
		invoke_target=invoke_target,
		resolve_target_for_introspection=resolve_target_for_introspection,
	)


def build_invoke_template_for_target(
	target: str,
	*,
	resolve_invoke_read_target: Callable[[str], ResolvedInvokeReadTarget],
	build_invoke_template: Callable[[str, list[dict[str, Any]]], dict[str, Any]],
	target_doc_fields_from_obj: Callable[[Any], tuple[str | None, str | None]],
	build_property_target_template: Callable[..., dict[str, Any]],
	schema_version: str,
) -> dict[str, Any]:
	"""Build template metadata for a target, including terminal property targets."""
	resolved_target = resolve_invoke_read_target(target)
	canonical_target = resolved_target.canonical_target
	terminal_target_info = resolved_target.terminal_target_info
	if terminal_target_info is None:
		return build_invoke_template(canonical_target, resolved_target.method_steps)
	obj = resolved_target.resolved_object
	if not isinstance(obj, property):
		summary_value, details_value = target_doc_fields_from_obj(obj)
		payload = {
			"schema_version": schema_version,
			"target": canonical_target,
			"mode": "attribute_read",
			"terminal_target": {
				"kind": terminal_target_info.get("kind", "attribute"),
				"property": terminal_target_info.get("name"),
			},
			"steps": [],
			"params_json_template": {},
			"workflow_examples": {
				"mode": "attribute_read",
				"cli_command": f"invoke {canonical_target}",
				"cli_args": [],
			},
		}
		if summary_value is not None:
			payload["summary"] = summary_value
		if details_value is not None:
			payload["details"] = details_value
		return payload
	return build_property_target_template(
		target=canonical_target,
		property_name=terminal_target_info["name"],
		raw_attr=obj,
		cli_to_class=resolved_target.cli_to_class,
	)


def _terminal_property_wrapper_class(
	resolved_target: ResolvedInvokeReadTarget,
	*,
	property_return_wrapper_class: Callable[[property, dict[str, type]], type | None],
) -> type | None:
	"""Return the wrapper class for a terminal property target when it yields a wrapper handle."""
	terminal_target_info = resolved_target.terminal_target_info
	if terminal_target_info is None or terminal_target_info.get("kind") != CLI_KIND_PROPERTY_GETTER:
		return None
	obj = resolved_target.resolved_object
	if not isinstance(obj, property):
		return None
	return property_return_wrapper_class(obj, resolved_target.cli_to_class)


def _summarize_steps(
	method_steps: list[dict[str, Any]],
	*,
	format_step_signature: Callable[[Any], str],
	apply_step_doc_fields: Callable[[dict[str, Any], Any], None],
) -> list[dict[str, Any]]:
	out: list[dict[str, Any]] = []
	for step in method_steps:
		param_map = step.get("params")
		step_payload = {
			"name": step["name"],
			"deferred": step.get("signature") is None and step.get("params") is None,
			"signature": format_step_signature(step.get("signature")),
			"params": sorted(list(param_map.keys())) if isinstance(param_map, dict) else [],
		}
		callable_obj = step.get("callable")
		if callable_obj is not None:
			apply_step_doc_fields(step_payload, callable_obj)
		out.append(step_payload)
	return out


def _plan_invoke_method_call(
	*,
	call_target: str,
	invoke_target: _ResolvedInvokeTarget,
	call_args: list[str],
	call_json_input: str | None,
	call_json_file_input: str | None,
	dry_run: bool,
	parse_invoke_items: Callable[..., list[Any]],
	bucket_items_by_step: Callable[[list[dict[str, Any]], list[Any]], Any],
	build_kwargs_per_step: Callable[..., dict[str, dict[str, Any]]],
	summarize_steps: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
) -> _PlannedInvokeCall:
	parsed_items = parse_invoke_items(
		invoke_target.method_steps,
		call_args,
		call_json_input,
		call_json_file_input,
	)
	step_args = bucket_items_by_step(invoke_target.method_steps, parsed_items)
	kwargs_per_step = build_kwargs_per_step(
		invoke_target.method_steps,
		step_args,
		call_target,
		dry_run=dry_run,
	)
	return _PlannedInvokeCall(
		target=call_target,
		invoke_target=invoke_target,
		kwargs_per_step=kwargs_per_step,
		summarized_steps=summarize_steps(invoke_target.method_steps),
	)


def _build_dry_run_method_plan(
	planned_call: _PlannedInvokeCall,
	*,
	build_invoke_template_for_target: Callable[[str], dict[str, Any]],
	serialize_value: Callable[[Any], Any],
	schema_version: str,
) -> dict[str, Any]:
	template_payload = build_invoke_template_for_target(planned_call.target)
	dry_run_steps = template_payload.get("steps")
	if not isinstance(dry_run_steps, list):
		dry_run_steps = planned_call.summarized_steps
	plan = {
		"schema_version": schema_version,
		"mode": "dry_run",
		"target": planned_call.target,
		"parts": planned_call.invoke_target.parts,
		"steps": dry_run_steps,
		"kwargs_per_step": serialize_value(planned_call.kwargs_per_step),
	}
	for doc_field in ("summary", "details"):
		doc_value = template_payload.get(doc_field)
		if isinstance(doc_value, str) and doc_value:
			plan[doc_field] = doc_value
	if planned_call.invoke_target.terminal_target_info is not None:
		plan["terminal_target"] = planned_call.invoke_target.terminal_target_info
	return plan