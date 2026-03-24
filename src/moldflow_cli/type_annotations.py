# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from types import NoneType
from typing import Annotated, Any, get_args, get_origin
import inspect
import re


_NONE_TYPE_NAMES = {"None", "NoneType", "types.NoneType"}
_MOLDFLOW_QUALIFIED_TYPE = re.compile(r"\bmoldflow\.[A-Za-z_][\w]*\.")


def _is_annotated_origin(origin: Any) -> bool:
	if origin is None:
		return False
	if origin is Annotated:
		return True
	origin_name = getattr(origin, "__name__", "")
	if origin_name == "Annotated":
		return True
	return "Annotated" in str(origin)


def _normalize_annotation_text(annotation_text: str) -> str:
	text = annotation_text.strip().strip("'\"")
	if not text:
		return ""
	return text.replace("typing.", "")


def format_annotation_text(annotation: Any) -> str | None:
	"""Return concise, user-facing annotation text for CLI signatures and payloads."""
	if annotation is inspect._empty:
		return None
	if isinstance(annotation, str):
		text = annotation
	elif isinstance(annotation, type):
		return annotation.__name__
	else:
		text = str(annotation)
	text = _normalize_annotation_text(text)
	if not text:
		return None
	return _MOLDFLOW_QUALIFIED_TYPE.sub("", text)


def format_signature_for_display(
	signature: inspect.Signature | None,
	*,
	empty_as_none: bool = False,
) -> str | None:
	"""Render a receiver-free signature with concise annotation text and no return arrow."""
	if signature is None:
		return None
	params = list(signature.parameters.values())
	if params and params[0].name in {"self", "cls"}:
		signature = signature.replace(parameters=params[1:])
	params = list(signature.parameters.values())
	if not params and empty_as_none:
		return None
	formatted_params: list[str] = []
	last_positional_only = max(
		(index for index, param in enumerate(params) if param.kind is inspect.Parameter.POSITIONAL_ONLY),
		default=-1,
	)
	needs_keyword_only_separator = any(
		param.kind is inspect.Parameter.KEYWORD_ONLY for param in params
	) and not any(param.kind is inspect.Parameter.VAR_POSITIONAL for param in params)
	for index, param in enumerate(params):
		prefix = ""
		if param.kind is inspect.Parameter.VAR_POSITIONAL:
			prefix = "*"
		elif param.kind is inspect.Parameter.VAR_KEYWORD:
			prefix = "**"
		if param.kind is inspect.Parameter.KEYWORD_ONLY and needs_keyword_only_separator:
			formatted_params.append("*")
			needs_keyword_only_separator = False
		formatted = f"{prefix}{param.name}"
		annotation_text = format_annotation_text(param.annotation)
		if annotation_text is not None:
			formatted += f": {annotation_text}"
		if param.default is not inspect._empty:
			formatted += f" = {param.default!r}"
		formatted_params.append(formatted)
		if index == last_positional_only:
			formatted_params.append("/")
	return f"({', '.join(formatted_params)})"


def _leaf_type_name(text: str) -> str:
	return text.strip().strip("'\"").rsplit(".", 1)[-1]


def _split_top_level(text: str, delimiter: str) -> list[str]:
	parts: list[str] = []
	depth = 0
	start = 0
	for idx, char in enumerate(text):
		if char == "[":
			depth += 1
		elif char == "]":
			depth = max(0, depth - 1)
		elif char == delimiter and depth == 0:
			parts.append(text[start:idx].strip())
			start = idx + 1
	parts.append(text[start:].strip())
	return [part for part in parts if part]


def _unwrap_generic(text: str, generic_name: str) -> str | None:
	prefix = f"{generic_name}["
	if text.startswith(prefix) and text.endswith("]"):
		return text[len(prefix) : -1]
	return None


def _collect_non_none_type_names(parts: list[str]) -> list[str]:
	results: list[str] = []
	for part in parts:
		results.extend(extract_non_none_annotation_type_names(part))
	return results


def extract_non_none_annotation_type_names(annotation_text: str) -> list[str]:
	"""
	Extract candidate non-None type names from a string annotation.

	Supports common forward-ref forms such as:
	- "str | None", "str|None"
	- "Optional[str]", "typing.Optional[str]"
	- "Union[A, B, None]", "typing.Union[A, B]"
	"""
	text = _normalize_annotation_text(annotation_text)
	if not text:
		return []

	optional_inner = _unwrap_generic(text, "Optional")
	if optional_inner is not None:
		return extract_non_none_annotation_type_names(optional_inner)

	union_inner = _unwrap_generic(text, "Union")
	if union_inner is not None:
		return _collect_non_none_type_names(_split_top_level(union_inner, ","))

	annotated_inner = _unwrap_generic(text, "Annotated")
	if annotated_inner is not None:
		parts = _split_top_level(annotated_inner, ",")
		if not parts:
			return []
		return extract_non_none_annotation_type_names(parts[0])

	if "|" in text:
		return _collect_non_none_type_names(_split_top_level(text, "|"))

	type_name = _leaf_type_name(text)
	if type_name in _NONE_TYPE_NAMES:
		return []
	return [type_name]


def extract_non_none_type_names(annotation: Any) -> list[str]:
	"""Extract top-level non-None type names from a runtime annotation object."""
	if annotation is inspect._empty:
		return []
	if isinstance(annotation, str):
		return extract_non_none_annotation_type_names(annotation)
	if isinstance(annotation, type):
		if annotation in {NoneType, type(None)}:
			return []
		return [annotation.__name__]

	origin = get_origin(annotation)
	if _is_annotated_origin(origin):
		annotated_args = get_args(annotation)
		if annotated_args:
			return extract_non_none_type_names(annotated_args[0])
		return []

	args = get_args(annotation)
	if args:
		names: list[str] = []
		for arg in args:
			if arg in {NoneType, type(None)}:
				continue
			if isinstance(arg, type):
				names.append(arg.__name__)
				continue
			forward_arg = getattr(arg, "__forward_arg__", None)
			if isinstance(forward_arg, str):
				names.extend(extract_non_none_annotation_type_names(forward_arg))
				continue
			if isinstance(arg, str):
				names.extend(extract_non_none_annotation_type_names(arg))
		return names

	forward_arg = getattr(annotation, "__forward_arg__", None)
	if isinstance(forward_arg, str):
		return extract_non_none_annotation_type_names(forward_arg)

	text = str(annotation).replace("typing.", "")
	if not text:
		return []
	return extract_non_none_annotation_type_names(text)


def annotation_text_allows_str(annotation_text: str) -> bool:
	"""Return True when a string annotation includes str (directly or in a union)."""
	return any(name == "str" for name in extract_non_none_annotation_type_names(annotation_text))
