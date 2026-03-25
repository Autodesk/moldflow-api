from __future__ import annotations

import inspect
from typing import Any

import typer

from moldflow.i18n import get_text

from .constants import CLI_ROOT_SYNERGY

from .invoke_binding import _build_step_kwargs
from .target_resolution import resolve_callable_attr_case_insensitive


MethodStep = dict[str, Any]
_T = get_text()


def _tr(message: str, **kwargs: Any) -> str:
	text = _T(message)
	return text.format(**kwargs) if kwargs else text


def _strip_receiver_from_signature(signature: inspect.Signature) -> inspect.Signature:
	"""Remove an implicit receiver parameter from inspectable method signatures."""
	params = list(signature.parameters.values())
	if params and params[0].name in {"self", "cls"}:
		signature = signature.replace(parameters=params[1:])
	return signature


def _signature_and_param_map(callable_obj: Any) -> tuple[Any, dict[str, inspect.Parameter] | None]:
	"""Return (signature, parameter map) for a callable, if inspectable."""
	try:
		sig = _strip_receiver_from_signature(inspect.signature(callable_obj))
		return sig, {p.name: p for p in sig.parameters.values()}
	except (TypeError, ValueError):
		return None, None


def _bind_runtime_step_kwargs(
	*,
	step: MethodStep,
	method_callable: Any,
	kwargs_per_step: dict[str, dict[str, Any]],
	target: str,
	trace_hook: Any | None,
) -> tuple[Any, dict[str, Any]]:
	sig = step["signature"]
	step_kwargs = kwargs_per_step.get(step["name"], {})
	if "__deferred_items__" not in step_kwargs:
		return sig, step_kwargs

	deferred_items = step_kwargs.get("__deferred_items__", [])
	runtime_sig, runtime_param_map = _signature_and_param_map(method_callable)
	runtime_step: MethodStep = {
		"name": step["name"],
		"callable": method_callable,
		"signature": runtime_sig,
		"params": runtime_param_map,
		"class": step.get("class"),
	}
	step_kwargs = _build_step_kwargs(runtime_step, deferred_items, target)
	if trace_hook is not None:
		trace_hook(
			"deferred_runtime_bind",
			{
				"step": step["name"],
				"signature": str(runtime_sig) if runtime_sig is not None else "(...)",
				"params": sorted(list(runtime_param_map.keys()))
				if isinstance(runtime_param_map, dict)
				else [],
			},
		)
	return runtime_sig, step_kwargs


def _execute_method_step_segment(
	*,
	current_obj: Any | None,
	seg: str,
	step: MethodStep,
	kwargs_per_step: dict[str, dict[str, Any]],
	target: str,
	owner_target: str | None,
	trace_hook: Any | None,
) -> Any:
	if current_obj is None:
		owner_label = owner_target or _tr("the owning object")
		raise typer.BadParameter(
			_tr(
				"Cannot invoke method '{segment}' for target '{target}' because "
				"'{owner}' is unavailable in the current session (it resolved to None). "
				"This target only works when that object exists.",
				segment=seg,
				target=target,
				owner=owner_label,
			)
		)

	try:
		_, method_callable = resolve_callable_attr_case_insensitive(current_obj, seg)
	except AttributeError:
		raise typer.BadParameter(
			_tr(
				"Resolved object has no callable attribute '{segment}' when executing target '{target}'",
				segment=seg,
				target=target,
			)
		)

	sig, step_kwargs = _bind_runtime_step_kwargs(
		step=step,
		method_callable=method_callable,
		kwargs_per_step=kwargs_per_step,
		target=target,
		trace_hook=trace_hook,
	)
	if trace_hook is not None:
		trace_hook("invoke_step", {"step": step["name"], "kwargs": step_kwargs})
	try:
		return method_callable(**step_kwargs)
	except TypeError as exc:
		raise typer.BadParameter(
			_tr(
				"Argument error calling {target}{signature}: {error}",
				target=target,
				signature=sig,
				error=exc,
			)
		) from exc


def _resolve_runtime_segment(
	*,
	seg: str,
	current_obj: Any | None,
	cli_to_class: dict[str, type],
	target: str,
) -> Any:
	from .context import get_synergy

	seg_lower = seg.lower()
	if seg_lower in cli_to_class:
		if seg_lower == CLI_ROOT_SYNERGY:
			return get_synergy()
		if current_obj is None:
			return getattr(get_synergy(), seg)
		return getattr(current_obj, seg)

	if current_obj is None:
		raise typer.BadParameter(
			_tr(
				"Cannot resolve attribute '{segment}' without an object instance when resolving target '{target}'",
				segment=seg,
				target=target,
			)
		)
	try:
		return getattr(current_obj, seg)
	except AttributeError as exc:
		raise typer.BadParameter(
			_tr(
				"Cannot resolve attribute '{segment}' on '{class_name}' when executing target '{target}': {error}",
				segment=seg,
				class_name=type(current_obj).__name__,
				target=target,
				error=exc,
			)
		) from exc


def _execute_invoke_chain(
	parts: list[str],
	cli_to_class: dict[str, type],
	method_steps: list[MethodStep],
	kwargs_per_step: dict[str, dict[str, Any]],
	target: str,
	trace_hook: Any | None = None,
) -> Any:
	current_obj: Any | None = None
	method_index = 0
	resolved_parts: list[str] = []
	for seg in parts:
		if method_index < len(method_steps) and seg == method_steps[method_index]["name"]:
			current_obj = _execute_method_step_segment(
				current_obj=current_obj,
				seg=seg,
				step=method_steps[method_index],
				kwargs_per_step=kwargs_per_step,
				target=target,
				owner_target=".".join(resolved_parts) if resolved_parts else None,
				trace_hook=trace_hook,
			)
			resolved_parts.append(seg)
			method_index += 1
			continue
		current_obj = _resolve_runtime_segment(
			seg=seg,
			current_obj=current_obj,
			cli_to_class=cli_to_class,
			target=target,
		)
		resolved_parts.append(seg)

	return current_obj
