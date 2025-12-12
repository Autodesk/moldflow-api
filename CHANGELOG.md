# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- `MeshGenerator.cad_mesh_grading_factor` now accepts `float` values in range 0.0 to 1.0 instead of enum/integer-coded options

### Deprecated
- N/A

### Removed
- `GradingFactor` enum - incorrectly restricted the API to discrete values when the COM API accepts continuous float values from 0.0 to 1.0

### Fixed
- Fixed `GeomType` enum not being exposed in package `__init__.py` - users can now import it directly with `from moldflow import GeomType`
- Fixed `MeshGenerator.cad_mesh_grading_factor` to properly accept float/double values matching the COM API signature instead of restricting to enum values

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
