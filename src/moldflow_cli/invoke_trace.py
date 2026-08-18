# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Callable

import typer

from .output_utils import to_json_text


def _trace_result_payload(
	result: Any,
	*,
	mode: str = "invoke",
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
	envelope = build_invoke_envelope(result)
	return {
		"mode": mode,
		"ok": envelope["ok"],
		"result_type": envelope["result_type"],
		"result": envelope["result"],
		"diagnostics": envelope.get("diagnostics", []),
	}


def _trace_error_payload(exc: Exception, *, error_type: str) -> dict[str, Any]:
	return {
		"error_type": error_type,
		"message": str(exc),
		"exception_type": type(exc).__name__,
	}


def _emit_invoke_trace_event(
	*,
	trace_enabled: bool,
	trace_state: dict[str, int],
	call_target: str | None,
	label: str,
	payload: Any,
	serialize_payload: Callable[[Any], Any],
	schema_version: str,
	batch_index: int | None = None,
) -> None:
	if not trace_enabled:
		return
	trace_state["sequence"] += 1
	trace_payload: dict[str, Any] = {
		"schema_version": schema_version,
		"sequence": trace_state["sequence"],
		"event": label,
		"target": call_target or "<batch-item>",
		"payload": serialize_payload(payload),
	}
	if batch_index is not None:
		trace_payload["batch_index"] = batch_index
	if isinstance(payload, dict):
		step_name = payload.get("step")
		property_name = payload.get("property")
		if isinstance(step_name, str) and step_name:
			trace_payload["step"] = step_name
		if isinstance(property_name, str) and property_name:
			trace_payload["property"] = property_name
	typer.echo(to_json_text(trace_payload, context="invoke-trace", default=str), err=True)


def _make_invoke_trace_hook(
	*,
	trace_enabled: bool,
	trace_state: dict[str, int],
	call_target: str,
	emit_invoke_trace_event: Callable[..., None],
	batch_index: int | None = None,
) -> Callable[[str, Any], None] | None:
	if not trace_enabled:
		return None

	def _emit_trace(label: str, payload: Any) -> None:
		emit_invoke_trace_event(
			trace_enabled=trace_enabled,
			trace_state=trace_state,
			call_target=call_target,
			label=label,
			payload=payload,
			batch_index=batch_index,
		)

	return _emit_trace


def _emit_batch_invoke_trace(
	batch_index: int,
	call_target: str | None,
	label: str,
	payload: dict[str, Any],
	*,
	emit_invoke_trace_event: Callable[..., None],
	trace_enabled: bool,
	trace_state: dict[str, int],
) -> None:
	emit_invoke_trace_event(
		trace_enabled=trace_enabled,
		trace_state=trace_state,
		call_target=call_target,
		label=label,
		payload=payload,
		batch_index=batch_index,
	)
