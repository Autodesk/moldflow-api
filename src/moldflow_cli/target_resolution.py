# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any, Callable, Sequence

import typer

from .constants import CLI_ROOT_MOLDFLOW, CLI_ROOT_SYNERGY

@dataclass(frozen=True)
class ResolvedReadTarget:
	requested_target: str
	canonical_target: str
	resolved_object: Any


@dataclass(frozen=True)
class ResolvedInvokeReadTarget:
	requested_target: str
	canonical_target: str
	parts: list[str]
	cli_to_class: dict[str, type]
	method_steps: list[dict[str, Any]]
	terminal_target_info: dict[str, str] | None
	resolved_object: Any | None


def strip_optional_moldflow_prefix(parts: Sequence[str]) -> tuple[list[str], bool]:
	"""Strip a leading moldflow prefix and report whether it was present."""
	normalized_parts = list(parts)
	had_moldflow_prefix = False
	if normalized_parts and normalized_parts[0].lower() == CLI_ROOT_MOLDFLOW:
		had_moldflow_prefix = True
		normalized_parts = normalized_parts[1:]
	return normalized_parts, had_moldflow_prefix


def validate_public_target_segments(
	parts: Sequence[str],
	*,
	target: str,
	translate: Callable[[str], str],
) -> None:
	"""Reject hidden/private target segments consistently across CLI entrypoints."""
	for segment in parts:
		if segment.startswith("_"):
			raise typer.BadParameter(
				translate("Non-public segment '{segment}' is not allowed in target '{target}'.").format(
					segment=segment,
					target=target,
				)
			)


def split_dotted_path(
	path_text: str,
	*,
	field_name: str,
	translate: Callable[[str], str],
) -> list[str]:
	"""Split dotted identifiers while rejecting empty or invalid segments."""
	if not path_text:
		raise typer.BadParameter(
			translate("Invalid {field_name}: value cannot be empty.").format(
				field_name=field_name
			)
		)
	path_text = path_text.strip()
	segments = [seg.strip() for seg in path_text.split(".")]
	if any(seg == "" for seg in segments):
		raise typer.BadParameter(
			translate("Invalid {field_name} '{path_text}': empty path segment is not allowed.").format(
				field_name=field_name,
				path_text=path_text,
			)
		)
	for segment in segments:
		if not segment.isidentifier():
			raise typer.BadParameter(
				translate(
					"Invalid {field_name} '{path_text}': segment '{segment}' must be a valid identifier."
				).format(
					field_name=field_name,
					path_text=path_text,
					segment=segment,
				)
			)
	return segments


def public_static_attr_lookup(cls: type) -> dict[str, str]:
	"""Build a case-insensitive lookup of a class's public static attributes."""
	lookup: dict[str, str] = {}
	for attr_name, _ in iter_static_members(cls):
		if attr_name.startswith("_"):
			continue
		lookup.setdefault(attr_name.lower(), attr_name)
	return lookup


def iter_static_members(obj: Any) -> list[tuple[str, Any]]:
	"""Return static members without invoking descriptors, including on Python 3.10."""
	try:
		return list(inspect.getmembers_static(obj))
	except AttributeError:
		pass

	members: list[tuple[str, Any]] = []
	for name in dir(obj):
		try:
			members.append((name, inspect.getattr_static(obj, name)))
		except AttributeError:
			continue
	return members


def canonicalize_describe_target_parts(
	target_parts: Sequence[str],
	*,
	target: str,
	translate: Callable[[str], str],
) -> str:
	"""Canonicalize describe targets while preserving bare public class targets."""
	parts, _had_moldflow_prefix = strip_optional_moldflow_prefix(target_parts)
	if not parts:
		return ""
	validate_public_target_segments(parts, target=target, translate=translate)
	if parts[0].lower() == CLI_ROOT_SYNERGY:
		return ".".join(parts)

	import moldflow

	synergy_cls = getattr(moldflow, "Synergy", None)
	if not isinstance(synergy_cls, type):
		return ".".join(parts)
	synergy_attrs = public_static_attr_lookup(synergy_cls)
	direct_attr = synergy_attrs.get(parts[0].lower())
	if isinstance(direct_attr, str):
		return ".".join(["synergy", direct_attr, *parts[1:]])
	return ".".join(parts)


def canonicalize_invoke_target(
	target: str,
	*,
	translate: Callable[[str], str],
) -> str:
	"""Canonicalize invoke targets, auto-prefixing bare targets to synergy.*."""
	parts = split_dotted_path(target, field_name="target", translate=translate)
	parts, had_moldflow_prefix = strip_optional_moldflow_prefix(parts)
	if not parts:
		raise typer.BadParameter(translate("Target must include at least one segment"))
	if parts[0].lower() != CLI_ROOT_SYNERGY:
		if had_moldflow_prefix:
			raise typer.BadParameter(
				translate(
					"Target must start with 'synergy' after the optional 'moldflow.' prefix. "
					"Bare targets such as 'open_project' are accepted and are interpreted as "
					"'synergy.open_project'."
				)
			)
		parts = [CLI_ROOT_SYNERGY, *parts]
	canonical_target = ".".join(parts)
	validate_public_target_segments(parts, target=canonical_target, translate=translate)
	return canonical_target


def resolve_attr_name_case_insensitive(
	current: Any,
	attr_name: str,
	*,
	static_lookup: bool = False,
) -> str | None:
	"""Resolve an attribute name exactly or case-insensitively."""
	if static_lookup:
		try:
			inspect.getattr_static(current, attr_name)
			return attr_name
		except AttributeError:
			pass
	else:
		if hasattr(current, attr_name):
			return attr_name
	attr_lower = attr_name.lower()
	return next((name for name in dir(current) if name.lower() == attr_lower), None)


def resolve_callable_attr_case_insensitive(obj: Any, name: str) -> tuple[str, Any]:
	"""Resolve a callable attribute by exact or case-insensitive name."""
	attr = getattr(obj, name, None)
	if callable(attr):
		return name, attr
	name_lower = name.lower()
	for candidate in dir(obj):
		if candidate.lower() != name_lower:
			continue
		resolved = getattr(obj, candidate, None)
		if callable(resolved):
			return candidate, resolved
	raise AttributeError(name)


def resolve_target_for_introspection(
	target: str,
	*,
	require_visible: bool = False,
) -> Any:
	"""Resolve a target for read-only CLI introspection with consistent CLI errors."""
	from .introspection import HiddenCliTargetError, resolve_for_introspection, validate_cli_target_visible

	try:
		if require_visible:
			validate_cli_target_visible(target)
		return resolve_for_introspection(target)
	except (AttributeError, HiddenCliTargetError, ValueError) as exc:
		raise typer.BadParameter(str(exc)) from exc


def resolve_describe_read_target(
	target: str,
	*,
	translate: Callable[[str], str],
) -> ResolvedReadTarget:
	"""Resolve a describe target into its canonical target and introspected object."""
	target_parts = split_dotted_path(target, field_name="target", translate=translate)
	canonical_target = canonicalize_describe_target_parts(
		target_parts,
		target=target,
		translate=translate,
	)
	resolved_object = resolve_target_for_introspection(canonical_target, require_visible=True)
	return ResolvedReadTarget(
		requested_target=target,
		canonical_target=canonical_target,
		resolved_object=resolved_object,
	)
