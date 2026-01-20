# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

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

## [27.0.0] - 2026-01-21

### Added
- Python 3.14 support
- New wrapper and documentation for `AnimationExportOptions` (`src/moldflow/animation_export_options.py` and docs/source/components/wrapper/animation_export_options.rst).
- New wrapper and documentation for `ImageExportOptions` (`src/moldflow/image_export_options.py` and docs/source/components/wrapper/image_export_options.rst).
- Added `CADDiagnostic` wrapper and documentation (`src/moldflow/cad_diagnostic.py`, docs/source/components/wrapper/cad_diagnostic.rst).
- Added and updated unit tests covering animation/image export options, CAD diagnostic, import options, mesh editor, plot manager, study document handling, synergy, and viewer (tests/api/unit_tests/* and tests/core/test_helper.py).

### Changed
- API improvements and helper additions across mesh editing, plotting, study documents, Synergy integration, and the viewer (`src/moldflow/mesh_editor.py`, `src/moldflow/plot_manager.py`, `src/moldflow/study_doc.py`, `src/moldflow/synergy.py`, `src/moldflow/viewer.py`).
- Added/updated component enum docs and wrapper docs (docs/source/components/enums/*, docs/source/components/wrapper/*) and updated project readme (docs/source/readme.rst).

### Deprecated
- Deprecated several legacy Viewer functions and MeshGenerator/ImportOptions properties in preparation for Synergy 2027.0.0:
  - `Viewer.save_image_legacy`
  - `Viewer.save_image`
  - `Viewer.save_animation`
  - `ImportOptions.mdl_kernel`
  - `MeshGenerator.automatic_tetra_optimization`
  - `MeshGenerator.element_reduction`
  - `MeshGenerator.use_fallbacks`
  - `MeshGenerator.use_tetras_on_edge`
  - `MeshGenerator.tetra_max_ar`
- Added deprecation warnings and clarified FillHole API redesigns

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [26.0.5] - 2025-12-12

### Added
- N/A

### Changed
- `MeshGenerator.cad_mesh_grading_factor` now accepts `float` values in range 0.0 to 1.0 instead of enum/integer-coded options

### Deprecated
- N/A

### Removed
- `GradingFactor` enum - incorrectly restricted the API to discrete values when the COM API accepts continuous float values from 0.0 to 1.0

### Fixed
- Fixed `MeshGenerator.cad_mesh_grading_factor` to properly accept float/double values matching the COM API signature instead of restricting to enum values

### Security
- N/A

## [26.0.4] - 2025-12-11

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- Fixed `GeomType` enum not being exposed in package `__init__.py` - users can now import it directly with `from moldflow import GeomType`
- Fixed invalid `DUAL_DOMAIN` enum value in `GeomType` - replaced with `FUSION = "Fusion"` to match valid Moldflow API values
- Fixed missing `-> bool` return type annotations for `MeshGenerator.generate()` and `MeshGenerator.save_options()` methods

### Security
- N/A

## [26.0.3] - 2025-10-29

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

[Unreleased]: https://github.com/Autodesk/moldflow-api/compare/v26.0.5...HEAD
[26.0.5]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.5
[26.0.4]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.4
[26.0.3]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.3
[26.0.2]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.2
[26.0.1]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.1
[26.0.0]: https://github.com/Autodesk/moldflow-api/releases/tag/v26.0.0
