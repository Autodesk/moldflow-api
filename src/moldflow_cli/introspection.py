# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
import inspect
import re
from functools import lru_cache
from typing import Any

from moldflow.i18n import get_text

from .constants import CLI_ROOT_MOLDFLOW
from .target_resolution import resolve_attr_name_case_insensitive
from .type_annotations import extract_non_none_type_names, format_annotation_text


_RST_FIELD_LINE = re.compile(r"^:[A-Za-z_][\w-]*:\s*")
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
    text = _T(message)
    return text.format(**kwargs) if kwargs else text


class HiddenCliTargetError(ValueError):
    """Raised when a target resolves through a member intentionally hidden from the CLI."""


def _public_class_lookup() -> dict[str, type]:
    """Map public wrapper type names and CLI aliases to their classes."""
    from .wrapper_registry import public_wrapper_alias_lookup

    return dict(public_wrapper_alias_lookup())


def _resolve_annotation_class(annotation: Any, class_lookup: dict[str, type]) -> type | None:
    """Resolve a return annotation to a known public wrapper class."""
    if isinstance(annotation, type):
        for cls in class_lookup.values():
            if cls is annotation:
                return cls

    matches: list[type] = []
    for type_name in extract_non_none_type_names(annotation):
        cls = class_lookup.get(type_name.lower())
        if cls is not None and cls not in matches:
            matches.append(cls)
    if len(matches) == 1:
        return matches[0]
    return None


def _resolve_next_chain_context(current: Any, attr_name: str, class_lookup: dict[str, type]) -> Any:
    """Return the next introspection context for a chained target segment."""
    if inspect.isclass(current):
        raw_attr = inspect.getattr_static(current, attr_name)
        if isinstance(raw_attr, property):
            if raw_attr.fget is None:
                return None
            try:
                getter_sig = inspect.signature(raw_attr.fget)
            except (TypeError, ValueError):
                return None
            return _resolve_annotation_class(getter_sig.return_annotation, class_lookup)
        if isinstance(raw_attr, (staticmethod, classmethod)):
            callable_obj = raw_attr.__func__
        else:
            callable_obj = getattr(current, attr_name)
    else:
        callable_obj = getattr(current, attr_name)

    if inspect.isclass(callable_obj):
        return callable_obj
    if not callable(callable_obj):
        return None
    try:
        callable_sig = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return None
    return _resolve_annotation_class(callable_sig.return_annotation, class_lookup)


def _cli_visibility_member(current: Any, attr_name: str) -> Any | None:
    """Return the underlying member object used for CLI visibility metadata checks."""
    try:
        if inspect.isclass(current):
            raw_attr = inspect.getattr_static(current, attr_name)
        else:
            raw_attr = inspect.getattr_static(type(current), attr_name)
    except AttributeError:
        return getattr(current, attr_name, None)

    if isinstance(raw_attr, property):
        return raw_attr.fget
    if isinstance(raw_attr, (staticmethod, classmethod)):
        return raw_attr.__func__
    return raw_attr


def _member_cli_visibility_metadata(member: Any) -> Any | None:
    """Return library-declared CLI visibility metadata for a member, if present."""
    try:
        from moldflow.cli_input_metadata import get_cli_visibility_metadata
    except ImportError:
        return None
    return get_cli_visibility_metadata(member)


def _transient_wrapper_factory_hidden_reason() -> str | None:
    """Return the library marker used for transient wrapper factory helpers."""
    try:
        from moldflow.cli_input_metadata import CLI_HIDDEN_REASON_TRANSIENT_WRAPPER_FACTORY
    except ImportError:
        return None
    return CLI_HIDDEN_REASON_TRANSIENT_WRAPPER_FACTORY


def _hidden_wrapper_type_name(member: Any) -> str | None:
    """Return a compact wrapper type name for a hidden factory member, if inspectable."""
    if member is None or not callable(member):
        return None
    try:
        signature = inspect.signature(member)
    except (TypeError, ValueError):
        return None
    type_names = extract_non_none_type_names(signature.return_annotation)
    if len(type_names) == 1:
        return type_names[0]
    if signature.return_annotation is inspect.Parameter.empty or signature.return_annotation is None:
        return None
    text = format_annotation_text(signature.return_annotation)
    return text or None


def hidden_cli_target_details(target: str) -> dict[str, Any] | None:
    """Return metadata for a target hidden by library CLI visibility decorators."""
    from .factories import camel_to_snake

    parts = [part for part in target.split(".") if part]
    if not parts:
        return None
    if parts[0].lower() == CLI_ROOT_MOLDFLOW:
        parts = parts[1:]
    if not parts:
        return None

    mf = importlib.import_module("moldflow")
    class_lookup = _public_class_lookup()
    first, *rest = parts
    first_lower = first.lower()

    current = getattr(mf, first, None)
    if current is None or inspect.ismodule(current):
        current = None
        for name, cls in iter_public_classes():
            if camel_to_snake(name) == first_lower:
                current = cls
                break
    if current is None:
        return None

    resolved_path = [first]
    for index, attr_name in enumerate(rest):
        matched_name = resolve_attr_name_case_insensitive(current, attr_name, static_lookup=True)
        if matched_name is None:
            return None
        member = _cli_visibility_member(current, matched_name)
        metadata = _member_cli_visibility_metadata(member)
        hidden_path = ".".join([*resolved_path, matched_name])
        if metadata is not None and getattr(metadata, "hidden", False):
            return {
                "hidden_path": hidden_path,
                "member": member,
                "metadata": metadata,
            }
        if index == len(rest) - 1:
            return None
        next_context = _resolve_next_chain_context(current, matched_name, class_lookup)
        if next_context is None:
            return None
        current = next_context
        resolved_path.append(matched_name)
    return None


def is_cli_target_hidden(target: str) -> bool:
    """Return True when a target or any parent surface is hidden from the CLI."""
    return hidden_cli_target_details(target) is not None


def validate_cli_target_visible(target: str) -> None:
    """Raise when a target is intentionally hidden from CLI discovery/invocation."""
    hidden_details = hidden_cli_target_details(target)
    if hidden_details is None:
        return

    hidden_path = hidden_details["hidden_path"]
    member = hidden_details.get("member")
    metadata = hidden_details["metadata"]
    message_template = getattr(metadata, "message", None)
    wrapper_type = _hidden_wrapper_type_name(member) or "wrapper"
    transient_hidden_reason = _transient_wrapper_factory_hidden_reason()

    if isinstance(message_template, str) and message_template:
        raise HiddenCliTargetError(
            message_template.format(
                target=target,
                hidden_path=hidden_path,
                wrapper_type=wrapper_type,
            )
        )

    if transient_hidden_reason is not None and getattr(metadata, "reason", None) == transient_hidden_reason:
        raise HiddenCliTargetError(
            _tr(
                "Target '{target}' is hidden from the CLI because '{hidden_path}' only creates a "
                "transient {wrapper_type} wrapper. The CLI constructs these helper objects "
                "internally when needed, so they are not exposed as direct CLI targets.",
                target=target,
                hidden_path=hidden_path,
                wrapper_type=wrapper_type,
            )
        )

    raise HiddenCliTargetError(
        _tr(
            "Target '{target}' is hidden from the CLI by library metadata on '{hidden_path}'.",
            target=target,
            hidden_path=hidden_path,
        )
    )


@lru_cache(maxsize=8)
def _iter_public_classes_cached(snapshot: tuple[tuple[str, int], ...]) -> tuple[tuple[str, type], ...]:
    """Return public wrapper classes for a stable moldflow export snapshot."""
    mf = importlib.import_module("moldflow")
    return tuple((name, getattr(mf, name)) for name, _ in snapshot)


def iter_public_classes() -> list[tuple[str, type]]:
    """
    Collect top-level wrapper classes from moldflow by importing the package
    and walking attributes on the module that are classes.
    """
    mf = importlib.import_module("moldflow")
    snapshot = tuple(
        sorted(
            (name, id(obj))
            for name, obj in vars(mf).items()
            if not name.startswith("_") and inspect.isclass(obj)
        )
    )
    return list(_iter_public_classes_cached(snapshot))


def _parse_target_parts(target: str) -> tuple[list[str], str]:
    """Parse and validate target string; return (parts, first_lower)."""
    parts = [p for p in target.split(".") if p]
    if not parts:
        raise ValueError(_T("Empty target"))
    if parts[0].lower() == CLI_ROOT_MOLDFLOW:
        parts = parts[1:]
    if not parts:
        raise ValueError(_T("Target must include a class or function name"))
    return parts, parts[0].lower()


def _resolve_first_segment(parts: list[str], first_lower: str) -> Any:
    """Resolve the first segment of a target to an object on the moldflow module."""
    from .factories import camel_to_snake

    mf = importlib.import_module("moldflow")
    first = parts[0]
    obj = getattr(mf, first, None)
    if obj is None or inspect.ismodule(obj):
        for name, cls in iter_public_classes():
            if camel_to_snake(name) == first_lower:
                obj = cls
                break
    if obj is None:
        raise AttributeError(
            _tr("Cannot resolve '{first}' on moldflow for introspection", first=first)
        )
    return obj


def _find_matched_attr_name(current: Any, attr_name: str) -> str:
    """Case-insensitive attribute lookup; raise AttributeError if not found."""
    if hasattr(current, attr_name):
        return attr_name
    attr_lower = attr_name.lower()
    matched_name = next((name for name in dir(current) if name.lower() == attr_lower), None)
    if matched_name is None:
        if inspect.isclass(current):
            raise AttributeError(
                _tr(
                    "Class '{class_name}' has no attribute '{attr_name}'",
                    class_name=current.__name__,
                    attr_name=attr_name,
                )
            )
        raise AttributeError(
            _tr(
                "Object '{type_name}' has no attribute '{attr_name}'",
                type_name=type(current).__name__,
                attr_name=attr_name,
            )
        )
    return matched_name


def _raise_non_wrapper_continuation(
    current: Any, matched_name: str, next_segment: str | None
) -> None:
    """Raise AttributeError for non-wrapper continuation."""
    continuation = (
        f"; cannot continue to '{next_segment}'"
        if isinstance(next_segment, str) and next_segment
        else ""
    )
    if inspect.isclass(current):
        raise AttributeError(
            _tr(
                "Attribute '{matched_name}' on class '{class_name}' returns a non-wrapper value{continuation}",
                matched_name=matched_name,
                class_name=current.__name__,
                continuation=continuation,
            )
        )
    raise AttributeError(
        _tr(
            "Attribute '{matched_name}' on object '{type_name}' returns a non-wrapper value{continuation}",
            matched_name=matched_name,
            type_name=type(current).__name__,
            continuation=continuation,
        )
    )


def resolve_for_introspection(target: str) -> Any:
    """
    Resolve a target for documentation/signature purposes only.
    This MUST NOT instantiate Synergy or any COM objects.

    We operate purely on the moldflow module and its exported classes.
    Targets can use either CamelCase class names (Synergy) or the
    snake_case CLI names (synergy, import_options, mesh_generator, ...).
    """
    parts, first_lower = _parse_target_parts(target)
    obj = _resolve_first_segment(parts, first_lower)
    rest = parts[1:]
    if not rest:
        return obj

    class_lookup = _public_class_lookup()
    current = obj
    for index, attr_name in enumerate(rest):
        matched_name = _find_matched_attr_name(current, attr_name)
        if index == len(rest) - 1:
            return getattr(current, matched_name)
        next_context = _resolve_next_chain_context(current, matched_name, class_lookup)
        if next_context is None:
            next_segment = rest[index + 1] if index + 1 < len(rest) else None
            _raise_non_wrapper_continuation(current, matched_name, next_segment)
        current = next_context

    return current


def get_signature_string(obj: Any) -> str:
    try:
        sig = inspect.signature(obj)
        return str(sig)
    except (TypeError, ValueError):
        return "(...)"


def get_docstring(obj: Any) -> str:
    doc = inspect.getdoc(obj) or ""
    return doc.strip()


def split_structured_doc(doc: str, *, obj_type: str | None) -> tuple[str | None, str | None]:
    """Return compact summary/details text for structured payloads."""
    lines = [line.rstrip() for line in doc.splitlines()]
    if obj_type == "property":
        lines = [line for line in lines if not _RST_FIELD_LINE.match(line.strip())]

    paragraphs: list[str] = []
    current_paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
            continue
        current_paragraph.append(stripped)
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    if not paragraphs:
        return None, None
    return paragraphs[0], " ".join(paragraphs[1:]) or None


