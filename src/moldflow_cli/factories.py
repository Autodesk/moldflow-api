# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Wrapper-construction helpers for CLI JSON and nested argument binding."""

from __future__ import annotations

from collections.abc import Iterator
from types import NoneType
from typing import Any
import inspect
import json as _json
import re

from moldflow.i18n import get_text

from .context import get_synergy
from .type_annotations import extract_non_none_type_names
from .wrapper_input_adapters import apply_wrapper_input_adapter
from .wrapper_registry import build_target_input_hints


_MISSING = object()
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
    text = _T(message)
    return text.format(**kwargs) if kwargs else text


def _matching_wrapper_type_metadata(
    obj: Any,
    data: dict[str, Any],
    *,
    expected_type: str | None = None,
) -> str | None:
    """Return a matching wrapper type tag when JSON metadata agrees with the target wrapper."""
    explicit_type = data.get("__type__")
    alias_type = data.get("type") if isinstance(data.get("type"), str) else None
    type_tag = explicit_type if isinstance(explicit_type, str) else alias_type
    if type_tag is None:
        return None
    expected_names = {type(obj).__name__}
    if isinstance(expected_type, str) and expected_type.strip():
        expected_names.add(expected_type.strip())
    if not type_tag.strip():
        primary_expected = expected_type or type(obj).__name__
        raise ValueError(
            _tr(
                "Empty type tag is not valid for '{primary_expected}'.",
                primary_expected=primary_expected,
            )
        )
    normalized_tag = type_tag.strip().lower()
    if all(normalized_tag != candidate.lower() for candidate in expected_names):
        primary_expected = expected_type or type(obj).__name__
        raise ValueError(
            _tr(
                "JSON type tag '{type_tag}' does not match expected wrapper '{primary_expected}'.",
                type_tag=type_tag,
                primary_expected=primary_expected,
            )
        )
    return type_tag


def _is_none_annotation(value: Any) -> bool:
    """Return True when a type annotation represents NoneType."""
    return value is NoneType


def camel_to_snake(name: str) -> str:
    """
    Best-effort CamelCase to snake_case converter for mapping class names
    to Synergy properties (e.g., ImportOptions -> import_options).
    """
    # Split at acronym-to-word boundaries and lower-to-upper transitions:
    # CADManager -> cad_manager, ImportOptions -> import_options.
    stage1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    stage2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stage1)
    return stage2.lower()


def _safe_getattr(obj: Any, attr_name: str) -> Any:
    try:
        return getattr(obj, attr_name)
    except (AttributeError, TypeError, ValueError, RuntimeError):
        return None


def _get_public_attr_value(obj: Any, attr_name: str) -> Any:
    if attr_name.startswith("_"):
        return _MISSING
    obj_dict = getattr(obj, "__dict__", {})
    if attr_name in obj_dict:
        value = obj_dict[attr_name]
        return value if not callable(value) else _MISSING
    try:
        descriptor = inspect.getattr_static(type(obj), attr_name)
    except AttributeError:
        return _MISSING
    if isinstance(descriptor, property) or hasattr(obj, attr_name):
        try:
            value = getattr(obj, attr_name)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return _MISSING
        return value if not callable(value) else _MISSING
    return _MISSING


def _can_set_public_attr(obj: Any, attr_name: str) -> bool:
    if attr_name.startswith("_"):
        return False
    if attr_name in getattr(obj, "__dict__", {}):
        return True
    try:
        descriptor = inspect.getattr_static(type(obj), attr_name)
    except AttributeError:
        return False
    if isinstance(descriptor, property):
        return descriptor.fset is not None
    if not hasattr(obj, attr_name):
        return False
    value = _safe_getattr(obj, attr_name)
    return value is not None and not callable(value)


def _is_nested_wrapper_candidate(value: Any) -> bool:
    return value is not _MISSING and value is not None and not isinstance(
        value,
        (str, int, float, bool, list, tuple, dict, set),
    )


def _format_json_snippet(value: Any) -> str:
    try:
        return _json.dumps(value, ensure_ascii=True)
    except (TypeError, ValueError):
        return repr(value)


def _wrapper_input_guidance(obj: Any) -> str | None:
    hints = build_target_input_hints(obj)
    if not isinstance(hints, dict):
        return None
    friendly_json_input = hints.get("friendly_json_input")
    examples = hints.get("examples")
    guidance_parts: list[str] = []
    if isinstance(friendly_json_input, dict):
        preferred_field = friendly_json_input.get("preferred_field")
        if isinstance(preferred_field, str) and preferred_field:
            guidance_parts.append(
                _tr("Use JSON field '{preferred_field}'.", preferred_field=preferred_field)
            )
    if isinstance(examples, dict):
        preferred_param_value = examples.get("preferred_param_value")
        if isinstance(preferred_param_value, dict) and preferred_param_value:
            guidance_parts.append(
                _tr(
                    "Example object template: {shape}.",
                    shape=_format_json_snippet(preferred_param_value),
                )
            )
        preferred_non_json = examples.get("preferred_non_json")
        if isinstance(preferred_non_json, str) and preferred_non_json:
            guidance_parts.append(
                _tr(
                    "In non-JSON mode, prefer direct shorthand like '{preferred_non_json}'.",
                    preferred_non_json=preferred_non_json,
                )
            )
    return " ".join(guidance_parts) if guidance_parts else None


def _unknown_wrapper_field_message(obj: Any, key_name: str) -> str:
    message = _tr(
        "Field '{key_name}' is not valid for '{type_name}'.",
        key_name=key_name,
        type_name=type(obj).__name__,
    )
    guidance = _wrapper_input_guidance(obj)
    if guidance:
        return f"{message} {guidance}"
    return message


def _iter_public_attr_names(obj: Any) -> Iterator[str]:
    seen: set[str] = set()
    for name in vars(obj):
        if name.startswith("_"):
            continue
        seen.add(name)
        yield name
    for cls in type(obj).__mro__:
        for name, descriptor in vars(cls).items():
            if name.startswith("_") or name in seen or not isinstance(descriptor, property):
                continue
            seen.add(name)
            yield name


def _iter_synergy_related_objects(synergy: Any) -> Iterator[Any]:
    seen_ids = {id(synergy)}
    yield synergy
    for attr_name in _iter_public_attr_names(synergy):
        candidate = _safe_getattr(synergy, attr_name)
        if candidate is None:
            continue
        candidate_id = id(candidate)
        if candidate_id in seen_ids:
            continue
        seen_ids.add(candidate_id)
        yield candidate


def _build_from_synergy_property(synergy: Any, type_name: str) -> Any:
    attr_name = camel_to_snake(type_name)
    if hasattr(synergy, attr_name):
        return getattr(synergy, attr_name)
    return None


def _build_ent_list_instance(synergy: Any) -> Any:
    for provider in _iter_synergy_related_objects(synergy):
        factory = _safe_getattr(provider, "create_entity_list")
        if callable(factory):
            return factory()
    raise ValueError(
        _T("Cannot build instance for type 'EntList'. No create_entity_list provider found.")
    )


def _build_from_synergy_factory_method(synergy: Any, type_name: str) -> Any:
    factory_name = f"create_{camel_to_snake(type_name)}"
    factory = _safe_getattr(synergy, factory_name)
    if not callable(factory):
        return None
    return factory()


def build_wrapper_instance(type_hint: Any) -> Any:
    """
    Create an instance of a wrapper class that normally comes from Synergy.
    This is contextual: we resolve via Synergy properties or factory methods.
    """
    type_names = extract_non_none_type_names(type_hint)
    if len(type_names) == 1:
        type_name = type_names[0]
    elif isinstance(type_hint, str):
        type_name = type_hint.strip().strip("'\"")
    else:
        type_name = getattr(type_hint, "__name__", str(type_hint))

    synergy = get_synergy()
    instance = _build_from_synergy_property(synergy, type_name)
    if instance is not None:
        return instance

    if type_name == "EntList":
        return _build_ent_list_instance(synergy)

    instance = _build_from_synergy_factory_method(synergy, type_name)
    if instance is not None:
        return instance

    raise ValueError(
        _tr(
            "Cannot build instance for type '{type_name}'. "
            "Not a known Synergy property or factory.",
            type_name=type_name,
        )
    )


def configure_object_from_dict(
    obj: Any,
    data: dict[str, Any],
    *,
    expected_type: str | None = None,
) -> Any:
    """
    Set attributes on wrapper objects using simple assignment/property setters.
    Supports nested constructions for values shaped as {'__type__': str, ...}.
    """
    _matching_wrapper_type_metadata(obj, data, expected_type=expected_type)
    applied_adapters: dict[str, str] = {}
    for key, value in data.items():
        key_name = str(key)
        if key_name == "__type__":
            continue
        if key_name == "type" and isinstance(value, str):
            continue
        if apply_wrapper_input_adapter(
            obj,
            key_name,
            value,
            applied_adapters=applied_adapters,
        ):
            continue
        if key_name.startswith("_"):
            raise ValueError(
                _tr(
                    "Non-public field '{key_name}' is not allowed "
                    "when constructing '{type_name}' from JSON.",
                    key_name=key_name,
                    type_name=type(obj).__name__,
                )
            )
        existing_attr = _get_public_attr_value(obj, key_name)
        if (
            isinstance(value, dict)
            and "__type__" not in value
            and _is_nested_wrapper_candidate(existing_attr)
        ):
            try:
                configure_object_from_dict(existing_attr, value)
            except (AttributeError, TypeError, ValueError, RecursionError) as exc:
                raise ValueError(
                    _tr(
                        "Cannot configure field '{key_name}' on '{type_name}': {error}",
                        key_name=key_name,
                        type_name=type(obj).__name__,
                        error=exc,
                    )
                ) from exc
            if _can_set_public_attr(obj, key_name):
                setattr(obj, key_name, existing_attr)
            continue
        if not _can_set_public_attr(obj, key_name):
            raise ValueError(_unknown_wrapper_field_message(obj, key_name))
        try:
            setattr(obj, key, convert_value(value))
        except (AttributeError, TypeError, ValueError, RecursionError) as exc:
            guidance = _wrapper_input_guidance(obj)
            if guidance:
                raise ValueError(f"{exc} {guidance}") from exc
            raise
    return obj


def convert_value(value: Any) -> Any:
    """
    Convert a value possibly containing nested typed dicts into wrapper instances.
    Accepted shapes:
    - primitives (str, int, float, bool, None)
    - lists/tuples of primitives or nested objects
    - dicts: either plain mappings passed as-is, or typed objects:
      {'__type__': 'ImportOptions', ...}
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [convert_value(v) for v in value]
    if isinstance(value, dict):
        type_tag = value.get("__type__")
        if type_tag:
            instance = build_wrapper_instance(type_tag)
            return configure_object_from_dict(instance, value, expected_type=type_tag)
        # Plain dict; pass through
        return {k: convert_value(v) for k, v in value.items()}
    return value
