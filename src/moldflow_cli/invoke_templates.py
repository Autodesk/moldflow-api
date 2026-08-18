from __future__ import annotations

import inspect
from typing import Any

from moldflow.i18n import get_text

from .constants import CLI_FIELD_VALUE, CLI_KIND_PROPERTY, CLI_MODE_PROPERTY_ASSIGNMENT
from .introspection import get_docstring, split_structured_doc
from .type_annotations import (
	extract_non_none_type_names,
	format_annotation_text,
	format_signature_for_display,
)
from .wrapper_registry import build_wrapper_input_hints, resolve_first_wrapper_name


_T = get_text()
MethodStep = dict[str, Any]


def _property_value_signature(raw_attr: property) -> tuple[str | None, inspect.Parameter | None]:
	if raw_attr.fset is None:
		return None, None
	try:
		setter_sig = inspect.signature(raw_attr.fset)
	except (TypeError, ValueError):
		return "(value)", None
	params = list(setter_sig.parameters.values())
	value_param = params[1] if len(params) >= 2 else None
	if value_param is None:
		return "(value)", None
	return str(inspect.Signature(parameters=[value_param])), value_param


def _property_return_wrapper_class(
	raw_attr: property,
	cli_to_class: dict[str, type],
	*,
	resolve_return_class: Any,
) -> type | None:
	"""Resolve a property getter return annotation to a public wrapper class when possible."""
	if raw_attr.fget is None:
		return None
	try:
		getter_sig = inspect.signature(raw_attr.fget)
	except (TypeError, ValueError):
		return None
	return resolve_return_class(getter_sig.return_annotation, cli_to_class)


def _build_property_target_template(
	*,
	target: str,
	property_name: str,
	raw_attr: property,
	cli_to_class: dict[str, type],
	resolve_return_class: Any,
	annotation_allows_none: Any,
	build_workflow_examples: Any,
	schema_version: str,
) -> dict[str, Any]:
	signature_value, value_param = _property_value_signature(raw_attr)
	settable = raw_attr.fset is not None
	readable = raw_attr.fget is not None
	return_wrapper_class = _property_return_wrapper_class(
		raw_attr,
		cli_to_class,
		resolve_return_class=resolve_return_class,
	)
	property_doc = get_docstring(raw_attr)
	property_summary, property_details = split_structured_doc(property_doc, obj_type="property") if property_doc else (None, None)
	steps: list[dict[str, Any]] = []
	params_json_template: dict[str, Any] = {}
	mode = "property_read"
	if return_wrapper_class is not None:
		mode = "wrapper_property"
	if settable:
		mode = CLI_MODE_PROPERTY_ASSIGNMENT
		annotation = value_param.annotation if value_param is not None else inspect._empty
		nullable = annotation_allows_none(annotation)
		input_hints = _build_param_template_hints(
			target=target,
			step_name=property_name,
			param_name=CLI_FIELD_VALUE,
			annotation=annotation,
			nullable=nullable,
		)
		step_payload = {
			"name": property_name,
			"kind": CLI_MODE_PROPERTY_ASSIGNMENT,
			"signature": signature_value,
			"params": [
				{
					"name": CLI_FIELD_VALUE,
					"kind": value_param.kind.name if value_param is not None else "POSITIONAL_OR_KEYWORD",
					"annotation": _annotation_text_for_template(annotation),
					"required": True,
					"nullable": nullable,
					"default": None,
					"input_hints": input_hints,
				}
			],
		}
		if property_summary is not None:
			step_payload["summary"] = property_summary
		if property_details is not None:
			step_payload["details"] = property_details
		steps.append(step_payload)
		params_json_template = {CLI_FIELD_VALUE: None}
	workflow_examples = build_workflow_examples(target=target, steps=steps, mode=mode)
	if return_wrapper_class is not None:
		workflow_examples = {
			"mode": mode,
			"notes": [
				_T(
					"This property returns a {class_name} wrapper. Continue with describe {target}.<member> or invoke {target}.<method>."
				).format(class_name=return_wrapper_class.__name__, target=target)
			],
		}
	if readable and settable:
		workflow_examples["read_command"] = f"invoke {target}"
		workflow_examples["read_args"] = []
	if not settable and return_wrapper_class is None:
		workflow_examples = {
			"mode": mode,
			"cli_command": f"invoke {target}",
			"cli_args": [],
		}
	payload = {
		"schema_version": schema_version,
		"target": target,
		"mode": mode,
		"terminal_target": {
			"kind": CLI_KIND_PROPERTY,
			"property": property_name,
			"readable": readable,
			"settable": settable,
		},
		"steps": steps,
		"params_json_template": params_json_template,
		"workflow_examples": workflow_examples,
	}
	if property_summary is not None:
		payload["summary"] = property_summary
	if property_details is not None:
		payload["details"] = property_details
	if return_wrapper_class is not None:
		payload["terminal_target"]["wrapper_class"] = return_wrapper_class.__name__
	return payload


def _apply_step_doc_fields(step_payload: dict[str, Any], *, callable_obj: Any, obj_type: str | None = None) -> None:
	"""Attach structured summary/details fields to a step payload when docs exist."""
	doc = get_docstring(callable_obj)
	if not doc:
		return
	summary_value, details_value = split_structured_doc(doc, obj_type=obj_type)
	if summary_value is not None:
		step_payload["summary"] = summary_value
	if details_value is not None:
		step_payload["details"] = details_value


def _target_doc_fields_from_obj(obj: Any, *, obj_type: str | None = None) -> tuple[str | None, str | None]:
	"""Return top-level structured summary/details for an invoke target object."""
	doc = get_docstring(obj)
	if not doc:
		return None, None
	return split_structured_doc(doc, obj_type=obj_type)


def _annotation_text_for_template(annotation: Any) -> str | None:
	return format_annotation_text(annotation)


def _format_step_signature(signature: Any) -> str:
	"""Render stable step signatures for templates and dry-run summaries."""
	if isinstance(signature, inspect.Signature):
		return format_signature_for_display(signature) or "()"
	if signature is None:
		return "(...)"
	return str(signature).rsplit(" -> ", 1)[0]


def _annotation_type_names_for_template(annotation: Any) -> list[str]:
	"""Return non-None type names used by a parameter annotation."""
	return extract_non_none_type_names(annotation)


def _replace_template_placeholders(value: Any, *, param_name: str) -> Any:
	"""Recursively replace template placeholders in hint/example payloads."""
	if isinstance(value, str):
		return value.replace("<param>", param_name)
	if isinstance(value, list):
		return [_replace_template_placeholders(item, param_name=param_name) for item in value]
	if isinstance(value, dict):
		return {
			(
				key.replace("<param>", param_name)
				if isinstance(key, str)
				else key
			): _replace_template_placeholders(item, param_name=param_name)
			for key, item in value.items()
		}
	return value


def _build_param_template_hints(
	*,
	target: str,
	step_name: str,
	param_name: str,
	annotation: Any,
	nullable: bool,
) -> dict[str, Any] | None:
	"""Build actionable invoke-template hints for complex/object parameters."""
	type_names = _annotation_type_names_for_template(annotation)
	if not type_names:
		return None

	wrapper_type = resolve_first_wrapper_name(type_names)
	if wrapper_type is None:
		return None

	hints: dict[str, Any] = {
		"wrapper_type": wrapper_type,
		"recommended": _T(
			"Prefer chaining invoke targets so this parameter is produced by a previous step, "
			"instead of constructing it manually in JSON."
		),
		"advanced_fallbacks": {
			"tagged_json": {
				"shape": {"__type__": wrapper_type, "<field>": "<value>"},
				"note": _T(
					"Advanced fallback only. Use this tagged shape when annotation context is unavailable, "
					"when a nested payload is truly generic, or when multiple wrapper families would be ambiguous."
				),
			},
		},
	}
	adapter_hints = build_wrapper_input_hints(wrapper_type)
	if adapter_hints is not None:
		typed_json_shape = adapter_hints.get("typed_json_shape")
		if isinstance(typed_json_shape, dict):
			hints["advanced_fallbacks"]["tagged_json"]["shape"] = typed_json_shape
		friendly_json_input = adapter_hints.get("friendly_json_input")
		if isinstance(friendly_json_input, dict):
			hints["friendly_json_input"] = friendly_json_input
		non_json_input = adapter_hints.get("non_json_input")
		if isinstance(non_json_input, dict):
			hints["non_json_input"] = _replace_template_placeholders(
				non_json_input,
				param_name=param_name,
			)
		examples = adapter_hints.get("examples")
		if isinstance(examples, dict):
			hints["examples"] = _replace_template_placeholders(examples, param_name=param_name)
	if nullable:
		hints["nullable"] = _T("This parameter can be null to indicate no value.")

	if wrapper_type.lower() == "plot":
		hints["chain_example"] = {
			"target": "synergy.plot_manager.find_plot_by_name.{step}".format(step=step_name),
			"args": [
				"find_plot_by_name.plot_name=<plot name>",
			],
			"maps_to": _T("{param} receives the Plot returned by find_plot_by_name").format(
				param=param_name
			),
		}

	return hints


def _build_invoke_template(
	target: str,
	method_steps: list[MethodStep],
	*,
	annotation_allows_none: Any,
	build_workflow_examples: Any,
	schema_version: str,
) -> dict[str, Any]:
	steps: list[dict[str, Any]] = []
	template_payload: dict[str, Any] = {}
	for step in method_steps:
		param_map = step.get("params")
		step_name = step["name"]
		step_template: dict[str, Any] = {}
		params: list[dict[str, Any]] = []
		if isinstance(param_map, dict):
			for param_name, param in param_map.items():
				nullable = annotation_allows_none(param.annotation)
				required = (
					param.default is inspect._empty
					and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
					and not nullable
				)
				default_value: Any = None
				if param.default is not inspect._empty:
					if isinstance(param.default, (str, int, float, bool)) or param.default is None:
						default_value = param.default
					else:
						default_value = repr(param.default)
				params.append(
					{
						"name": param_name,
						"kind": param.kind.name,
						"annotation": _annotation_text_for_template(param.annotation),
						"required": required,
						"nullable": nullable,
						"default": default_value,
						"input_hints": _build_param_template_hints(
							target=target,
							step_name=step_name,
							param_name=param_name,
							annotation=param.annotation,
							nullable=nullable,
						),
					}
				)
				if required:
					step_template[param_name] = None
				elif param.default is not inspect._empty:
					step_template[param_name] = default_value
				elif nullable:
					step_template[param_name] = None
		steps.append(
			step_payload := {
				"name": step_name,
				"signature": _format_step_signature(step.get("signature")),
				"params": params,
			}
		)
		callable_obj = step.get("callable")
		if callable_obj is not None:
			_apply_step_doc_fields(step_payload, callable_obj=callable_obj)
		template_payload[step_name] = step_template

	if len(method_steps) == 1 and method_steps:
		template_payload = template_payload[method_steps[0]["name"]]

	workflow_examples = build_workflow_examples(
		target=target,
		steps=steps,
		mode="invoke",
	)
	final_callable = next(
		(step.get("callable") for step in reversed(method_steps) if step.get("callable") is not None),
		None,
	)
	summary_value, details_value = (
		_target_doc_fields_from_obj(final_callable) if final_callable is not None else (None, None)
	)
	payload = {
		"schema_version": schema_version,
		"target": target,
		"steps": steps,
		"params_json_template": template_payload,
		"workflow_examples": workflow_examples,
	}
	if summary_value is not None:
		payload["summary"] = summary_value
	if details_value is not None:
		payload["details"] = details_value
	return payload
