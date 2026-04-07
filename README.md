# Moldflow API

[![PyPI version](https://badge.fury.io/py/moldflow.svg)](https://badge.fury.io/py/moldflow)
[![Python versions](https://img.shields.io/pypi/pyversions/moldflow.svg)](https://pypi.org/project/moldflow/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/Autodesk/moldflow-api/workflows/CI/badge.svg)](https://github.com/Autodesk/moldflow-api/actions)

Moldflow API is a Python wrapper library for the Synergy API, designed to simplify interactions with Autodesk Moldflow Synergy. This library provides a clean, pythonic interface to Moldflow's simulation capabilities, making it easier to integrate Moldflow functionality into your Python applications.

## Prerequisites

Before you begin, ensure you have:
- Windows 10/11
- Python 3.10.x - 3.14.x
- Autodesk Moldflow Synergy 2026.0.1 or later

## Install
```sh
python -m pip install moldflow
```

### Install with CLI support

To install the package together with the optional command-line interface:

```sh
python -m pip install "moldflow[cli]"
```

After installation a `moldflow` command will be available on your `PATH`.

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

## Command Line Interface (CLI)

The optional CLI provides a `moldflow` command for driving Synergy operations from a shell.

### Basic usage

```sh
moldflow --help
moldflow list
moldflow list --json --with-describe --max-results 25
moldflow describe synergy.open_project
moldflow describe synergy.new_project synergy.open_project
moldflow list --filter new_proj --filter "*_diag"
```

The top-level help now guides first-time users through the intended workflow:
start with `list` to discover targets, use `describe <target>` to inspect
usage, then run `invoke <target> ...`.

`describe` now shows the preferred and minimal `invoke` forms, plus the
corresponding `--params-json` shapes when the target is invokable, so discovery
and execution use the same examples without leaking Python-only `self`/`cls`
receiver details.

`describe` also accepts multiple targets in one command. In human mode it renders
one block per target; in structured `--json`, `--yaml`, and `--schema` modes it
returns a single object for one target or a list for multiple targets.

`list` now includes readable properties and read/write properties as well as methods,
so property targets are discoverable from the main index too. In human mode it also
surfaces each target's kind and a sensible next step. When the CLI can map a
wrapper back to a Synergy property or `create_*` factory, the listed target is
shown in the same Synergy-rooted form that `invoke` accepts.

`list --filter` can be repeated, and repeated filters are additive: a target is
included when it matches any provided filter value.

In structured mode, `list --json` and `list --yaml` are described as scripting
and agent-oriented outputs. `list --with-describe` embeds the structured
`describe` payload for each listed target, and `--max-results` lets callers cap
the result set after filtering.

### Interactive REPL

Start an interactive shell session with tab completion and built-in session
commands:

```sh
moldflow repl
```

Inside the REPL you can run any CLI command without the `moldflow` prefix:

```
moldflow> list
moldflow> describe synergy.open_project
moldflow> invoke synergy.new_project name="My Project" path="C:/mf/MyProject.mfproj"
```

Built-in session commands:

| Command          | Description                               |
|------------------|-------------------------------------------|
| `help`           | Show available commands                   |
| `help <command>` | Show detailed help for a specific command |
| `clear`          | Clear the screen                          |
| `reset`          | Reset the Synergy session                 |
| `exit` / `quit`  | Exit the REPL (Ctrl+D also works)         |

Tab completion is available for all commands and for invokable targets when
using `describe` or `invoke`. Pass `--debug` to show full tracebacks on errors:

```sh
moldflow repl --debug
```

### Invoking methods

You can invoke methods directly:

```sh
moldflow invoke synergy.new_project name="My Project" path="C:/mf/MyProject.mfproj"
moldflow invoke synergy.import_file file="C:/models/part.iges" show_logs=true
```

Non-primitive parameters (such as `ImportOptions`) can be configured using dotted arguments:

```sh
moldflow invoke synergy.import_file \
  file="C:/models/part.iges" \
  import_options.use_mdl=true \
  import_options.units=Millimeter
```

For more complex operations you can chain calls through the object model, for example:

```sh
moldflow invoke synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line \
  find_plot_by_name.plot_name="My Plot" \
  get_probe_plot_probe_line.index=0 \
  get_probe_plot_probe_line.start_pt.x=0 \
  get_probe_plot_probe_line.start_pt.y=0 \
  get_probe_plot_probe_line.start_pt.z=0 \
  get_probe_plot_probe_line.end_pt.x=10 \
  get_probe_plot_probe_line.end_pt.y=0 \
  get_probe_plot_probe_line.end_pt.z=0
```

For automation or LLM-based tooling, you can request JSON output with `--json`:

```sh
moldflow invoke synergy.boundary_conditions.create_ndbc ... --json
```

You can provide parameters as JSON using `--params-json` or `--params-json-file` (`-J`).
For chained targets, group parameters by step name. For single-step targets, either
top-level parameters or an optional step-name wrapper object are accepted:

```sh
moldflow invoke synergy.plot_manager.find_plot_by_name --params-json \
  '{"find_plot_by_name":{"plot_name":"My Plot"}}'
```

For wrapper parameters, prefer the direct parameter form in non-JSON mode. For a
real public target such as `synergy.boundary_conditions.create_edge_loads`, that means:

```sh
moldflow invoke synergy.boundary_conditions.create_edge_loads \
  nodes=N1,N2 \
  force=0,0,-100
```

The JSON form uses the wrapper-native fields shown by `describe`:

```json
{
  "nodes": {"entity_string": "N1,N2"},
  "force": {"xyz": [0.0, 0.0, -100.0]}
}
```

Array-like wrappers follow the same pattern, for example
`{"value": {"values": [1.0, 2.5]}}` when a target has
a `DoubleArray` parameter named `value`, or `{"points": {"xyz": [[0, 0, 0], [1, 0, 0]]}}`
for a `VectorArray` parameter named `points`.

The direct `param=value` form is the preferred non-JSON syntax. The explicit dotted
form is mostly an escape hatch for tooling or debugging; when you need it, use the
wrapper-native field name shown by `describe`, for example `nodes.entity_string=...`
or `force.xyz=...`. List-backed wrappers now also accept shorthand such as
`levels=1.0,2.5`, and vector-array wrappers accept `points="0,0,0;1,0,0"`.
If shorthand input becomes ambiguous or hard to escape, prefer `--params-json`.

Advanced fallback only: tagged objects with `__type__` are still accepted for generic
or annotation-free JSON payloads, but they are intentionally not part of the normal
customer-facing path for annotated parameters. If the CLI already has wrapper context,
such as a typed parameter or an existing nested wrapper-valued property, the untagged
wrapper-native JSON form is preferred.

Advanced invoke modes:

- `--dry-run`: parse/validate/build a call plan without executing invoke steps.
- `--trace`: emit JSON trace events for planning/runtime deferred binding.
- `--batch-file`: execute multiple invoke calls from a JSON array file.

For terminal users, `describe`, `--dry-run`, and `--batch-file` now render
human-readable summaries by default. Add `--json` when you want the structured
machine contract on stdout. `--json-file-output` writes the JSON contract to a
file without changing stdout mode, so terminal users can keep the human summary
unless they also ask for `--json`. Human-mode output also confirms where the
structured payload was written.

`--trace` emits line-delimited JSON to stderr, one object per event, with
`schema_version`, `sequence`, `event`, `target`, and `payload`, plus `step` or
`property` when relevant.
Result and error events are emitted explicitly, and batch runs add `batch_index`
so trace consumers can correlate per-item activity without inferring it from order.

Batch file shape example:

```json
[
  {"target": "synergy.open_project", "args": ["path=C:/tmp/a.mfproj"]},
  {"target": "synergy.import_file", "params_json": {"file": "C:/tmp/part.iges"}}
]
```

Run:

```sh
moldflow invoke --batch-file C:/tmp/invoke_batch.json
```

To persist machine-readable output, use `--json-file-output`. Add `--json` as well
when you also want the structured payload on stdout.

Batch output now includes a `summary` block and each `batch_results` entry echoes a
normalized `request` payload plus an `error_type` when validation or business logic fails.

`workflow_examples` now carries both fuller `preferred_*` examples and leaner
`minimal_*` examples so tooling and humans can choose between a representative
workflow call and the smallest valid call shape. Human template and dry-run
summaries surface the preferred and minimal `params-json` examples too, not just
the command lines.

Common wrapper types such as `EntList`, `Vector`, `DoubleArray`, `IntegerArray`,
`StringArray`, `VectorArray`, and `Property` are converted to structured JSON
objects describing their contents. Structured object-like JSON responses include
`schema_version` to make automation parsing contracts explicit.

Input validation and escaping
-----------------------------

The CLI performs conservative validation to protect against malformed string input:

- The CLI rejects null bytes and embedded control characters (newlines, tabs, carriage returns) in any string parameter.
- Shell metacharacters are treated as normal literal characters in parameter values.
- For JSON-derived parameters (``--params-json``/``--params-json-file``), shell metacharacter checks are not applied; only null bytes are rejected.
- The CLI does not perform path normalization or otherwise rewrite values; valid values are passed through unchanged to the target call. If a callee requires a normalized path, normalize it before calling the CLI or perform normalization in your script.
- JSON parameter payloads must be objects (mappings) with named arguments.
- Methods that require positional-only parameters are not supported by CLI named-argument routing.
- Duplicate/conflicting argument paths (for example ``param=1`` and ``param.attr=2``) are rejected.

Recommended usage:

- Quote or escape values containing spaces or shell characters:

```sh
moldflow invoke synergy.open_path path="C:\\path with spaces\\file.txt"
```

- For complex values or to avoid shell-escaping issues, prefer JSON input (``--params-json`` or ``--params-json-file``) and programmatic consumption of JSON output.

See the [CLI documentation](https://autodesk.github.io/moldflow-api/cli.html) for more details.

### Safety & testing notes

The CLI performs careful introspection and validation to avoid accidental side effects:

- `list` and `describe` only reflect on the Python API and do **not** start Synergy or any COM objects.
- `invoke` validates required arguments and parses types before constructing wrapper instances, so malformed calls fail fast without launching the Synergy UI.

Running the CLI tests

The project includes a suite of unit tests for the CLI that mock the Synergy integration so the real application is never opened. To run the CLI tests locally:

```sh
python run.py test -m cli
# or directly with pytest:
python -m pytest tests/api/unit_tests -m cli -q
```

Test authors: when writing tests that might touch runtime objects or factories, always patch both:

- `moldflow_cli.context.get_synergy`
- `moldflow_cli.factories.get_synergy`

This ensures neither the introspection nor the factory helpers attempt to talk to COM during tests.

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

> ***Note:  When releasing a new version, update ``switcher.json`` in ``docs/source/_static/`` to include the new tag in the version dropdown for documentation.***

Options:
- `--skip-build` (`-s`): Skip building before generating docs
- `--local` (`-l`): Build documentation locally for a single version (skips multi-version build)

The documentation can be accessed locally by serving the docs/build/html/ folder:
```sh
cd docs/build/html
python -m http.server 8000
```

Then open http://localhost:8000 in your browser. The root automatically redirects to the latest version documentation.

**Versioned Documentation:**
- Each git tag creates a separate documentation version (e.g., `/v26.0.5/`)
- A `/latest/` directory points to the newest version
- Root (`/`) automatically redirects to `/latest/`
- Run `git fetch --tags` before building to ensure all version tags are available

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
