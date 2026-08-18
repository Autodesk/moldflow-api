from __future__ import annotations

import json as _json
from typing import Any

from .invoke_output import _build_invoke_envelope as _build_invoke_envelope_base


def _serialize_entlist_like(obj: Any) -> Any | None:
	if not (hasattr(obj, "convert_to_string") and hasattr(obj, "size")):
		return None
	try:
		return {"type": obj.__class__.__name__, "size": getattr(obj, "size", None), "string": obj.convert_to_string()}
	except (AttributeError, TypeError, ValueError, IndexError):
		return None


def _serialize_vector_like(obj: Any) -> Any | None:
	if not all(hasattr(obj, attr) for attr in ("x", "y", "z")):
		return None
	try:
		x_attr = getattr(obj, "x")
		y_attr = getattr(obj, "y")
		z_attr = getattr(obj, "z")
		if not callable(x_attr) and not callable(y_attr) and not callable(z_attr):
			return {"type": obj.__class__.__name__, "x": x_attr, "y": y_attr, "z": z_attr}
	except (AttributeError, TypeError, ValueError, IndexError):
		return None
	return None


def _serialize_array_like(obj: Any) -> Any | None:
	if not (hasattr(obj, "to_list") and hasattr(obj, "size")):
		return None
	try:
		values = obj.to_list()  # type: ignore[attr-defined]
		return {"type": obj.__class__.__name__, "size": getattr(obj, "size", None), "values": values}
	except (AttributeError, TypeError, ValueError, IndexError):
		return None


def _serialize_vector_array_like(obj: Any) -> Any | None:
	if not (hasattr(obj, "size") and all(hasattr(obj, m) for m in ("x", "y", "z"))):
		return None
	try:
		coords = []
		for i in range(getattr(obj, "size")):  # type: ignore[attr-defined]
			coords.append({"x": obj.x(i), "y": obj.y(i), "z": obj.z(i)})  # type: ignore[attr-defined]
		return {"type": obj.__class__.__name__, "size": getattr(obj, "size", None), "values": coords}
	except (AttributeError, TypeError, ValueError, IndexError):
		return None


def _serialize_property_like(obj: Any) -> Any | None:
	if not all(hasattr(obj, attr) for attr in ("id", "name", "type")):
		return None
	try:
		return {
			"type": obj.__class__.__name__,
			"id": obj.id,  # type: ignore[attr-defined]
			"name": obj.name,  # type: ignore[attr-defined]
			"prop_type": obj.type,  # type: ignore[attr-defined]
		}
	except (AttributeError, TypeError, ValueError):
		return None


def _serialize_public_attrs(obj: Any, *, depth: int, seen: set[int]) -> Any | None:
	obj_dict = getattr(obj, "__dict__", None)
	if not isinstance(obj_dict, dict) or not obj_dict:
		return None
	public_attrs: dict[str, Any] = {}
	for attr_name in sorted(obj_dict):
		if attr_name.startswith("_"):
			continue
		attr_value = obj_dict[attr_name]
		if callable(attr_value):
			continue
		public_attrs[attr_name] = _to_serializable(attr_value, _depth=depth + 1, _seen=seen)
		if len(public_attrs) >= 25:
			public_attrs["_truncated"] = True
			break
	if public_attrs:
		return {"type": obj.__class__.__name__, "attributes": public_attrs}
	return None


def _to_serializable(
	obj: Any,
	*,
	_depth: int = 0,
	_seen: set[int] | None = None,
) -> Any:
	if _seen is None:
		_seen = set()
	if _depth > 6:
		return {"type": obj.__class__.__name__, "max_depth_exceeded": True, "repr": repr(obj)}
	if isinstance(obj, (str, int, float, bool)) or obj is None:
		return obj
	obj_id = id(obj)
	if obj_id in _seen:
		return {"type": obj.__class__.__name__, "circular_ref": True}
	_seen.add(obj_id)
	try:
		if isinstance(obj, dict):
			return {
				str(k): _to_serializable(v, _depth=_depth + 1, _seen=_seen) for k, v in obj.items()
			}
		if isinstance(obj, (list, tuple)):
			return [_to_serializable(v, _depth=_depth + 1, _seen=_seen) for v in obj]
		if isinstance(obj, set):
			values = [_to_serializable(v, _depth=_depth + 1, _seen=_seen) for v in obj]
			return sorted(values, key=lambda value: _json.dumps(value, sort_keys=True, default=str))
		for serializer in (
			_serialize_entlist_like,
			_serialize_vector_like,
			_serialize_array_like,
			_serialize_vector_array_like,
			_serialize_property_like,
		):
			serialized = serializer(obj)
			if serialized is not None:
				return serialized
		public_attrs = _serialize_public_attrs(obj, depth=_depth, seen=_seen)
		if public_attrs is not None:
			return public_attrs
		return {"type": obj.__class__.__name__, "unserializable_repr": repr(obj)}
	finally:
		_seen.discard(obj_id)


def _apply_schema_version(payload: Any, *, schema_version: str) -> Any:
	if isinstance(payload, dict):
		with_schema = dict(payload)
		with_schema.setdefault("schema_version", schema_version)
		return with_schema
	return payload


def _serialize_trace_payload(payload: Any, *, schema_version: str) -> Any:
	return _apply_schema_version(_to_serializable(payload), schema_version=schema_version)


def _build_invoke_envelope(result: Any, *, schema_version: str) -> dict[str, Any]:
	return _build_invoke_envelope_base(
		result,
		schema_version=schema_version,
		serialize_result=lambda payload: _serialize_trace_payload(payload, schema_version=schema_version),
	)
