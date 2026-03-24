from __future__ import annotations

import inspect
import json as _json
from difflib import get_close_matches
from types import NoneType
from typing import Annotated, Any, Optional, get_args, get_origin

import typer

from moldflow.i18n import get_text

from .constants import CLI_FIELD_VALUE, CLI_INPUT_SOURCE_JSON
from .factories import build_wrapper_instance
from .target_resolution import split_dotted_path
from .type_annotations import annotation_text_allows_str, extract_non_none_type_names
from .wrapper_registry import build_wrapper_input_hints, resolve_first_wrapper_name
from .wrapper_input_adapters import (
	apply_wrapper_input_adapter,
	apply_wrapper_shorthand_adapter,
)


ParsedItem = tuple[list[str], Any, str]
MethodStep = dict[str, Any]
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _closest_name(name: str, candidates: list[str] | set[str] | tuple[str, ...]) -> str | None:
	matches = get_close_matches(name, list(candidates), n=1, cutoff=0.6)
	return matches[0] if matches else None


def _multi_step_json_example(step_name: str) -> str:
	return _json.dumps({step_name: {"<param>": "<value>"}}, ensure_ascii=True)


def _wrapper_json_guidance(param_name: str, param: inspect.Parameter | None) -> str | None:
	if param is None:
		return None
	type_names = extract_non_none_type_names(param.annotation)
	if not type_names:
		return None
	wrapper_type = resolve_first_wrapper_name(type_names)
	if wrapper_type is None:
		return None
	hints = build_wrapper_input_hints(wrapper_type)
	if not isinstance(hints, dict):
		return None
	friendly_json_input = hints.get("friendly_json_input")
	if not isinstance(friendly_json_input, dict):
		return None
	preferred_field = friendly_json_input.get("preferred_field")
	if not isinstance(preferred_field, str) or not preferred_field:
		return None
	return _tr(
		"Use JSON field '{preferred_field}' for '{param_name}'.",
		param_name=param_name,
		preferred_field=preferred_field,
	)


def _wrapper_non_json_guidance(param_name: str, param: inspect.Parameter | None) -> str | None:
	if param is None:
		return None
	guidance = _wrapper_json_guidance(param_name, param)
	if guidance is None:
		return None
	return _tr(
		"If shorthand input is ambiguous, switch to --params-json. {guidance}",
		guidance=guidance,
	)


def _is_annotated_origin(origin: Any) -> bool:
	"""Return True when origin represents typing.Annotated across Python versions."""
	if origin is None:
		return False
	if origin is Annotated:
		return True
	origin_name = getattr(origin, "__name__", "")
	if origin_name == "Annotated":
		return True
	return "Annotated" in str(origin)


def _parse_scalar(value: str) -> Any:
	"""Best-effort conversion of a string CLI value into a Python scalar."""
	text = value.strip()
	lower = text.lower()
	if lower in {"true", "yes", "on"}:
		return True
	if lower in {"false", "no", "off"}:
		return False
	if lower in {"none", "null"}:
		return None
	try:
		return int(text)
	except ValueError:
		pass
	try:
		return float(text)
	except ValueError:
		pass
	return text


def _validate_cli_param(param_name: str, value: Any) -> Any:
	"""Light validation for string CLI argument values."""
	if not isinstance(value, str):
		return value
	if "\x00" in value:
		raise typer.BadParameter(
			_T("Parameter '{param_name}' contains a null byte which is not allowed.").format(
				param_name=param_name
			)
		)
	if any(ch in value for ch in ("\n", "\r", "\t")):
		raise typer.BadParameter(
			_T(
				"Parameter '{param_name}' contains control characters (newline/tab/carriage return); "
				"please provide a single-line value or quote/escape as needed."
			).format(param_name=param_name)
		)
	return value


def _validate_json_param(param_name: str, value: Any) -> Any:
	"""Validation for JSON-derived string parameters."""
	if not isinstance(value, str):
		return value
	if "\x00" in value:
		raise typer.BadParameter(
			_T("Parameter '{param_name}' contains a null byte which is not allowed.").format(
				param_name=param_name
			)
		)
	return value


def _split_dotted_path(path_text: str, *, field_name: str) -> list[str]:
	"""Split dotted identifiers while rejecting empty segments."""
	return split_dotted_path(path_text, field_name=field_name, translate=_T)


def _validate_invoke_input_sources(
	raw_args: list[str], json_input: Optional[str], json_file_input: Optional[str]
) -> None:
	_ = get_text()
	if json_input and json_file_input:
		raise typer.BadParameter(
			_("Only one of --params-json or --params-json-file may be specified.")
		)
	if (json_input or json_file_input) and raw_args:
		raise typer.BadParameter(
			_(
				"When JSON input is provided via --params-json or --params-json-file, no positional "
				"key=value args may be given."
			)
		)


def _append_payload_items(
	parsed_items: list[ParsedItem], payload: Any, method_steps: list[MethodStep]
) -> None:
	_ = get_text()
	if not isinstance(payload, dict):
		raise typer.BadParameter(
			_(
				"JSON parameters must be a JSON object of named arguments. "
				"Example: --params-json '{\"param\": 1}' "
				"or --params-json '{\"step\": {\"param\": 1}}' for chained targets."
			)
		)

	if len(method_steps) == 1:
		single_step_name = method_steps[0]["name"]
		single_step_params = method_steps[0].get("params")
		single_step_params_lower = (
			{str(name).lower() for name in single_step_params}
			if isinstance(single_step_params, dict)
			else set()
		)
		if (
			isinstance(single_step_params, dict)
			and len(payload) == 1
			and isinstance(next(iter(payload.values())), dict)
		):
			only_key = str(next(iter(payload.keys())))
			if only_key.lower() == single_step_name.lower() and only_key.lower() not in single_step_params_lower:
				payload = next(iter(payload.values()))

		for key, value in payload.items():
			if str(key).startswith("_"):
				raise typer.BadParameter(
					_tr("Non-public argument path '{path}' is not allowed.", path=key)
				)
			parsed_items.append(([str(key)], value, CLI_INPUT_SOURCE_JSON))
		return

	valid_step_names = {step["name"] for step in method_steps}
	valid_step_names_lower = {name.lower(): name for name in valid_step_names}
	for step_name, step_payload in payload.items():
		if str(step_name).startswith("_"):
			raise typer.BadParameter(
				_tr("Non-public argument path '{path}' is not allowed.", path=step_name)
			)
		canonical_step_name = valid_step_names_lower.get(str(step_name).lower())
		if canonical_step_name is None:
			raise typer.BadParameter(
				_tr(
					"Argument '{argument}' must start with one of: {valid_steps}",
					argument=step_name,
					valid_steps=", ".join(sorted(valid_step_names)),
				)
			)
		if not isinstance(step_payload, dict):
			raise typer.BadParameter(
				_tr(
					"Arguments for step '{step_name}' must be a JSON object of parameters.",
					step_name=step_name,
				)
			)
		for key, value in step_payload.items():
			if str(key).startswith("_"):
				raise typer.BadParameter(
					_tr(
						"Non-public argument path '{path}' is not allowed.",
						path=f"{canonical_step_name}.{key}",
					)
				)
			parsed_items.append(([canonical_step_name, str(key)], value, CLI_INPUT_SOURCE_JSON))


def _parse_positional_key_value_items(raw_args: list[str]) -> list[ParsedItem]:
	_ = get_text()
	parsed_items: list[ParsedItem] = []
	for item in raw_args:
		if "=" not in item:
			raise typer.BadParameter(
				_("Invalid argument '{item}'. Expected key=value or param.attr=value.").format(
					item=item
				)
			)
		left, value = item.split("=", 1)
		path = _split_dotted_path(left, field_name="argument path")
		if any(seg.startswith("_") for seg in path):
			raise typer.BadParameter(
				_tr("Non-public argument path '{path}' is not allowed.", path=left)
			)
		parsed_items.append((path, value, "cli"))
	return parsed_items


def _parse_invoke_items(
	method_steps: list[MethodStep],
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
) -> list[ParsedItem]:
	_validate_invoke_input_sources(raw_args, json_input, json_file_input)
	parsed_items: list[ParsedItem] = []

	if json_input is not None:
		try:
			payload = _json.loads(json_input)
		except (_json.JSONDecodeError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr("Invalid JSON payload for parameters: {error}", error=exc)
			) from exc
		_append_payload_items(parsed_items, payload, method_steps)
	elif json_file_input is not None:
		try:
			with open(json_file_input, "r", encoding="utf-8-sig") as input_file:
				payload = _json.load(input_file)
		except (OSError, UnicodeError, _json.JSONDecodeError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr("Cannot read JSON file '{path}': {error}", path=json_file_input, error=exc)
			) from exc
		_append_payload_items(parsed_items, payload, method_steps)
	elif len(raw_args) == 1 and isinstance(raw_args[0], str) and raw_args[0].strip().startswith(("{", "[")):
		try:
			payload = _json.loads(raw_args[0])
		except (_json.JSONDecodeError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr(
					"Invalid JSON payload for parameters: {error}. A single positional "
					"argument beginning with '{{' or '[' is treated as JSON shorthand; "
					"use --params-json for clearer intent.",
					error=exc,
				)
			) from exc
		_append_payload_items(parsed_items, payload, method_steps)
	else:
		parsed_items.extend(_parse_positional_key_value_items(raw_args))

	return parsed_items


def _parse_terminal_property_assignment_value(
	raw_args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
) -> Any:
	"""Parse assignment input for terminal property targets.

	Accepted inputs are:
	- `value=...`
	- `--params-json '{"value": ...}'`
	- `--params-json-file` containing `{"value": ...}`
	"""
	_ = get_text()
	_validate_invoke_input_sources(raw_args, json_input, json_file_input)

	if json_input is not None or json_file_input is not None:
		if json_input is not None:
			try:
				payload = _json.loads(json_input)
			except (_json.JSONDecodeError, RecursionError) as exc:
				raise typer.BadParameter(
					_tr("Invalid JSON payload for parameters: {error}", error=exc)
				) from exc
		else:
			try:
				with open(json_file_input, "r", encoding="utf-8-sig") as input_file:
					payload = _json.load(input_file)
			except (OSError, UnicodeError, _json.JSONDecodeError, RecursionError) as exc:
				raise typer.BadParameter(
					_tr("Cannot read JSON file '{path}': {error}", path=json_file_input, error=exc)
				) from exc

		if not isinstance(payload, dict):
			raise typer.BadParameter(
				_(
					"Property assignment JSON must be an object with a single 'value' field."
				)
			)

		payload_keys = list(payload.keys())
		if len(payload_keys) != 1 or str(payload_keys[0]).lower() != CLI_FIELD_VALUE:
			raise typer.BadParameter(
				_(
					"Property assignment requires exactly one 'value' argument "
					"(e.g., value=... or --params-json '{\"value\": ...}')."
				)
			)

		from .factories import convert_value

		try:
			return _validate_json_param(CLI_FIELD_VALUE, convert_value(payload[payload_keys[0]]))
		except (AttributeError, TypeError, ValueError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr("Invalid JSON value for parameter '{param_name}': {error}", param_name=CLI_FIELD_VALUE, error=exc)
			) from exc

	parsed_items = _parse_positional_key_value_items(raw_args)
	if len(parsed_items) != 1:
		raise typer.BadParameter(
			_(
				"Property assignment requires exactly one 'value' argument "
				"(e.g., value=... or --params-json '{\"value\": ...}')."
			)
		)
	path, value, _origin = parsed_items[0]
	if len(path) != 1 or path[0].lower() != CLI_FIELD_VALUE:
		raise typer.BadParameter(
			_(
				"Property assignment requires exactly one 'value' argument "
				"(e.g., value=... or --params-json '{\"value\": ...}')."
			)
		)
	raw_value = _validate_cli_param(CLI_FIELD_VALUE, value)
	return _validate_cli_param(CLI_FIELD_VALUE, _parse_scalar(raw_value))


def _bucket_items_by_step(
	method_steps: list[MethodStep], parsed_items: list[ParsedItem]
) -> dict[str, list[ParsedItem]]:
	step_args: dict[str, list[ParsedItem]] = {step["name"]: [] for step in method_steps}
	if len(method_steps) == 1:
		single_name = method_steps[0]["name"]
		single_name_lower = single_name.lower()
		for path, value, origin in parsed_items:
			if path and path[0].lower() == single_name_lower and len(path) > 1:
				path = path[1:]
			step_args[single_name].append((path, value, origin))
		return step_args

	valid_step_names = {step["name"] for step in method_steps}
	valid_step_names_lower = {name.lower(): name for name in valid_step_names}
	for path, value, origin in parsed_items:
		step_name = valid_step_names_lower.get(path[0].lower())
		if step_name is None:
			suggestion = _closest_name(path[0], valid_step_names)
			extra = ""
			if suggestion is not None:
				extra += _tr("\nDid you mean step '{step_name}'?", step_name=suggestion)
			example_step = suggestion or sorted(valid_step_names)[0]
			if origin == CLI_INPUT_SOURCE_JSON:
				extra += _tr(
					"\nFor JSON input on multi-step targets, group parameters by step name, e.g. {example}",
					example=_multi_step_json_example(example_step),
				)
				message = _tr(
					"For JSON input, group parameters by step name. Argument '{argument}' must start with one of: {valid_steps}.{extra}",
					argument=".".join(path),
					valid_steps=", ".join(sorted(valid_step_names)),
					extra=extra,
				)
			else:
				message = _tr(
					"Argument '{argument}' must start with one of: {valid_steps}.{extra}",
					argument=".".join(path),
					valid_steps=", ".join(sorted(valid_step_names)),
					extra=extra,
				)
			raise typer.BadParameter(message)
		if len(path) == 1:
			extra = ""
			if origin == CLI_INPUT_SOURCE_JSON:
				extra = _tr(
					"\nFor JSON input, this step key must map to an object of parameter names, e.g. {example}",
					example=_multi_step_json_example(step_name),
				)
			raise typer.BadParameter(
				_tr(
					"Argument '{argument}' must specify a parameter name after the step "
					"(e.g., {step_name}.param=...).{extra}",
					argument=".".join(path),
					step_name=step_name,
					extra=extra,
				)
			)
		step_args[step_name].append((path[1:], value, origin))
	return step_args


def _build_kwargs_per_step(
	method_steps: list[MethodStep],
	step_args: dict[str, list[ParsedItem]],
	target: str,
	*,
	dry_run: bool = False,
) -> dict[str, dict[str, Any]]:
	kwargs_per_step: dict[str, dict[str, Any]] = {step["name"]: {} for step in method_steps}
	qualify_parameter_names = len(method_steps) > 1
	for step in method_steps:
		items = step_args.get(step["name"], [])
		if step.get("signature") is None and step.get("params") is None:
			kwargs_per_step[step["name"]] = {"__deferred_items__": items}
			continue
		kwargs_per_step[step["name"]] = _build_step_kwargs(
			step,
			items,
			target,
			dry_run=dry_run,
			qualify_parameter_names=qualify_parameter_names,
		)
	return kwargs_per_step


def _required_parameter_label(step_name: str, parameter_name: str, *, qualify: bool) -> str:
	"""Return the user-facing missing-parameter label for a step."""
	if not qualify:
		return parameter_name
	return f"{step_name}.{parameter_name}"


def _ensure_required_step_params(
	step_name: str,
	param_map: dict[str, inspect.Parameter] | None,
	items: list[ParsedItem],
	target: str,
	sig: Any,
	*,
	qualify_parameter_names: bool,
) -> None:
	if param_map is None:
		return
	positional_only = [
		name for name, param in param_map.items() if param.kind == inspect.Parameter.POSITIONAL_ONLY
	]
	if positional_only:
		raise typer.BadParameter(
			_tr(
				"Step '{step_name}' in target '{target}' has positional-only parameters "
				"({parameters}), which are not supported by CLI named-argument "
				"routing. Use the Python API for this target.",
				step_name=step_name,
				target=target,
				parameters=", ".join(positional_only),
			)
		)
	provided_param_names_lower = {path[0].lower() for path, _, _ in items if path}
	for name, param in param_map.items():
		if name.lower() in provided_param_names_lower:
			continue
		if param.default is not inspect._empty:
			continue
		if _annotation_allows_none(param.annotation):
			continue
		if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
			continue
		raise typer.BadParameter(
			_tr(
				"Missing required parameter '{parameter}' for {target}{signature}. "
				"Run 'describe {target}' to inspect accepted parameters and JSON examples.",
				parameter=_required_parameter_label(
					step_name,
					name,
					qualify=qualify_parameter_names,
				),
				target=target,
				signature=sig,
			)
		)


def _annotation_allows_none(annotation: Any) -> bool:
	"""Return True when the annotation explicitly allows None/null."""
	if annotation is inspect._empty:
		return False
	if annotation is None or annotation is NoneType:
		return True
	if isinstance(annotation, str):
		normalized = annotation.replace(" ", "").replace("typing.", "").lower()
		return (
			"optional[" in normalized
			or "|none" in normalized
			or "nonetype" in normalized
			or "none]" in normalized
			or ",none" in normalized
		)
	origin = get_origin(annotation)
	if _is_annotated_origin(origin):
		annotated_args = get_args(annotation)
		if annotated_args:
			return _annotation_allows_none(annotated_args[0])
	args = get_args(annotation)
	if args:
		return any(arg is NoneType for arg in args)
	return False


def _validate_step_item_path_conflicts(step_name: str, items: list[ParsedItem]) -> None:
	seen_paths: list[tuple[str, ...]] = []
	for path, _, _ in items:
		path_tuple = tuple(path)
		if path_tuple in seen_paths:
			raise typer.BadParameter(
				_tr(
					"Duplicate argument path '{path}' is not allowed.",
					path=f"{step_name}.{'.'.join(path)}",
				)
			)
		for existing in seen_paths:
			if len(existing) <= len(path_tuple) and path_tuple[: len(existing)] == existing:
				raise typer.BadParameter(
					_tr(
						"Conflicting argument paths '{left_path}' and '{right_path}' are not allowed.",
						left_path=f"{step_name}.{'.'.join(existing)}",
						right_path=f"{step_name}.{'.'.join(path)}",
					)
				)
			if len(path_tuple) < len(existing) and existing[: len(path_tuple)] == path_tuple:
				raise typer.BadParameter(
					_tr(
						"Conflicting argument paths '{left_path}' and '{right_path}' are not allowed.",
						left_path=f"{step_name}.{'.'.join(path)}",
						right_path=f"{step_name}.{'.'.join(existing)}",
					)
				)
		seen_paths.append(path_tuple)


def _coerce_step_value_for_dry_run(param_name: str, value: Any, origin: str) -> Any:
	if origin == CLI_INPUT_SOURCE_JSON:
		return _validate_json_param(param_name, value)
	raw_value = _validate_cli_param(param_name, value)
	return _validate_cli_param(param_name, _parse_scalar(raw_value))


def _annotation_prefers_raw_string(param: inspect.Parameter | None) -> bool:
	if param is None:
		return False
	annotation = param.annotation
	if annotation is str:
		return True
	if isinstance(annotation, str) and annotation_text_allows_str(annotation):
		return True
	annotation_args = get_args(annotation)
	return bool(annotation_args and any(arg is str for arg in annotation_args))


def _coerce_non_json_step_value(
	param_name: str,
	value: Any,
	param: inspect.Parameter | None,
) -> Any:
	raw_value = _validate_cli_param(param_name, value)
	if _annotation_prefers_raw_string(param):
		return raw_value
	if param is not None:
		try:
			obj = build_wrapper_instance(param.annotation)
		except (AttributeError, TypeError, ValueError, RecursionError):
			obj = None
		if obj is not None:
			try:
				if apply_wrapper_shorthand_adapter(obj, raw_value, applied_adapters={}):
					return obj
			except (AttributeError, TypeError, ValueError, RecursionError) as exc:
				guidance = _wrapper_non_json_guidance(param_name, param)
				error_text = str(exc)
				if guidance:
					error_text = f"{error_text} {guidance}"
				raise typer.BadParameter(
					_tr(
						"Invalid value for parameter '{param_name}': {error}",
						param_name=param_name,
						error=error_text,
					)
				) from exc
	return _validate_cli_param(param_name, _parse_scalar(raw_value))


def _raise_invalid_json_step_value(
	param_name: str,
	exc: Exception,
	param: inspect.Parameter | None = None,
) -> None:
	message = _tr("Invalid JSON value for parameter '{param_name}': {error}", param_name=param_name, error=exc)
	guidance = _wrapper_json_guidance(param_name, param)
	if guidance:
		message = f"{message} {guidance}"
	raise typer.BadParameter(message) from exc


def _coerce_json_step_value(
	param_name: str,
	value: Any,
	param: inspect.Parameter | None,
) -> Any:
	from .factories import configure_object_from_dict, convert_value

	if isinstance(value, dict) and param is not None and "__type__" not in value:
		type_names = extract_non_none_type_names(param.annotation)
		expected_wrapper_type = type_names[0] if len(type_names) == 1 else None
		try:
			obj = build_wrapper_instance(param.annotation)
		except (AttributeError, TypeError, ValueError, RecursionError):
			try:
				return _validate_json_param(param_name, convert_value(value))
			except (AttributeError, TypeError, ValueError, RecursionError) as inner_exc:
				_raise_invalid_json_step_value(param_name, inner_exc, param)

		try:
			obj = configure_object_from_dict(obj, value, expected_type=expected_wrapper_type)
			return _validate_json_param(param_name, obj)
		except (AttributeError, TypeError, ValueError, RecursionError) as exc:
			_raise_invalid_json_step_value(param_name, exc, param)

	try:
		return _validate_json_param(param_name, convert_value(value))
	except (AttributeError, TypeError, ValueError, RecursionError) as exc:
		_raise_invalid_json_step_value(param_name, exc, param)


def _coerce_step_value(
	param_name: str,
	value: Any,
	origin: str,
	param: inspect.Parameter | None,
	*,
	dry_run: bool = False,
) -> Any:
	if dry_run:
		return _coerce_step_value_for_dry_run(param_name, value, origin)

	if origin != CLI_INPUT_SOURCE_JSON:
		return _coerce_non_json_step_value(param_name, value, param)

	return _coerce_json_step_value(param_name, value, param)


def _coerce_kwargs_value(param_name: str, value: Any, origin: str, *, dry_run: bool = False) -> Any:
	if dry_run:
		if origin == CLI_INPUT_SOURCE_JSON:
			return _validate_json_param(param_name, value)
		raw_value = _validate_cli_param(param_name, value)
		return _validate_cli_param(param_name, _parse_scalar(raw_value))

	if origin == CLI_INPUT_SOURCE_JSON:
		from .factories import convert_value

		try:
			return _validate_json_param(param_name, convert_value(value))
		except (AttributeError, TypeError, ValueError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr("Invalid JSON value for parameter '{param_name}': {error}", param_name=param_name, error=exc)
			) from exc
	raw_value = _validate_cli_param(param_name, value)
	return _validate_cli_param(param_name, _parse_scalar(raw_value))


def _navigate_to_parent_dry_run(
	step_name: str, step_kwargs: dict[str, Any], path: list[str]
) -> tuple[dict[str, Any], str]:
	"""Navigate to parent dict for dry-run nested set; return (parent_dict, final_attr)."""
	param_name = path[0]
	current_obj: Any = step_kwargs[param_name]
	for attr in path[1:-1]:
		if not isinstance(current_obj, dict):
			raise typer.BadParameter(
				_tr(
					"Invalid nested argument path '{path}': cannot nest into non-object '{obj_type}'.",
					path=f"{step_name}.{'.'.join(path)}",
					obj_type=type(current_obj).__name__,
				)
			)
		current_obj = current_obj.setdefault(attr, {})
	final_attr = path[-1]
	if not isinstance(current_obj, dict):
		raise typer.BadParameter(
			_tr(
				"Invalid nested argument path '{path}': cannot set '{final_attr}' on non-object '{obj_type}'.",
				path=f"{step_name}.{'.'.join(path)}",
				final_attr=final_attr,
				obj_type=type(current_obj).__name__,
			)
		)
	return current_obj, final_attr


def _navigate_to_parent_live(
	step_name: str, step_kwargs: dict[str, Any], path: list[str]
) -> tuple[Any, str]:
	"""Navigate to parent object for live nested set; return (parent_obj, final_attr)."""
	param_name = path[0]
	current_obj = step_kwargs[param_name]
	for attr in path[1:-1]:
		try:
			current_obj = getattr(current_obj, attr)
		except (AttributeError, TypeError, ValueError) as exc:
			raise typer.BadParameter(
				_tr(
					"Invalid nested argument path '{path}': attribute '{attr}' does not exist on '{obj_type}'.",
					path=f"{step_name}.{'.'.join(path)}",
					attr=attr,
					obj_type=type(current_obj).__name__,
				)
			) from exc
	return current_obj, path[-1]


def _coerce_final_value(
	param_name: str, final_attr: str, value: Any, origin: str
) -> Any:
	"""Coerce value for nested assignment (JSON or CLI scalar)."""
	full_param = f"{param_name}.{final_attr}"
	if origin == CLI_INPUT_SOURCE_JSON:
		from .factories import convert_value

		try:
			return _validate_json_param(full_param, convert_value(value))
		except (AttributeError, TypeError, ValueError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr(
					"Invalid JSON value for parameter '{param_name}': {error}",
					param_name=full_param,
					error=exc,
				)
			) from exc
	raw_value = _validate_cli_param(full_param, value)
	return _validate_cli_param(full_param, _parse_scalar(raw_value))


def _set_nested_step_value_dry_run(
	step_name: str, step_kwargs: dict[str, Any], path: list[str], value: Any, origin: str
) -> None:
	"""Handle dry-run nested step value assignment."""
	param_name = path[0]
	parent, final_attr = _navigate_to_parent_dry_run(step_name, step_kwargs, path)
	parent[final_attr] = _coerce_final_value(param_name, final_attr, value, origin)


def _set_nested_step_value_live(
	step_name: str,
	step_kwargs: dict[str, Any],
	path: list[str],
	value: Any,
	origin: str,
	adapter_states: dict[str, dict[str, str]] | None,
) -> None:
	"""Handle live nested step value assignment."""
	param_name = path[0]
	parent, final_attr = _navigate_to_parent_live(step_name, step_kwargs, path)
	adapter_state = None
	if adapter_states is not None:
		adapter_key = ".".join(path[:-1])
		adapter_state = adapter_states.setdefault(adapter_key, {})
	if origin != CLI_INPUT_SOURCE_JSON and adapter_state is not None:
		raw_value = _validate_cli_param(f"{param_name}.{final_attr}", value)
		try:
			if apply_wrapper_input_adapter(
				parent, final_attr, raw_value, applied_adapters=adapter_state
			):
				return
		except (AttributeError, TypeError, ValueError, RecursionError) as exc:
			raise typer.BadParameter(
				_tr(
					"Cannot set nested argument '{path}': {error}",
					path=f"{step_name}.{'.'.join(path)}",
					error=exc,
				)
			) from exc
	if not hasattr(parent, final_attr):
		raise typer.BadParameter(
			_tr(
				"Invalid nested argument path '{path}': attribute '{attr}' does not exist on '{obj_type}'.",
				path=f"{step_name}.{'.'.join(path)}",
				attr=final_attr,
				obj_type=type(parent).__name__,
			)
		)
	safe_val = _coerce_final_value(param_name, final_attr, value, origin)
	try:
		setattr(parent, final_attr, safe_val)
	except (AttributeError, TypeError, ValueError) as exc:
		raise typer.BadParameter(
			_tr(
				"Cannot set nested argument '{path}': {error}",
				path=f"{step_name}.{'.'.join(path)}",
				error=exc,
			)
		) from exc


def _set_nested_step_value(
	step_name: str,
	step_kwargs: dict[str, Any],
	path: list[str],
	value: Any,
	origin: str,
	*,
	adapter_states: dict[str, dict[str, str]] | None = None,
	dry_run: bool = False,
) -> None:
	if dry_run:
		_set_nested_step_value_dry_run(step_name, step_kwargs, path, value, origin)
	else:
		_set_nested_step_value_live(
			step_name, step_kwargs, path, value, origin, adapter_states
		)


def _normalize_step_items(
	items: list[ParsedItem],
	param_map: dict[str, inspect.Parameter] | None,
) -> list[ParsedItem]:
	normalized_items: list[ParsedItem] = []
	for path, value, origin in items:
		if not path:
			normalized_items.append((path, value, origin))
			continue
		param_name = path[0]
		if param_map is not None and param_name not in param_map:
			case_insensitive_name = next(
				(name for name in param_map if name.lower() == param_name.lower()),
				None,
			)
			if case_insensitive_name is not None:
				param_name = case_insensitive_name
		normalized_items.append(([param_name, *path[1:]], value, origin))
	return normalized_items


def _assign_step_item(
	*,
	step_name: str,
	path: list[str],
	value: Any,
	origin: str,
	param_map: dict[str, inspect.Parameter] | None,
	target: str,
	sig: Any,
	step_kwargs: dict[str, Any],
	dry_run: bool,
) -> None:
	if not path:
		raise typer.BadParameter(
			_tr(
				"Invalid argument for step '{step_name}': missing parameter name.",
				step_name=step_name,
			)
		)

	param_name = path[0]
	if param_map is not None and param_name not in param_map:
		accepts_kwargs = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in param_map.values())
		if not accepts_kwargs:
			known_params = ", ".join(sorted(param_map))
			suggestion = _closest_name(param_name, set(param_map))
			extra = _tr(" Known parameters: {known_params}.", known_params=known_params)
			if suggestion is not None:
				extra += _tr(" Did you mean '{parameter}'?", parameter=f"{step_name}.{suggestion}")
			extra += _tr(
				" Run 'describe {target}' to inspect accepted parameters and JSON examples.",
				target=target,
			)
			raise typer.BadParameter(
				_tr(
					"Unknown parameter '{parameter}' for {target}{signature}.{extra}",
					parameter=f"{step_name}.{param_name}",
					target=target,
					signature=sig,
					extra=extra,
				)
			)
		if len(path) > 1:
			raise typer.BadParameter(
				_tr(
					"Nested argument '{path}' is not supported for **kwargs on step '{step_name}'. "
					"Use a single key (e.g., {example}=...).",
					path=f"{step_name}.{'.'.join(path)}",
					step_name=step_name,
					example=f"{step_name}.{param_name}",
				)
			)
		step_kwargs[param_name] = _coerce_kwargs_value(param_name, value, origin, dry_run=dry_run)
		return

	param = param_map[param_name] if param_map is not None else None
	if len(path) == 1:
		step_kwargs[param_name] = _coerce_step_value(param_name, value, origin, param, dry_run=dry_run)
		return
	if param_name not in step_kwargs:
		if param is None:
			raise typer.BadParameter(
				_tr(
					"Cannot set nested attributes for '{param_name}' without signature info on '{step_name}'.",
					param_name=param_name,
					step_name=step_name,
				)
			)
		step_kwargs[param_name] = {} if dry_run else build_wrapper_instance(param.annotation)


def _apply_nullable_defaults(
	*,
	step_kwargs: dict[str, Any],
	param_map: dict[str, inspect.Parameter] | None,
) -> None:
	if param_map is None:
		return
	for param_name, param in param_map.items():
		if param_name in step_kwargs:
			continue
		if param.default is not inspect._empty:
			continue
		if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
			continue
		if _annotation_allows_none(param.annotation):
			step_kwargs[param_name] = None


def _build_step_kwargs(
	step: MethodStep,
	items: list[ParsedItem],
	target: str,
	*,
	dry_run: bool = False,
	qualify_parameter_names: bool = True,
) -> dict[str, Any]:
	step_name = step["name"]
	param_map = step["params"]
	sig = step["signature"]
	step_kwargs: dict[str, Any] = {}
	adapter_states: dict[str, dict[str, str]] = {}
	normalized_items = _normalize_step_items(items, param_map)

	_validate_step_item_path_conflicts(step_name, normalized_items)
	_ensure_required_step_params(
		step_name,
		param_map,
		normalized_items,
		target,
		sig,
		qualify_parameter_names=qualify_parameter_names,
	)

	for path, value, origin in normalized_items:
		_assign_step_item(
			step_name=step_name,
			path=path,
			value=value,
			origin=origin,
			param_map=param_map,
			target=target,
			sig=sig,
			step_kwargs=step_kwargs,
			dry_run=dry_run,
		)

	for path, value, origin in normalized_items:
		if len(path) > 1:
			_set_nested_step_value(
				step_name,
				step_kwargs,
				path,
				value,
				origin,
				adapter_states=adapter_states,
				dry_run=dry_run,
			)

	_apply_nullable_defaults(step_kwargs=step_kwargs, param_map=param_map)

	return step_kwargs
