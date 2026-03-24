# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import inspect
import json as _json
from typing import Any

from moldflow.i18n import get_text
from moldflow.cli_input_metadata import (
	CLI_VALUE_KIND_LIST_VALUES,
	CLI_VALUE_KIND_SELECTION_TEXT,
	CLI_VALUE_KIND_VECTOR_ARRAY_VALUES,
	CLI_VALUE_KIND_VECTOR_TRIPLET,
)

from .constants import CLI_FIELD_VALUE
from .wrapper_registry import resolve_wrapper_class, resolve_wrapper_name

_CLI_INPUT_ADAPTER_ATTR = "__moldflow_cli_input_adapter__"
_DIRECT_PARAM_SHORTHAND_KEY = CLI_FIELD_VALUE
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


@dataclass(frozen=True)
class _AdapterSpec:
	name: str
	method_name: str
	preferred_field: str
	value_kind: str
	shorthand_supported: bool


def _callable_params_from_callable(method: Any) -> tuple[inspect.Parameter, ...] | None:
	if not callable(method):
		return None
	try:
		signature = inspect.signature(method)
	except (TypeError, ValueError):
		return None
	return tuple(param for param in signature.parameters.values() if param.name != "self")


def _callable_params(target: Any, method_name: str) -> tuple[inspect.Parameter, ...] | None:
	method = getattr(target, method_name, None)
	return _callable_params_from_callable(method)


def _method_cli_input_metadata(method: Any) -> Any | None:
	return getattr(method, _CLI_INPUT_ADAPTER_ATTR, None)


def _annotation_text(annotation: Any) -> str:
	if annotation is inspect._empty:
		return ""
	if isinstance(annotation, str):
		return annotation.replace("typing.", "")
	if isinstance(annotation, type):
		return annotation.__name__
	return str(annotation).replace("typing.", "")


def _annotation_is_str(annotation: Any) -> bool:
	text = _annotation_text(annotation)
	return text == "" or text == "str"


def _annotation_is_list_like(annotation: Any) -> bool:
	text = _annotation_text(annotation).lower()
	if text == "":
		return True
	return text.startswith("list[") or text.startswith("tuple[") or text in {"list", "tuple"}


def _preferred_field_for_metadata(metadata: Any, params: tuple[inspect.Parameter, ...]) -> str | None:
	preferred_field = getattr(metadata, "preferred_field", None)
	if isinstance(preferred_field, str) and preferred_field:
		return preferred_field
	if len(params) == 1:
		return params[0].name
	return None


def _is_valid_metadata_shape(value_kind: str, params: tuple[inspect.Parameter, ...]) -> bool:
	if value_kind == CLI_VALUE_KIND_SELECTION_TEXT:
		return len(params) == 1 and _annotation_is_str(params[0].annotation)
	if value_kind == CLI_VALUE_KIND_LIST_VALUES:
		return len(params) == 1 and _annotation_is_list_like(params[0].annotation)
	if value_kind in {CLI_VALUE_KIND_VECTOR_TRIPLET, CLI_VALUE_KIND_VECTOR_ARRAY_VALUES}:
		return [param.name for param in params] == ["x", "y", "z"]
	return False


def _adapter_spec_from_method(method_name: str, method: Any) -> _AdapterSpec | None:
	metadata = _method_cli_input_metadata(method)
	if metadata is None:
		return None
	params = _callable_params_from_callable(method)
	if params is None:
		return None
	value_kind = getattr(metadata, "value_kind", None)
	if not isinstance(value_kind, str) or not _is_valid_metadata_shape(value_kind, params):
		return None
	preferred_field = _preferred_field_for_metadata(metadata, params)
	if preferred_field is None:
		return None
	return _AdapterSpec(
		name=value_kind,
		method_name=method_name,
		preferred_field=preferred_field,
		value_kind=value_kind,
		shorthand_supported=bool(getattr(metadata, "shorthand_supported", False)),
	)


@lru_cache(maxsize=None)
def _adapter_specs_for_class(wrapper_cls: type) -> tuple[_AdapterSpec, ...]:
	specs: list[_AdapterSpec] = []
	seen_methods: set[str] = set()
	for cls in wrapper_cls.__mro__:
		for method_name, member in vars(cls).items():
			if method_name in seen_methods:
				continue
			seen_methods.add(method_name)
			candidate = _adapter_spec_from_method(method_name, member)
			if candidate is not None:
				specs.append(candidate)
	return tuple(specs)


def _adapter_specs_for_target(target: Any) -> tuple[_AdapterSpec, ...]:
	wrapper_cls = target if inspect.isclass(target) else type(target)
	return _adapter_specs_for_class(wrapper_cls)


def _adapter_spec_for_field(target: Any, key: str) -> _AdapterSpec | None:
	for spec in _adapter_specs_for_target(target):
		if spec.preferred_field == key:
			return spec
	return None


def _shorthand_adapter_spec(target: Any) -> _AdapterSpec | None:
	candidates = [spec for spec in _adapter_specs_for_target(target) if spec.shorthand_supported]
	if len(candidates) != 1:
		return None
	return candidates[0]


def _ensure_adapter_unused(
	adapter_spec: _AdapterSpec,
	key: str,
	*,
	applied_adapters: dict[str, str],
	obj: Any,
) -> None:
	previous_key = applied_adapters.get(adapter_spec.name)
	if previous_key is not None:
		raise ValueError(
			_tr(
				"Fields '{previous_key}' and '{key}' both map to the same input for '{type_name}'. Provide only one of: {preferred_field} or direct parameter shorthand.",
				previous_key=previous_key,
				key=key,
				type_name=type(obj).__name__,
				preferred_field=adapter_spec.preferred_field,
			)
		)


def _is_number(value: Any) -> bool:
	return isinstance(value, (int, float)) and not isinstance(value, bool)


def _parse_shorthand_scalar(value: str) -> Any:
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


def _list_element_kind(annotation: Any) -> str | None:
	args = getattr(annotation, "__args__", ())
	if args:
		elem_type = args[0]
		if elem_type is int:
			return "int"
		if elem_type is float:
			return "float"
		if elem_type is str:
			return "str"
	text = _annotation_text(annotation).replace(" ", "")
	lower = text.lower()
	for prefix in ("list[", "tuple["):
		if lower.startswith(prefix) and lower.endswith("]"):
			inner = lower[len(prefix) : -1].split(",", maxsplit=1)[0]
			if inner in {"int", "float", "str"}:
				return inner
	return None


def _list_element_kind_for_spec(target: Any, spec: _AdapterSpec) -> str | None:
	params = _callable_params(target, spec.method_name)
	if params is None or not params:
		return None
	return _list_element_kind(params[0].annotation)


def _coerce_list_item(raw_value: str, *, element_kind: str | None, key: str, obj: Any) -> Any:
	if element_kind == "str":
		return raw_value
	if element_kind == "int":
		try:
			return int(raw_value)
		except ValueError as exc:
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must contain integer values.",
					key=key,
					type_name=type(obj).__name__,
				)
			) from exc
	if element_kind == "float":
		try:
			return float(raw_value)
		except ValueError as exc:
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must contain numeric values.",
					key=key,
					type_name=type(obj).__name__,
				)
			) from exc
	return _parse_shorthand_scalar(raw_value)


def _second_list_example_item(example_item: Any) -> Any:
	if isinstance(example_item, float):
		return 2.5
	if isinstance(example_item, int):
		return 2
	if isinstance(example_item, str):
		return "beta"
	return example_item


def _list_values_shorthand_example(target: Any, spec: _AdapterSpec) -> str:
	example_item = _example_item_for_list_spec(target, spec)
	second_item = _second_list_example_item(example_item)
	return f"{example_item},{second_item}"


def _coerce_list_values(value: Any, *, spec: _AdapterSpec, key: str, obj: Any) -> list[Any]:
	if isinstance(value, (list, tuple)):
		return list(value)
	if not isinstance(value, str):
		raise ValueError(
			_tr(
				"Field '{key}' for '{type_name}' must be a JSON array or a comma-separated list.",
				key=key,
				type_name=type(obj).__name__,
			)
		)
	text = value.strip()
	if not text:
		raise ValueError(
			_tr(
				"Field '{key}' for '{type_name}' must be a JSON array or a comma-separated list.",
				key=key,
				type_name=type(obj).__name__,
			)
		)
	if text.startswith("["):
		try:
			parsed = _json.loads(text)
		except _json.JSONDecodeError as exc:
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must be a valid JSON array or a comma-separated list.",
					key=key,
					type_name=type(obj).__name__,
				)
			) from exc
		if not isinstance(parsed, list):
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must be a JSON array or a comma-separated list.",
					key=key,
					type_name=type(obj).__name__,
				)
			)
		return parsed
	parts = [part.strip() for part in text.split(",")]
	if any(part == "" for part in parts):
		raise ValueError(
			_tr(
				"Field '{key}' for '{type_name}' must be a JSON array or a comma-separated list.",
				key=key,
				type_name=type(obj).__name__,
			)
		)
	element_kind = _list_element_kind_for_spec(obj, spec)
	return [
		_coerce_list_item(part, element_kind=element_kind, key=key, obj=obj)
		for part in parts
	]


def _coerce_triplet(value: Any, *, key: str, obj: Any) -> tuple[float, float, float]:
	if isinstance(value, str):
		parts = [part.strip() for part in value.split(",")]
		if len(parts) != 3 or any(part == "" for part in parts):
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must be a comma-separated numeric triplet like '0,0,1'.",
					key=key,
					type_name=type(obj).__name__,
				)
			)
		try:
			numbers = [float(part) for part in parts]
		except ValueError as exc:
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must be a comma-separated numeric triplet like '0,0,1'.",
					key=key,
					type_name=type(obj).__name__,
				)
			) from exc
		return numbers[0], numbers[1], numbers[2]

	if isinstance(value, (list, tuple)) and len(value) == 3 and all(_is_number(v) for v in value):
		return float(value[0]), float(value[1]), float(value[2])

	raise ValueError(
		_tr(
			"Field '{key}' for '{type_name}' must be a 3-item numeric sequence like [0, 0, 1].",
			key=key,
			type_name=type(obj).__name__,
		)
	)


def _vector_array_triplets(value: Any, *, key: str, obj: Any) -> list[tuple[float, float, float]]:
	if isinstance(value, str):
		text = value.strip()
		if not text:
			raise ValueError(
				_tr(
					"Field '{key}' for '{type_name}' must be a JSON array of triplets or a semicolon-separated list like '0,0,0;1,0,0'.",
					key=key,
					type_name=type(obj).__name__,
				)
			)
		if text.startswith("["):
			try:
				parsed = _json.loads(text)
			except _json.JSONDecodeError as exc:
				raise ValueError(
					_tr(
						"Field '{key}' for '{type_name}' must be a valid JSON array of triplets or a semicolon-separated list like '0,0,0;1,0,0'.",
						key=key,
						type_name=type(obj).__name__,
					)
				) from exc
			value = parsed
		else:
			parts = [part.strip() for part in text.split(";")]
			if any(part == "" for part in parts):
				raise ValueError(
					_tr(
						"Field '{key}' for '{type_name}' must be a JSON array of triplets or a semicolon-separated list like '0,0,0;1,0,0'.",
						key=key,
						type_name=type(obj).__name__,
					)
				)
			return [_coerce_triplet(part, key=f"{key}[{index}]", obj=obj) for index, part in enumerate(parts)]
	if not isinstance(value, (list, tuple)):
		raise ValueError(
			_tr(
				"Field '{key}' for '{type_name}' must be a list of numeric triplets.",
				key=key,
				type_name=type(obj).__name__,
			)
		)
	return [_coerce_triplet(item, key=f"{key}[{index}]", obj=obj) for index, item in enumerate(value)]


def _example_item_for_list_spec(target: Any, spec: _AdapterSpec) -> Any:
	params = _callable_params(target, spec.method_name)
	if params is None or not params:
		return "<value>"
	annotation = params[0].annotation
	args = getattr(annotation, "__args__", ())
	if args:
		elem_type = args[0]
		if elem_type is int:
			return 1
		if elem_type is float:
			return 1.0
		if elem_type is str:
			return "alpha"
	return "<value>"


def _call_adapter_method(obj: Any, spec: _AdapterSpec, *args: Any) -> Any:
	method = getattr(obj, spec.method_name, None)
	if not callable(method):
		raise ValueError(
			_tr(
				"'{type_name}' no longer exposes adapter method '{method_name}'.",
				type_name=type(obj).__name__,
				method_name=spec.method_name,
			)
		)
	return method(*args)


def _apply_selection_text_adapter(
	spec: _AdapterSpec,
	obj: Any,
	key: str,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	_ensure_adapter_unused(
		spec,
		key,
		applied_adapters=applied_adapters,
		obj=obj,
	)

	if not isinstance(value, str):
		raise ValueError(
			_tr(
				"Field '{key}' for '{type_name}' must be a string selection expression. Expected field: {preferred_field}.",
				key=key,
				type_name=type(obj).__name__,
				preferred_field=spec.preferred_field,
			)
		)

	_call_adapter_method(obj, spec, value)
	applied_adapters[spec.name] = key
	return True


def _apply_vector_triplet_adapter(
	spec: _AdapterSpec,
	obj: Any,
	key: str,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	_ensure_adapter_unused(
		spec,
		key,
		applied_adapters=applied_adapters,
		obj=obj,
	)
	x, y, z = _coerce_triplet(value, key=key, obj=obj)
	_call_adapter_method(obj, spec, x, y, z)
	applied_adapters[spec.name] = key
	return True


def _apply_list_values_adapter(
	spec: _AdapterSpec,
	obj: Any,
	key: str,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	_ensure_adapter_unused(
		spec,
		key,
		applied_adapters=applied_adapters,
		obj=obj,
	)
	value_list = _coerce_list_values(value, spec=spec, key=key, obj=obj)
	_call_adapter_method(obj, spec, value_list)
	applied_adapters[spec.name] = key
	return True


def _apply_vector_array_values_adapter(
	spec: _AdapterSpec,
	obj: Any,
	key: str,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	_ensure_adapter_unused(
		spec,
		key,
		applied_adapters=applied_adapters,
		obj=obj,
	)
	triplets = _vector_array_triplets(value, key=key, obj=obj)
	clear = getattr(obj, "clear", None)
	if callable(clear):
		clear()
	for x, y, z in triplets:
		_call_adapter_method(obj, spec, x, y, z)
	applied_adapters[spec.name] = key
	return True


def apply_wrapper_input_adapter(
	obj: Any,
	key: str,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	"""Apply user-friendly CLI input shapes for supported wrapper objects."""
	spec = _adapter_spec_for_field(obj, key)
	if spec is None:
		return False
	if spec.value_kind == CLI_VALUE_KIND_SELECTION_TEXT:
		return _apply_selection_text_adapter(spec, obj, key, value, applied_adapters=applied_adapters)
	if spec.value_kind == CLI_VALUE_KIND_VECTOR_TRIPLET:
		return _apply_vector_triplet_adapter(spec, obj, key, value, applied_adapters=applied_adapters)
	if spec.value_kind == CLI_VALUE_KIND_VECTOR_ARRAY_VALUES:
		return _apply_vector_array_values_adapter(spec, obj, key, value, applied_adapters=applied_adapters)
	if spec.value_kind == CLI_VALUE_KIND_LIST_VALUES:
		return _apply_list_values_adapter(spec, obj, key, value, applied_adapters=applied_adapters)
	return False


def apply_wrapper_shorthand_adapter(
	obj: Any,
	value: Any,
	*,
	applied_adapters: dict[str, str],
) -> bool:
	"""Apply non-JSON key=value shorthand inputs for supported wrapper objects."""
	spec = _shorthand_adapter_spec(obj)
	if spec is None:
		return False
	if spec.value_kind == CLI_VALUE_KIND_SELECTION_TEXT:
		return _apply_selection_text_adapter(
			spec,
			obj,
			_DIRECT_PARAM_SHORTHAND_KEY,
			value,
			applied_adapters=applied_adapters,
		)
	if spec.value_kind == CLI_VALUE_KIND_VECTOR_TRIPLET:
		return _apply_vector_triplet_adapter(
			spec,
			obj,
			_DIRECT_PARAM_SHORTHAND_KEY,
			value,
			applied_adapters=applied_adapters,
		)
	if spec.value_kind == CLI_VALUE_KIND_LIST_VALUES:
		return _apply_list_values_adapter(
			spec,
			obj,
			_DIRECT_PARAM_SHORTHAND_KEY,
			value,
			applied_adapters=applied_adapters,
		)
	if spec.value_kind == CLI_VALUE_KIND_VECTOR_ARRAY_VALUES:
		return _apply_vector_array_values_adapter(
			spec,
			obj,
			_DIRECT_PARAM_SHORTHAND_KEY,
			value,
			applied_adapters=applied_adapters,
		)
	return False


def _selection_text_adapter_hints(wrapper_type: str, spec: _AdapterSpec) -> dict[str, Any]:
	return {
		"typed_json_shape": {
			"__type__": wrapper_type,
			spec.preferred_field: "<selection string>",
		},
		"friendly_json_input": {
			"preferred_field": spec.preferred_field,
			"field_value_type": "string",
			"note": _tr(
				"Canonical JSON field is derived from the reflected wrapper method signature for {method_name}().",
				method_name=spec.method_name,
			),
		},
		"non_json_input": {
			"preferred_syntax": "<param>=<selection string>",
			"explicit_field_syntax": f"<param>.{spec.preferred_field}=<selection string>",
			"note": _T("Direct parameter assignment remains the preferred non-JSON form."),
		},
		"examples": {
			"preferred_param_value": {
				spec.preferred_field: "N1,N2",
			},
			"preferred_params_json": {
				"<param>": {
					spec.preferred_field: "N1,N2",
				}
			},
			"preferred_non_json": "<param>=N1,N2",
			"explicit_field_non_json": f"<param>.{spec.preferred_field}=N1,N2",
		},
	}


def _vector_triplet_adapter_hints(wrapper_type: str, spec: _AdapterSpec) -> dict[str, Any]:
	return {
		"typed_json_shape": {
			"__type__": wrapper_type,
			spec.preferred_field: [0.0, 0.0, 1.0],
		},
		"friendly_json_input": {
			"preferred_field": spec.preferred_field,
			"alternate_fields": ["x", "y", "z"],
			"field_value_type": "number[3]",
			"note": _tr(
				"Canonical triplet field is derived from the reflected wrapper method {method_name}().",
				method_name=spec.method_name,
			),
		},
		"non_json_input": {
			"preferred_syntax": "<param>=0,0,1",
			"explicit_field_syntax": f"<param>.{spec.preferred_field}=0,0,1",
			"note": _T("Use a comma-separated triplet for vector shorthand."),
		},
		"examples": {
			"preferred_param_value": {
				spec.preferred_field: [0.0, 0.0, 1.0],
			},
			"preferred_params_json": {
				"<param>": {
					spec.preferred_field: [0.0, 0.0, 1.0],
				}
			},
			"preferred_non_json": "<param>=0,0,1",
			"explicit_field_non_json": f"<param>.{spec.preferred_field}=0,0,1",
		},
	}


def _list_values_adapter_hints(
	wrapper_type: str,
	wrapper_cls: type,
	spec: _AdapterSpec,
) -> dict[str, Any]:
	example_item = _example_item_for_list_spec(wrapper_cls, spec)
	second_item = _second_list_example_item(example_item)
	shorthand_example = _list_values_shorthand_example(wrapper_cls, spec)
	return {
		"typed_json_shape": {
			"__type__": wrapper_type,
			spec.preferred_field: [example_item, second_item],
		},
		"friendly_json_input": {
			"preferred_field": spec.preferred_field,
			"field_value_type": "list",
			"note": _tr(
				"Canonical list field is derived from the reflected wrapper method {method_name}().",
				method_name=spec.method_name,
			),
		},
		"non_json_input": {
			"preferred_syntax": f"<param>={shorthand_example}",
			"explicit_field_syntax": f"<param>.{spec.preferred_field}={shorthand_example}",
			"note": _T(
				"Use a comma-separated list for quick CLI input, or a JSON array string when values contain commas."
			),
		},
		"examples": {
			"preferred_param_value": {
				spec.preferred_field: [example_item, second_item],
			},
			"preferred_params_json": {
				"<param>": {
					spec.preferred_field: [example_item, second_item],
				}
			},
			"preferred_non_json": f"<param>={shorthand_example}",
			"explicit_field_non_json": f"<param>.{spec.preferred_field}={shorthand_example}",
		},
	}


def _vector_array_values_adapter_hints(wrapper_type: str, spec: _AdapterSpec) -> dict[str, Any]:
	return {
		"typed_json_shape": {
			"__type__": wrapper_type,
			spec.preferred_field: [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
		},
		"friendly_json_input": {
			"preferred_field": spec.preferred_field,
			"field_value_type": "list[number[3]]",
			"note": _tr(
				"Canonical vector-array field is derived from the reflected wrapper method {method_name}().",
				method_name=spec.method_name,
			),
		},
		"non_json_input": {
			"preferred_syntax": "<param>=0,0,0;1,0,0",
			"explicit_field_syntax": f"<param>.{spec.preferred_field}=0,0,0;1,0,0",
			"note": _T(
				"Use semicolon-separated triplets for quick CLI input. Quote the value in shells that treat semicolons specially."
			),
		},
		"examples": {
			"preferred_param_value": {
				spec.preferred_field: [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
			},
			"preferred_params_json": {
				"<param>": {
					spec.preferred_field: [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
				}
			},
			"preferred_non_json": "<param>=0,0,0;1,0,0",
			"explicit_field_non_json": f"<param>.{spec.preferred_field}=0,0,0;1,0,0",
		},
	}



def _build_input_adapter_hints_for_class(wrapper_cls: type, wrapper_type: str) -> dict[str, Any] | None:
	hints: dict[str, Any] = {}
	for spec in _adapter_specs_for_target(wrapper_cls):
		if spec.value_kind == CLI_VALUE_KIND_SELECTION_TEXT:
			hints.update(_selection_text_adapter_hints(wrapper_type, spec))
		elif spec.value_kind == CLI_VALUE_KIND_VECTOR_TRIPLET:
			hints.update(_vector_triplet_adapter_hints(wrapper_type, spec))
		elif spec.value_kind == CLI_VALUE_KIND_VECTOR_ARRAY_VALUES:
			hints.update(_vector_array_values_adapter_hints(wrapper_type, spec))
		elif spec.value_kind == CLI_VALUE_KIND_LIST_VALUES:
			hints.update(_list_values_adapter_hints(wrapper_type, wrapper_cls, spec))
	return hints or None


def build_target_input_adapter_hints(target: Any) -> dict[str, Any] | None:
	"""Return user-facing hints for a specific wrapper instance or wrapper class."""
	wrapper_cls = target if inspect.isclass(target) else type(target)
	return _build_input_adapter_hints_for_class(wrapper_cls, wrapper_cls.__name__)


def build_wrapper_input_adapter_hints(wrapper_type: str) -> dict[str, Any] | None:
	"""Return user-facing template hints for wrapper-specific CLI adapters."""
	canonical_wrapper_type = resolve_wrapper_name(wrapper_type)
	wrapper_cls = resolve_wrapper_class(wrapper_type)
	if wrapper_cls is None or canonical_wrapper_type is None:
		return None
	return _build_input_adapter_hints_for_class(wrapper_cls, canonical_wrapper_type)