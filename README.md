# Moldflow API

[![PyPI version](https://badge.fury.io/py/moldflow.svg)](https://badge.fury.io/py/moldflow)
[![Python versions](https://img.shields.io/pypi/pyversions/moldflow.svg)](https://pypi.org/project/moldflow/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/Autodesk/moldflow-api/workflows/CI/badge.svg)](https://github.com/Autodesk/moldflow-api/actions)

Moldflow API is a Python wrapper library for the Synergy API, designed to simplify interactions with Autodesk Moldflow Synergy. This library provides a clean, pythonic interface to Moldflow's simulation capabilities, making it easier to integrate Moldflow functionality into your Python applications.

## Prerequisites

Before you begin, ensure you have:
- Windows 10/11
- Python 3.10.x - 3.13.x
- Autodesk Moldflow Synergy 2026.0.1 or later

## Install
```sh
python -m pip install moldflow
```

## Quick Start

```python
from moldflow import Synergy

# Initialize the API
synergy = Synergy()

# Example: Get version information
version = synergy.version
print(f"Moldflow Synergy version: {version}")
```

See the [full documentation](https://autodesk.github.io/moldflow-api) for more in-depth examples.

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

The documentation can be accessed locally by opening the index.html in the docs/build/html/ folder.

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

We welcome contributions! Please see our [Contributing Guide](https://github.com/Autodesk/moldflow-api/blob/main/CONTRIBUTING.md) for details on how to contribute to this project. Here's a quick overview:

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

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/Autodesk/moldflow-api/blob/main/LICENSE) file for details.

## Support

- **Documentation**: [Full documentation available online](https://autodesk.github.io/moldflow-api)
- **Issues**: Report bugs and request features through [GitHub Issues](https://github.com/Autodesk/moldflow-api/issues)
- **Security**: For security issues, please see our [Security Policy](https://github.com/Autodesk/moldflow-api/blob/main/SECURITY.md)

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](https://github.com/Autodesk/moldflow-api/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
