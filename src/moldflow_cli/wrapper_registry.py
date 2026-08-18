# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any, Iterable


def _wrapper_snapshot() -> tuple[tuple[str, int], ...]:
	"""Return a stable snapshot of currently exported public wrapper classes."""
	from .introspection import iter_public_classes

	return tuple(sorted((name, id(cls)) for name, cls in iter_public_classes()))


@lru_cache(maxsize=8)
def _public_wrapper_classes_by_name_cached(
	snapshot: tuple[tuple[str, int], ...],
) -> dict[str, type]:
	"""Return public wrapper classes keyed by case-insensitive class name."""
	mf = importlib.import_module("moldflow")

	return {name.lower(): getattr(mf, name) for name, _ in snapshot}


def public_wrapper_classes_by_name() -> dict[str, type]:
	return _public_wrapper_classes_by_name_cached(_wrapper_snapshot())


@lru_cache(maxsize=8)
def _public_wrapper_alias_lookup_cached(
	snapshot: tuple[tuple[str, int], ...],
) -> dict[str, type]:
	"""Return public wrapper classes keyed by class name and snake_case CLI alias."""
	from .factories import camel_to_snake
	mf = importlib.import_module("moldflow")

	lookup = {name.lower(): getattr(mf, name) for name, _ in snapshot}
	for name, _ in snapshot:
		cls = getattr(mf, name)
		name_lower = name.lower()
		lookup.setdefault(name_lower, cls)
		lookup.setdefault(camel_to_snake(name).lower(), cls)
		lookup.setdefault(cls.__name__.lower(), cls)
		lookup.setdefault(camel_to_snake(cls.__name__).lower(), cls)
	return lookup


def public_wrapper_alias_lookup() -> dict[str, type]:
	return _public_wrapper_alias_lookup_cached(_wrapper_snapshot())


@lru_cache(maxsize=8)
def _public_wrapper_name_lookup_cached(
	snapshot: tuple[tuple[str, int], ...],
) -> dict[str, str]:
	"""Return canonical exported wrapper names keyed by supported case-insensitive aliases."""
	from .factories import camel_to_snake
	mf = importlib.import_module("moldflow")

	lookup: dict[str, str] = {}
	for name, _ in snapshot:
		cls = getattr(mf, name)
		lookup.setdefault(name.lower(), name)
		lookup.setdefault(camel_to_snake(name).lower(), name)
		lookup.setdefault(cls.__name__.lower(), name)
		lookup.setdefault(camel_to_snake(cls.__name__).lower(), name)
	return lookup


def public_wrapper_name_lookup() -> dict[str, str]:
	return _public_wrapper_name_lookup_cached(_wrapper_snapshot())


@lru_cache(maxsize=8)
def _public_wrapper_cli_map_cached(snapshot: tuple[tuple[str, int], ...]) -> dict[str, type]:
	"""Return public wrapper classes keyed by snake_case CLI alias."""
	from .factories import camel_to_snake
	mf = importlib.import_module("moldflow")

	return {camel_to_snake(name): getattr(mf, name) for name, _ in snapshot}


def public_wrapper_cli_map() -> dict[str, type]:
	return _public_wrapper_cli_map_cached(_wrapper_snapshot())


def resolve_wrapper_class(wrapper_type: str) -> type | None:
	"""Resolve a wrapper class by case-insensitive class name or CLI alias."""
	if not isinstance(wrapper_type, str) or not wrapper_type.strip():
		return None
	return public_wrapper_alias_lookup().get(wrapper_type.strip().lower())


def resolve_wrapper_name(wrapper_type: str) -> str | None:
	"""Resolve the canonical exported wrapper name for a supported alias."""
	if not isinstance(wrapper_type, str) or not wrapper_type.strip():
		return None
	return public_wrapper_name_lookup().get(wrapper_type.strip().lower())


def resolve_first_wrapper_name(type_names: Iterable[str]) -> str | None:
	"""Resolve the first canonical exported wrapper name from annotation-derived type names."""
	lookup = public_wrapper_name_lookup()
	for type_name in type_names:
		if not isinstance(type_name, str):
			continue
		resolved = lookup.get(type_name.strip().lower())
		if resolved is not None:
			return resolved
	return None


def build_wrapper_input_hints(wrapper_type: str) -> dict[str, Any] | None:
	"""Return wrapper input hints through the shared facade."""
	from .wrapper_input_adapters import build_wrapper_input_adapter_hints

	return build_wrapper_input_adapter_hints(wrapper_type)


def build_target_input_hints(target: Any) -> dict[str, Any] | None:
	"""Return target input hints through the shared facade."""
	from .wrapper_input_adapters import build_target_input_adapter_hints

	return build_target_input_adapter_hints(target)
