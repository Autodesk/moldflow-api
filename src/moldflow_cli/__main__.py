# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

from moldflow.i18n import get_text


def _install_cli_localization() -> None:
	"""Best-effort localization bootstrap for CLI help and errors."""
	try:
		from moldflow.localization import set_language

		set_language()
	except (ImportError, OSError, ValueError, RuntimeError):
		# Keep CLI functional even when locale probing/installation is unavailable.
		return

def _ensure_utf8_stdio() -> None:
	"""Best-effort UTF-8 stdio for predictable CLI automation output."""
	import sys

	for stream_name in ("stdout", "stderr"):
		stream = getattr(sys, stream_name, None)
		if stream is None or not hasattr(stream, "reconfigure"):
			continue
		try:
			stream.reconfigure(encoding="utf-8", errors="replace")
		except (AttributeError, OSError, TypeError, ValueError):
			# Keep CLI functional even if the host stream disallows reconfiguration.
			continue


def main() -> None:
	"""
	Entrypoint for the 'moldflow' console script.
	- Imports optional CLI deps lazily.
	- Provides a helpful message if extras are missing.
	"""
	_ensure_utf8_stdio()
	_install_cli_localization()
	_ = get_text()
	try:
		# Imported only when the CLI is invoked so library-only installs stay lean.
		import importlib
		importlib.import_module("typer")
		importlib.import_module("rich")
	except ModuleNotFoundError as exc:
		missing_name = (getattr(exc, "name", None) or "").split(".")[0]
		missing_cli_dep = missing_name in {"typer", "rich"} or any(
			f"No module named '{dep}'" in str(exc) for dep in ("typer", "rich")
		)
		if missing_cli_dep:
			print(
				_(
					"The Moldflow CLI requires optional dependencies. "
					"Install them with: pip install 'moldflow[cli]'"
				)
			)
			raise SystemExit(1) from exc
		raise

	app = _build_app()
	app()


def _build_app():
	from .commands import build_cli_app
	return build_cli_app()


if __name__ == "__main__":
	main()

