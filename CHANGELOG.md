# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Python 3.14 support
- New wrapper and documentation for `AnimationExportOptions` (`src/moldflow/animation_export_options.py` and docs/source/components/wrapper/animation_export_options.rst).
- New wrapper and documentation for `ImageExportOptions` (`src/moldflow/image_export_options.py` and docs/source/components/wrapper/image_export_options.rst).
- Added `CADDiagnostic` wrapper and documentation (`src/moldflow/cad_diagnostic.py`, docs/source/components/wrapper/cad_diagnostic.rst).

### Changed
- `MeshGenerator.cad_mesh_grading_factor` now accepts `float` values in range 0.0 to 1.0 instead of enum/integer-coded options (`src/moldflow/mesh_generator.py`).
- API improvements and helper additions across mesh editing, plotting, study documents, Synergy integration, and the viewer (`src/moldflow/mesh_editor.py`, `src/moldflow/plot_manager.py`, `src/moldflow/study_doc.py`, `src/moldflow/synergy.py`, `src/moldflow/viewer.py`).

### Documentation
- Added/updated component enum docs and wrapper docs (docs/source/components/enums/*, docs/source/components/wrapper/*).
- Updated project readme/documentation index to include the new wrappers and examples (docs/source/readme.rst).

### Removed
- `GradingFactor` enum - incorrectly restricted the API to discrete values when the COM API accepts continuous float values from 0.0 to 1.0

### Fixed
- Exposed `GeomType` enum in package `__init__.py` so users can `from moldflow import GeomType` (`src/moldflow/__init__.py`).
- Fixed `MeshGenerator.cad_mesh_grading_factor` to properly accept float/double values matching the COM API signature instead of restricting to enum values.

### Tests
- Added and updated unit tests covering animation/image export options, CAD diagnostic, import options, mesh editor, plot manager, study document handling, synergy, and viewer (tests/api/unit_tests/* and tests/core/test_helper.py).

### Security
- N/A

## [26.0.3]

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed README links

### Security
- N/A

## [26.0.2] - 2025-10-10

### Added
- Added convenience class for showing message boxes and text input dialogs via Win32
- Add more examples in the documentation

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [26.0.1] - 2025-09-12

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fix return types for `from_list` functions in data classes
- Fix color band range options to 1 to 256

### Security
- N/A

## [26.0.0] - 2025-09-01

### Added
- Initial version aligned with Moldflow Synergy 2026.0.1
- Python 3.10-3.13 compatibility

[Unreleased]: https://github.com/Autodesk/moldflow-api/compare/v26.0.3...HEAD
[26.0.3]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.3
[26.0.2]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.2
[26.0.1]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.1
[26.0.0]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.0
