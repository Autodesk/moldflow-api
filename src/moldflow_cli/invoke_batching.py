# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Any, Callable, Optional
import json as _json

import typer

from moldflow.i18n import get_text


_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _batch_result_entry(
	*,
	index: int,
	target: str | None,
	request: dict[str, Any] | None,
	ok: bool,
	result: Any = None,
	result_type: str | None = None,
	plan: Any = None,
	diagnostics: list[Any] | None = None,
	error_type: str | None = None,
	error: str | None = None,
) -> dict[str, Any]:
	"""Return a schema-stable batch result entry."""
	return {
		"index": index,
		"target": target,
		"request": request,
		"ok": ok,
		"result": result,
		"result_type": result_type,
		"plan": plan,
		"diagnostics": diagnostics if isinstance(diagnostics, list) else [],
		"error_type": error_type,
		"error": error,
	}


def _validate_batch_mode_inputs(
	*,
	target: Optional[str],
	args: list[str],
	json_input: Optional[str],
	json_file_input: Optional[str],
	translate: Any,
) -> None:
	if target is not None:
		raise typer.BadParameter(translate("Do not pass TARGET when --batch-file is used."))
	if args or json_input is not None or json_file_input is not None:
		raise typer.BadParameter(
			translate("Do not pass positional args/JSON input with --batch-file."))


def _load_batch_payload(batch_file: str) -> list[Any]:
	try:
		with open(batch_file, "r", encoding="utf-8-sig") as input_file:
			batch_payload = _json.load(input_file)
	except (OSError, UnicodeError, _json.JSONDecodeError, RecursionError) as exc:
		raise typer.BadParameter(
			_tr("Cannot read batch file '{path}': {error}", path=batch_file, error=exc)
		) from exc
	if not isinstance(batch_payload, list):
		raise typer.BadParameter(
			_T("Batch file must contain a JSON array of invoke call objects."))
	return batch_payload


def _parse_batch_call(
	index: int,
	item: Any,
) -> tuple[tuple[str, list[str], Optional[str], Optional[str]] | None, dict[str, Any] | None]:
	if not isinstance(item, dict):
		return None, _batch_result_entry(
			index=index,
			target=None,
			request=None,
			ok=False,
			error_type="batch_item_validation",
			error=_tr("Batch item must be a JSON object."),
		)
	allowed_keys = {"target", "args", "params_json", "params_json_file"}
	unknown_keys = sorted([k for k in item.keys() if k not in allowed_keys])
	if unknown_keys:
		return None, _batch_result_entry(
			index=index,
			target=item.get("target") if isinstance(item.get("target"), str) else None,
			request=item,
			ok=False,
			error_type="batch_item_validation",
			error=_tr(
				"Unknown batch item field(s): {fields}.",
				fields=", ".join(unknown_keys),
			),
		)

	call_target = item.get("target")
	if not isinstance(call_target, str) or not call_target.strip():
		return None, _batch_result_entry(
			index=index,
			target=None,
			request=item,
			ok=False,
			error_type="batch_item_validation",
			error=_tr("Batch item requires string field 'target'."),
		)

	call_args = item.get("args", [])
	if not isinstance(call_args, list) or any(not isinstance(v, str) for v in call_args):
		return None, _batch_result_entry(
			index=index,
			target=call_target,
			request=item,
			ok=False,
			error_type="batch_item_validation",
			error=_tr("Batch item field 'args' must be a list of strings."),
		)

	call_json_input = item.get("params_json")
	call_json_file_input = item.get("params_json_file")
	if call_json_input is not None and not isinstance(call_json_input, str):
		call_json_input = _json.dumps(call_json_input)
	if call_json_file_input is not None and not isinstance(call_json_file_input, str):
		return None, _batch_result_entry(
			index=index,
			target=call_target,
			request=item,
			ok=False,
			error_type="batch_item_validation",
			error=_tr("Batch item field 'params_json_file' must be a string path."),
		)

	return (call_target, call_args, call_json_input, call_json_file_input), None


def _batch_request_preview(
	*,
	target: str,
	call_args: list[str],
	call_json_input: Optional[str],
	call_json_file_input: Optional[str],
) -> dict[str, Any]:
	request: dict[str, Any] = {"target": target}
	if call_args:
		request["args"] = call_args
	if call_json_input is not None:
		try:
			request["params_json"] = _json.loads(call_json_input)
		except (_json.JSONDecodeError, TypeError, ValueError, RecursionError):
			request["params_json"] = call_json_input
	if call_json_file_input is not None:
		request["params_json_file"] = call_json_file_input
	return request


def _build_batch_result(
	*,
	index: int,
	target: str,
	request: dict[str, Any],
	call_result: Any,
	dry_run: bool,
	fail_on_false: bool,
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
) -> tuple[dict[str, Any], bool]:
	if dry_run:
		return _batch_result_entry(
			index=index,
			target=target,
			request=request,
			ok=True,
			result=None,
			result_type="dry_run",
			plan=call_result,
			diagnostics=[],
			error_type=None,
			error=None,
		), False
	envelope = build_invoke_envelope(call_result)
	any_error = bool(fail_on_false and envelope["ok"] is False)
	error_type = None
	if envelope["ok"] is False:
		error_type = "business_failure"
	return (
		_batch_result_entry(
			index=index,
			target=target,
			request=request,
			ok=bool(envelope["ok"]),
			result=envelope["result"],
			result_type=envelope["result_type"],
			plan=None,
			diagnostics=envelope.get("diagnostics", []),
			error_type=error_type,
			error=None,
		),
		any_error,
	)


def _build_batch_summary(results: list[dict[str, Any]]) -> dict[str, int]:
	total = len(results)
	succeeded = sum(1 for item in results if item.get("ok") is True)
	failed = total - succeeded
	return {"total": total, "succeeded": succeeded, "failed": failed}


def _run_batch_invoke(
	*,
	batch_payload: list[Any],
	invoke_once: Callable[[str, list[str], Optional[str], Optional[str], Optional[int]], Any],
	dry_run: bool,
	fail_on_false: bool,
	build_invoke_envelope: Callable[[Any], dict[str, Any]],
	emit_batch_trace: Callable[[int, str | None, str, dict[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], bool]:
	results: list[dict[str, Any]] = []
	any_error = False
	for idx, item in enumerate(batch_payload):
		parsed_call, parse_error = _parse_batch_call(idx, item)
		if parse_error is not None:
			if emit_batch_trace is not None:
				emit_batch_trace(idx, parse_error.get("target"), "error", parse_error)
			results.append(parse_error)
			any_error = True
			continue

		call_target, call_args, call_json_input, call_json_file_input = parsed_call
		request = _batch_request_preview(
			target=call_target,
			call_args=call_args,
			call_json_input=call_json_input,
			call_json_file_input=call_json_file_input,
		)
		try:
			call_result = invoke_once(call_target, call_args, call_json_input, call_json_file_input, idx)
			result_entry, result_error = _build_batch_result(
				index=idx,
				target=call_target,
				request=request,
				call_result=call_result,
				dry_run=dry_run,
				fail_on_false=fail_on_false,
				build_invoke_envelope=build_invoke_envelope,
			)
			results.append(result_entry)
			any_error = any_error or result_error
		except Exception as exc:
			error_type = "invoke_validation" if isinstance(exc, typer.BadParameter) else "runtime_error"
			error_entry = _batch_result_entry(
				index=idx,
				target=call_target,
				request=request,
				ok=False,
				result=None,
				result_type=None,
				plan=None,
				diagnostics=[],
				error_type=error_type,
				error=str(exc) or exc.__class__.__name__,
			)
			if emit_batch_trace is not None:
				emit_batch_trace(idx, call_target, "error", error_entry)
			results.append(error_entry)
			any_error = True

	return results, any_error