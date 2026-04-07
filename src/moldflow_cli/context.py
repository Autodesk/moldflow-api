# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

_logger = logging.getLogger(__name__)

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
	"""Close the active Synergy application and discard the cached instance.

	The next call to :func:`get_synergy` will launch a fresh Synergy session.
	If no instance is cached the call is a no-op.
	"""
	global _synergy_singleton
	if _synergy_singleton is not None:
		try:
			_synergy_singleton.quit(prompt_save=True)
		except Exception:
			# COM may already be disconnected — ignore and drop the reference.
			_logger.debug("Ignoring error while quitting Synergy", exc_info=True)
	_synergy_singleton = None


