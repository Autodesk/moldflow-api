# Moldflow API

[![PyPI version](https://badge.fury.io/py/moldflow.svg)](https://badge.fury.io/py/moldflow)
[![Python versions](https://img.shields.io/pypi/pyversions/moldflow.svg)](https://pypi.org/project/moldflow/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/Autodesk/moldflow-api/workflows/CI/badge.svg)](https://github.com/Autodesk/moldflow-api/actions)

Moldflow API is a Python wrapper library for the Synergy API, designed to simplify interactions with Autodesk Moldflow Synergy. This library provides a clean, pythonic interface to Moldflow's simulation capabilities, making it easier to integrate Moldflow functionality into your Python applications.

## Features

- **Simple API**: Clean, intuitive interface for Moldflow operations
- **Windows-only**: Requires Microsoft Windows with Autodesk Moldflow Synergy
- **Well-documented**: Comprehensive documentation with examples
- **Type hints**: Full type annotation support for better IDE integration
- **Testing**: Comprehensive test suite ensuring reliability

## Prerequisites

Before you begin, ensure you have:
- Windows 10/11
- Python 3.10.x-3.13.x installed
- Autodesk Moldflow Synergy installed (for full functionality)
- pip package manager (usually comes with Python)

## Install
```sh
python -m pip install moldflow
```

## Quick Start

```python
from moldflow import Synergy

# Initialize the API
synergy = Synergy()

# Create a new project and study
project = synergy.project
project.new_study("my_study")

# Get mesh information
diagnosis_mgr = synergy.diagnosis_manager
mesh_summary = diagnosis_mgr.get_mesh_summary(element_only=True)
print(f"Min aspect ratio: {mesh_summary.min_aspect_ratio}")
print(f"Max aspect ratio: {mesh_summary.max_aspect_ratio}")
print(f"Average aspect ratio: {mesh_summary.ave_aspect_ratio}")
```

## Common Use Cases

### Opening and Managing Studies
```python
# Initialize Synergy
synergy = Synergy()

# Create a new project and study
project = synergy.project
project.new_study("my_study")

# Save all open documents
project.save_all()

# Close project (with save prompts)
project.close(prompts=True)
```

### Working with Mesh
```python
# Initialize Synergy
synergy = Synergy()

# Get mesh editor
mesh_editor = synergy.mesh_editor

# Create entity list for selection
entities = mesh_editor.create_entity_list()

# Auto-fix mesh issues
mesh_editor.auto_fix()

# Clean up unused nodes
mesh_editor.purge_nodes()

# Get mesh diagnostics
diagnosis_mgr = synergy.diagnosis_manager
mesh_summary = diagnosis_mgr.get_mesh_summary(
    element_only=False,
    inc_beams=True,
    inc_match=True,
    recalculate=False
)
```

### Material Management
```python
# Initialize Synergy
synergy = Synergy()

# Get material finder
material_finder = synergy.material_finder

# Set material database domain
from moldflow.common import MaterialDatabase, MaterialDatabaseType
material_finder.set_data_domain(
    MaterialDatabase.THERMOPLASTIC,
    MaterialDatabaseType.SYSTEM
)

# Iterate through materials
material = material_finder.get_first_material()
while material:
    print(f"Material: {material}")
    material = material_finder.get_next_material(material)
```

## For Development

### 1. Clone the Repository

```sh
git clone https://github.com/Autodesk/moldflow-api.git
```

### 2. Navigate to the Repository

```sh
cd moldflow-api
```

### 3. Set Up Development Environment

```sh
python -m pip install -r requirements.txt
pre-commit install
```

## Usage

### Building the Package

```sh
python run.py build
```

### Building the Documentation
```sh
python run.py build-docs
```

Options:
- `--skip-build` (`-s`): Skip building before generating docs

The documentation can be accessed locally by opening the [index.html](docs/build/html/index.html) in the [html](docs/build/html/) folder.

### Running the Formatter

```sh
python run.py format
```

Options:
- `--check`: Check the code formatting without making changes

### Running Lint Checks

```sh
python run.py lint
```

Options:
- `--skip-build` (`-s`): Skip building before linting

### Running Tests

```sh
python run.py test
```

| Option             | Alias  | Description                                                            |
|--------------------|:------:|------------------------------------------------------------------------|
| `<tests>...`       | -      | Test files/directories path                                            |
| `--marker`         | `-m`   | Marker [unit, integration, core]                                       |
| `--skip-build`     | `-s`   | Skip building before testing                                           |
| `--keep-files`     | `-k`   | Don't remove the .coverage files after testing [for report generation] |
| `--unit`           | -      | Run Unit Tests                                                         |
| `--core`           | -      | Run Core Functionality Tests                                           |
| `--integration`    | -      | Run Integration Tests                                                  |
| `--quiet`          | `q`    | Simple test output                                                     |

#### Flag Combinations

| Flag Combination                    | Runs Unit | Runs Core | Runs Integration  | Runs Custom Marker |
|-------------------------------------|:---------:|:---------:|:-----------------:|:------------------:|
| Default (no flags)                  | ✅        | ✅       | ❌                | ❌                |
| `--unit`                            | ✅        | ❌       | ❌                | ❌                |
| `--core`                            | ❌        | ✅       | ❌                | ❌                |
| `--integration`                     | ❌        | ❌       | ✅                | ❌                |
| `--unit --core`                     | ✅        | ✅       | ❌                | ❌                |
| `--unit --integration`              | ✅        | ❌       | ✅                | ❌                |
| `--core --integration`              | ❌        | ✅       | ✅                | ❌                |
| `--unit --core --integration`       | ✅        | ✅       | ✅                | ❌                |
| `--all`                             | ✅        | ✅       | ✅                | ❌                |
| `--marker foo`                      | ❌        | ❌       | ❌                | ✅ (`foo`)        |
| `--unit --marker bar`               | ✅        | ❌       | ❌                | ✅ (`bar`)        |
| `--integration --marker baz`        | ❌        | ❌       | ✅                | ✅ (`baz`)        |


### Running specific test files

```sh
python run.py test tests/api/unit_tests/test_unit_material_finder.py
```

## API Documentation

For detailed API documentation, please visit our [online documentation](https://autodesk.github.io/moldflow-api/).

Key modules include:
- `synergy`: Main interface to Moldflow Synergy
- `study_doc`: Study document management
- `mesh_editor`: Mesh manipulation and analysis
- `material_finder`: Material database interactions
- `plot`: Results visualization

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to this project. Here's a quick overview:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python run.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Versioning

We use [Semantic Versioning](https://semver.org/). For available versions, see the [tags on this repository](https://github.com/Autodesk/moldflow-api/tags).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Full documentation available online](https://autodesk.github.io/moldflow-api)
- **Issues**: Report bugs and request features through [GitHub Issues](https://github.com/Autodesk/moldflow-api/issues)
- **Security**: For security issues, please see our [Security Policy](SECURITY.md)
- **Discussions**: Join our [GitHub Discussions](https://github.com/Autodesk/moldflow-api/discussions) for questions and community support

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Acknowledgments

- Special thanks to the Autodesk Moldflow team for their maintenance of this project
