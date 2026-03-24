# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

_synergy_singleton = None


def get_synergy() -> "object":
	"""
	Lazily create and cache a moldflow.Synergy instance for the current process.
	We avoid importing moldflow at module import time to keep base installs lean.
	"""
	global _synergy_singleton
	if _synergy_singleton is None:
		import moldflow  # imported lazily

		# Default construction; advanced options could be exposed via CLI flags later.
		_synergy_singleton = moldflow.Synergy()
	return _synergy_singleton


def reset_synergy() -> None:
	global _synergy_singleton
	_synergy_singleton = None


