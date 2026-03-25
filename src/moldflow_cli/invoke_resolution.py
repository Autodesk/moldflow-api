from __future__ import annotations

import inspect
from typing import Any, Optional

import typer

from moldflow.i18n import get_text

from .constants import CLI_KIND_PROPERTY_GETTER, CLI_KIND_PROPERTY_SETTER_ONLY
from .factories import camel_to_snake
from .introspection import HiddenCliTargetError, validate_cli_target_visible
from .invoke_engine import _ResolvedInvokeTarget
from .invoke_runtime import _signature_and_param_map
from .target_resolution import (
	canonicalize_invoke_target,
	resolve_attr_name_case_insensitive,
	resolve_callable_attr_case_insensitive,
	split_dotted_path,
)
from .type_annotations import extract_non_none_type_names
from .wrapper_registry import public_wrapper_cli_map


MethodStep = dict[str, Any]
_T = get_text()


def _match_wrapper_classes_by_type_names(
	type_names: list[str],
	cli_to_class: dict[str, type],
) -> set[type]:
	matches: set[type] = set()
	classes = set(cli_to_class.values())
	for type_name in type_names:
		normalized_type_name = type_name.lower()
		for key, cls in cli_to_class.items():
			if isinstance(key, str) and key.lower() == normalized_type_name:
				matches.add(cls)
		for cls in classes:
			class_name = getattr(cls, "__name__", "")
			if not isinstance(class_name, str) or not class_name:
				continue
			if class_name.lower() == normalized_type_name:
				matches.add(cls)
				continue
			if camel_to_snake(class_name).lower() == normalized_type_name:
				matches.add(cls)
	return matches


def _extract_wrapper_type_names_from_annotation(annotation: Any) -> list[str]:
	return extract_non_none_type_names(annotation)


def _resolve_return_class(ret: Any, cli_to_class: dict[str, type]) -> Optional[type]:
	"""Best-effort resolve of a return annotation to a known wrapper class."""
	if ret is inspect._empty:
		return None

	if isinstance(ret, type):
		for cls in cli_to_class.values():
			if cls is ret:
				return cls

	matches = _match_wrapper_classes_by_type_names(
		_extract_wrapper_type_names_from_annotation(ret),
		cli_to_class,
	)
	if len(matches) == 1:
		return next(iter(matches))
	return None


def _has_ambiguous_wrapper_union(ret: Any, cli_to_class: dict[str, type]) -> bool:
	"""Return True when return annotation names multiple possible wrapper classes."""
	if ret is inspect._empty:
		return False

	matches = _match_wrapper_classes_by_type_names(
		_extract_wrapper_type_names_from_annotation(ret),
		cli_to_class,
	)
	return len(matches) > 1


def _classify_terminal_class_attr(cls: type, attr_name: str) -> str:
	"""Classify a terminal class attribute for invoke target validation."""
	try:
		raw_attr = inspect.getattr_static(cls, attr_name)
	except AttributeError:
		return "attribute"
	if isinstance(raw_attr, property):
		if raw_attr.fget is None:
			return CLI_KIND_PROPERTY_SETTER_ONLY
		return CLI_KIND_PROPERTY_GETTER
	return "attribute"


def _canonicalize_invoke_target(target: str) -> str:
	return canonicalize_invoke_target(target, translate=get_text())


def _normalize_invoke_target_parts(target: str) -> list[str]:
	canonical_target = _canonicalize_invoke_target(target)
	return split_dotted_path(canonical_target, field_name="target", translate=_T)


def _build_cli_to_class_map() -> dict[str, type]:
	return dict(public_wrapper_cli_map())


def _validate_unique_step_names(method_steps: list[MethodStep]) -> None:
	method_name_counts: dict[str, int] = {}
	for step in method_steps:
		key = step["name"].lower()
		method_name_counts[key] = method_name_counts.get(key, 0) + 1
	duplicate_step_names = sorted(
		{step["name"] for step in method_steps if method_name_counts[step["name"].lower()] > 1}
	)
	if duplicate_step_names:
		raise typer.BadParameter(
			_T(
				"Chained targets with repeated method names are ambiguous for argument routing: "
				"{duplicate_names}. "
				"Please use an equivalent target path where each invoked step name is unique."
			).format(duplicate_names=", ".join(duplicate_step_names))
		)


def _append_deferred_method_step(method_steps: list[MethodStep], segment: str) -> None:
	method_steps.append(
		{
			"name": segment,
			"callable": None,
			"signature": None,
			"params": None,
			"class": None,
		}
	)


def _resolve_callable_candidate_for_segment(
	current_cls: type | None,
	segment: str,
) -> tuple[str | None, Any | None]:
	if current_cls is None:
		return None, None
	try:
		return resolve_callable_attr_case_insensitive(current_cls, segment)
	except AttributeError:
		return None, None


def _resolve_class_alias_segment(
	*,
	parts: list[str],
	index: int,
	segment: str,
	current_cls: type | None,
	cli_to_class: dict[str, type],
	target: str,
) -> type:
	if current_cls is not None:
		try:
			canonical_attr = resolve_attr_name_case_insensitive(current_cls, segment)
			if canonical_attr is None:
				raise AttributeError(segment)
		except AttributeError as exc:
			raise typer.BadParameter(
				_T(
					"Segment '{segment}' does not resolve as an attribute on class "
					"'{class_name}' when resolving target '{target}'"
				).format(segment=segment, class_name=current_cls.__name__, target=target)
			) from exc
		parts[index] = canonical_attr
	return cli_to_class[segment.lower()]


def _record_callable_step(
	*,
	parts: list[str],
	index: int,
	step_name: str,
	callable_attr: Any,
	method_steps: list[MethodStep],
	current_cls: type,
	cli_to_class: dict[str, type],
	runtime_deferred_mode: bool,
) -> tuple[type | None, bool]:
	parts[index] = step_name
	sig, param_map = _signature_and_param_map(callable_attr)
	method_steps.append(
		{
			"name": step_name,
			"callable": callable_attr,
			"signature": sig,
			"params": param_map,
			"class": current_cls,
		}
	)
	if sig is None:
		return current_cls, runtime_deferred_mode

	ret_cls = _resolve_return_class(sig.return_annotation, cli_to_class)
	if ret_cls is not None:
		return ret_cls, False
	if _has_ambiguous_wrapper_union(sig.return_annotation, cli_to_class):
		return None, True
	return current_cls, runtime_deferred_mode


def _resolve_non_callable_segment(
	*,
	parts: list[str],
	index: int,
	segment: str,
	current_cls: type,
	runtime_deferred_mode: bool,
	method_steps: list[MethodStep],
	target: str,
) -> dict[str, str] | None:
	canonical_attr = resolve_attr_name_case_insensitive(current_cls, segment)

	if canonical_attr is not None and index == len(parts) - 1:
		attr_kind = _classify_terminal_class_attr(current_cls, canonical_attr)
		if attr_kind == CLI_KIND_PROPERTY_SETTER_ONLY:
			raise typer.BadParameter(
				_T(
					"Target '{target}' resolves to write-only property '{property_name}' "
					"and cannot be read via invoke."
				).format(target=target, property_name=canonical_attr)
			)
		parts[index] = canonical_attr
		return {"name": canonical_attr, "kind": attr_kind}

	if runtime_deferred_mode:
		_append_deferred_method_step(method_steps, segment)
		return None

	raise typer.BadParameter(
		_T(
			"Segment '{segment}' is not a callable method on class '{class_name}' "
			"when resolving target '{target}'"
		).format(segment=segment, class_name=current_cls.__name__, target=target)
	)


def _resolve_invoke_steps(target: str) -> _ResolvedInvokeTarget:
	canonical_target = _canonicalize_invoke_target(target)
	try:
		validate_cli_target_visible(canonical_target)
	except HiddenCliTargetError as exc:
		raise typer.BadParameter(str(exc)) from exc
	parts = _normalize_invoke_target_parts(canonical_target)
	cli_to_class = _build_cli_to_class_map()
	method_steps: list[MethodStep] = []
	current_cls = None
	runtime_deferred_mode = False
	terminal_target_info: dict[str, str] | None = None

	for idx, seg in enumerate(parts):
		seg_lower = seg.lower()
		callable_candidate_name, callable_candidate = _resolve_callable_candidate_for_segment(
			current_cls,
			seg,
		)

		if seg_lower in cli_to_class and callable_candidate is None:
			prefer_terminal_attr = False
			if current_cls is not None and idx == len(parts) - 1:
				prefer_terminal_attr = (
					resolve_attr_name_case_insensitive(current_cls, seg) is not None
				)
			if not prefer_terminal_attr:
				current_cls = _resolve_class_alias_segment(
					parts=parts,
					index=idx,
					segment=seg,
					current_cls=current_cls,
					cli_to_class=cli_to_class,
					target=canonical_target,
				)
				continue
		if current_cls is None:
			if runtime_deferred_mode:
				_append_deferred_method_step(method_steps, seg)
				continue
			raise typer.BadParameter(
				_T(
					"Cannot resolve segment '{segment}' in target '{target}' without a class context. "
					"Use a Synergy-rooted target such as 'synergy.some_method'."
				).format(segment=seg, target=canonical_target)
			)
		if callable_candidate is None or callable_candidate_name is None:
			terminal_info = _resolve_non_callable_segment(
				parts=parts,
				index=idx,
				segment=seg,
				current_cls=current_cls,
				runtime_deferred_mode=runtime_deferred_mode,
				method_steps=method_steps,
				target=canonical_target,
			)
			if terminal_info is not None:
				terminal_target_info = terminal_info
			continue

		current_cls, runtime_deferred_mode = _record_callable_step(
			parts=parts,
			index=idx,
			step_name=callable_candidate_name,
			callable_attr=callable_candidate,
			method_steps=method_steps,
			current_cls=current_cls,
			cli_to_class=cli_to_class,
			runtime_deferred_mode=runtime_deferred_mode,
		)

	_validate_unique_step_names(method_steps)
	canonical_target = ".".join(parts)
	return _ResolvedInvokeTarget(
		canonical_target=canonical_target,
		parts=parts,
		cli_to_class=cli_to_class,
		method_steps=method_steps,
		terminal_target_info=terminal_target_info,
	)
