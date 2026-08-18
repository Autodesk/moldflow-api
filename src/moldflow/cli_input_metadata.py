# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Metadata helpers for declaring CLI-specific wrapper behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar


_CLI_INPUT_ADAPTER_ATTR = "__moldflow_cli_input_adapter__"
_CLI_VISIBILITY_ATTR = "__moldflow_cli_visibility__"
CLI_HIDDEN_REASON_TRANSIENT_WRAPPER_FACTORY = "transient_wrapper_factory"
CLI_VALUE_KIND_SELECTION_TEXT = "selection_text"
CLI_VALUE_KIND_LIST_VALUES = "list_values"
CLI_VALUE_KIND_VECTOR_TRIPLET = "vector_triplet"
CLI_VALUE_KIND_VECTOR_ARRAY_VALUES = "vector_array_values"
_Fn = TypeVar("_Fn", bound=Callable[..., Any])


@dataclass(frozen=True)
class CliInputAdapterMetadata:
    """Describes how a wrapper method should be exposed to the CLI input layer."""

    value_kind: str
    preferred_field: str | None = None
    shorthand_supported: bool = False


@dataclass(frozen=True)
class CliVisibilityMetadata:
    """Describes whether a wrapper member should be hidden from CLI discovery."""

    hidden: bool = True
    reason: str = "hidden"
    message: str | None = None


def cli_input_adapter(
    *, value_kind: str, preferred_field: str | None = None, shorthand_supported: bool = False
) -> Callable[[_Fn], _Fn]:
    """Attach explicit CLI input metadata to a wrapper method."""

    def decorator(func: _Fn) -> _Fn:
        setattr(
            func,
            _CLI_INPUT_ADAPTER_ATTR,
            CliInputAdapterMetadata(
                value_kind=value_kind,
                preferred_field=preferred_field,
                shorthand_supported=shorthand_supported,
            ),
        )
        return func

    return decorator


def cli_hidden(*, reason: str = "hidden", message: str | None = None) -> Callable[[_Fn], _Fn]:
    """Attach metadata marking a wrapper member as intentionally hidden from the CLI."""

    def decorator(func: _Fn) -> _Fn:
        setattr(
            func,
            _CLI_VISIBILITY_ATTR,
            CliVisibilityMetadata(hidden=True, reason=reason, message=message),
        )
        return func

    return decorator


def get_cli_input_adapter_metadata(method: Any) -> CliInputAdapterMetadata | None:
    """Return CLI adapter metadata attached to a wrapper method, if any."""

    return getattr(method, _CLI_INPUT_ADAPTER_ATTR, None)


def get_cli_visibility_metadata(method: Any) -> CliVisibilityMetadata | None:
    """Return CLI visibility metadata attached to a wrapper member, if any."""

    return getattr(method, _CLI_VISIBILITY_ATTR, None)
