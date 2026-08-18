# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import inspect
import re
from typing import Any, Sequence

from moldflow.i18n import get_text

from .constants import CLI_KIND_PROPERTY, CLI_KIND_SETTABLE_PROPERTY, CLI_ROOT_SYNERGY
from .factories import camel_to_snake
from .introspection import is_cli_target_hidden, iter_public_classes, resolve_for_introspection
from .invoke_resolution import _resolve_return_class
from .target_resolution import iter_static_members, public_static_attr_lookup
from .wrapper_registry import public_wrapper_classes_by_name


_T = get_text()
_MAX_FILTERED_MATCH_SUMMARY_ROWS = 10


def _matches_list_filter(filter_text: str | None, *candidates: str) -> bool:
	"""Return True when a list row matches the user's filter text."""
	if not filter_text:
		return True
	needle = filter_text.lower()
	lower_candidates = [candidate.lower() for candidate in candidates]
	if not any(token in needle for token in "*?"):
		return any(needle in candidate for candidate in lower_candidates)
	pattern = re.escape(needle).replace(r"\*", ".*").replace(r"\?", ".")
	return any(re.search(pattern, candidate) is not None for candidate in lower_candidates)


def _matches_any_list_filter(filters: Sequence[str] | None, *candidates: str) -> bool:
	"""Return True when a row matches at least one provided filter value."""
	normalized_filters = [filter_text for filter_text in (filters or []) if filter_text]
	if not normalized_filters:
		return True
	return any(_matches_list_filter(filter_text, *candidates) for filter_text in normalized_filters)


def _resolve_list_target(cli_name: str, attr_name: str) -> tuple[str, bool]:
	"""Return a best-effort CLI target and whether it is Synergy-rooted."""
	base_target = f"{cli_name}.{attr_name}"
	if cli_name == CLI_ROOT_SYNERGY:
		return base_target, True

	import moldflow

	synergy_cls = getattr(moldflow, "Synergy", None)
	if not isinstance(synergy_cls, type):
		return base_target, False

	synergy_attrs = public_static_attr_lookup(synergy_cls)
	direct_owner = synergy_attrs.get(cli_name.lower())
	if isinstance(direct_owner, str):
		return f"{CLI_ROOT_SYNERGY}.{direct_owner}.{attr_name}", True

	factory_name = synergy_attrs.get(f"create_{cli_name}".lower())
	if isinstance(factory_name, str):
		return f"{CLI_ROOT_SYNERGY}.{factory_name}.{attr_name}", True

	return base_target, False


def _target_returns_wrapper_property(target: str) -> bool:
	"""Return True when a target resolves to a wrapper-handle property, not a scalar end value."""
	try:
		obj = resolve_for_introspection(target)
	except (AttributeError, ValueError, TypeError):
		return False
	if not isinstance(obj, property) or obj.fget is None:
		return False
	try:
		getter_sig = inspect.signature(obj.fget)
	except (TypeError, ValueError):
		return False
	cli_to_class = public_wrapper_classes_by_name()
	return _resolve_return_class(getter_sig.return_annotation, cli_to_class) is not None


def _list_commands_for_target(*, target: str, kind: str, rooted: bool) -> tuple[dict[str, str], str]:
	"""Return relevant follow-up commands and the best suggested starting command."""
	commands = {"describe": f"describe {target}"}
	if kind == CLI_KIND_PROPERTY:
		if rooted and not _target_returns_wrapper_property(target):
			commands["invoke"] = f"invoke {target}"
		return commands, commands["describe"]
	if kind == CLI_KIND_SETTABLE_PROPERTY:
		if rooted:
			commands["invoke"] = f"invoke {target}"
		return commands, commands["describe"]
	if rooted:
		commands["invoke"] = f"invoke {target}"
	return commands, commands["describe"]


def _is_directly_invokable_list_target(commands: dict[str, str]) -> bool:
	"""Return True when list metadata exposes an actual invoke path for the target."""
	invoke_command = commands.get("invoke")
	return isinstance(invoke_command, str) and bool(invoke_command)


def _prefer_method_rows_over_settable_properties(cls: type) -> bool:
	"""Return True for builder-style wrappers where settable knobs would drown out the action methods."""
	method_count = 0
	settable_property_count = 0
	for attr_name, raw_attr in iter_static_members(cls):
		if attr_name.startswith("_"):
			continue
		if isinstance(raw_attr, property):
			if raw_attr.fget is None or raw_attr.fset is None:
				continue
			settable_property_count += 1
			continue
		attr = raw_attr.__func__ if isinstance(raw_attr, (staticmethod, classmethod)) else raw_attr
		if callable(attr):
			method_count += 1
	return method_count > 0 and method_count <= 2 and settable_property_count >= 3


def _hide_config_only_property_surface(cls: type) -> bool:
	"""Return True for rooted option-bag wrappers that expose only settable properties."""
	method_count = 0
	settable_property_count = 0
	for attr_name, raw_attr in iter_static_members(cls):
		if attr_name.startswith("_"):
			continue
		if isinstance(raw_attr, property):
			if raw_attr.fget is None or raw_attr.fset is None:
				continue
			settable_property_count += 1
			continue
		attr = raw_attr.__func__ if isinstance(raw_attr, (staticmethod, classmethod)) else raw_attr
		if callable(attr):
			method_count += 1
	return method_count == 0 and settable_property_count >= 3


def _try_add_property_row(
	rows: list[dict[str, Any]],
	*,
	target: str,
	name: str,
	kind: str,
	rooted: bool,
	suppress_settable: bool,
	hide_config_only: bool,
) -> None:
	"""Append a property row if it passes filters and is invokable."""
	if rooted and hide_config_only:
		return
	if kind == CLI_KIND_SETTABLE_PROPERTY and rooted and suppress_settable:
		return
	commands, suggested_command = _list_commands_for_target(
		target=target, kind=kind, rooted=rooted
	)
	if not _is_directly_invokable_list_target(commands):
		return
	rows.append({
		"target": target,
		"owner_class": name,
		"kind": kind,
		"suggested_command": suggested_command,
		"commands": commands,
	})


def _try_add_method_row(
	rows: list[dict[str, Any]],
	*,
	target: str,
	name: str,
	rooted: bool,
) -> None:
	"""Append a method row if it passes filters and is invokable."""
	commands, suggested_command = _list_commands_for_target(
		target=target, kind="method", rooted=rooted
	)
	if not _is_directly_invokable_list_target(commands):
		return
	rows.append({
		"target": target,
		"owner_class": name,
		"kind": "method",
		"suggested_command": suggested_command,
		"commands": commands,
	})


def collect_list_rows(filters: Sequence[str] | None) -> list[dict[str, Any]]:
	"""Collect invokable method/property rows for list output."""
	import enum

	rows: list[dict[str, Any]] = []
	for name, cls in sorted(iter_public_classes(), key=lambda t: t[0].lower()):
		if isinstance(cls, type) and issubclass(cls, enum.Enum):
			continue
		cli_name = camel_to_snake(name)
		suppress_settable = _prefer_method_rows_over_settable_properties(cls)
		hide_config_only = _hide_config_only_property_surface(cls)
		for attr_name, raw_attr in iter_static_members(cls):
			if attr_name.startswith("_"):
				continue
			target, rooted = _resolve_list_target(cli_name, attr_name)
			if is_cli_target_hidden(target):
				continue
			if isinstance(raw_attr, property):
				if raw_attr.fget is None or not _matches_any_list_filter(filters, target, name):
					continue
				kind = CLI_KIND_SETTABLE_PROPERTY if raw_attr.fset is not None else CLI_KIND_PROPERTY
				_try_add_property_row(
					rows,
					target=target,
					name=name,
					kind=kind,
					rooted=rooted,
					suppress_settable=suppress_settable,
					hide_config_only=hide_config_only,
				)
				continue
			attr = raw_attr.__func__ if isinstance(raw_attr, (staticmethod, classmethod)) else raw_attr
			if not callable(attr) or not _matches_any_list_filter(filters, target, name):
				continue
			_try_add_method_row(rows, target=target, name=name, rooted=rooted)
	return rows


def has_list_filters(filters: Sequence[str] | None) -> bool:
	"""Return True when the list command was given one or more non-empty filters."""
	return any(filter_text for filter_text in (filters or []))


def human_list_kind(row: dict[str, Any]) -> str:
	"""Return a compact type label for human list tables."""
	if row.get("kind") == CLI_KIND_SETTABLE_PROPERTY:
		return _T("settable")
	return row.get("kind", "")


def human_list_target(row: dict[str, Any]) -> str:
	"""Return a compact display target for human list tables."""
	target = row.get("target", "")
	if target.lower().startswith(f"{CLI_ROOT_SYNERGY}."):
		return target[len(f"{CLI_ROOT_SYNERGY}.") :]
	return target


def render_filtered_list_matches(console: Any, rows: list[dict[str, Any]]) -> None:
	"""Show full target strings when a human filtered list would otherwise crop them."""
	if not rows or len(rows) > _MAX_FILTERED_MATCH_SUMMARY_ROWS:
		return
	console.print(_T("Filtered matches:"), markup=False)
	for row in rows:
		console.print(
			f"- {human_list_target(row)}",
			markup=False,
		)
