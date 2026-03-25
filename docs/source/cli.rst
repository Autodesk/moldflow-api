.. _cli:

Command-line interface (CLI)
============================

The Moldflow API package ships with an optional command-line interface that lets you
drive Synergy operations from a shell or automation script.

Installation
------------

To install the library **with** the CLI extras:

.. code-block:: bash

   python -m pip install "moldflow[cli]"

Alternatively, from a clone of this repository you can run:

.. code-block:: bash

   python run.py install

which will build and install the local wheel together with the CLI dependencies.

Basic usage
-----------

Once installed, a top-level ``moldflow`` command is available:

.. code-block:: bash

   moldflow --help
   moldflow list
   moldflow list --json --with-describe --max-results 25
   moldflow describe synergy.open_project

The main commands are:

* ``list`` – discover invokable targets and the next command to run for each one
* ``describe`` – inspect a target's signature, docs, examples, and structured invoke template
* ``invoke`` – run a Moldflow target with named parameters or JSON input

The top-level help guides first-time users through the intended flow:
start with ``list`` to discover targets, use ``describe <target>`` to inspect
usage, then run ``invoke <target> ...``.

The ``list`` output includes readable properties and read/write properties as well
as methods, so property targets are discoverable from the main index. In human
mode it also shows the target kind and a suggested next step. When the CLI knows
how to reach a wrapper through a Synergy property or ``create_*`` factory, the
listed target is emitted in the same Synergy-rooted form that ``invoke`` accepts.

``list --filter`` can be repeated, and repeated filters are additive: a target
is included when it matches any provided filter value.

Invoking simple methods
-----------------------

For simple methods on the ``Synergy`` wrapper you can call them directly with
``name=value`` arguments:

.. code-block:: bash

   moldflow invoke synergy.new_project name="My Project" path="C:/mf/MyProject.mfproj"
   moldflow invoke synergy.import_file file="C:/models/part.iges" show_logs=true

Arguments are parsed as:

* ``true/false/yes/no/on/off`` → booleans
* integer and float literals → numbers
* everything else → strings

Nested objects and non-primitive parameters
-------------------------------------------

Some methods take non-primitive parameters (for example ``ImportOptions`` or
``Vector``). These parameters can be configured using dotted paths:

.. code-block:: bash

   moldflow invoke synergy.import_file \
     file="C:/models/part.iges" \
     import_options.use_mdl=true \
     import_options.units=Millimeter

The CLI will:

* Inspect the type annotation of ``import_options``
* Create an appropriate wrapper instance from the ``Synergy`` object
* Set the specified attributes on that instance before calling the method

Chained targets
---------------

The ``invoke`` command also supports chained targets that navigate through the
object model and call multiple methods in sequence. For example, to find a plot
by name and then query a probe line:

.. code-block:: bash

   moldflow invoke synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line \
     find_plot_by_name.plot_name="My Plot" \
     get_probe_plot_probe_line.index=0 \
     get_probe_plot_probe_line.start_pt.x=0 \
     get_probe_plot_probe_line.start_pt.y=0 \
     get_probe_plot_probe_line.start_pt.z=0 \
     get_probe_plot_probe_line.end_pt.x=10 \
     get_probe_plot_probe_line.end_pt.y=0 \
     get_probe_plot_probe_line.end_pt.z=0

In this example:

* ``synergy`` resolves to the main :class:`moldflow.synergy.Synergy` instance
* ``plot_manager`` resolves to ``Synergy.plot_manager``
* ``find_plot_by_name`` is called first, using arguments prefixed with
  ``find_plot_by_name.``
* The returned :class:`moldflow.plot.Plot` instance is then used to call
  ``get_probe_plot_probe_line``, using arguments prefixed with
  ``get_probe_plot_probe_line.``

For multi-step targets, each method in the chain has its own argument namespace.
The general pattern is::

   method_name.parameter[.attribute] = value

For humans and agents, grouped JSON is often easier to read and generate for
multi-step targets with nested objects. The same chained probe-line call can be
written as:

.. code-block:: bash

   moldflow invoke synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line \
     --params-json '{"find_plot_by_name":{"plot_name":"My Plot"},"get_probe_plot_probe_line":{"index":0,"start_pt":{"x":0,"y":0,"z":0},"end_pt":{"x":10,"y":0,"z":0}}}'

Structured output for `list`
---------------------------

The ``list`` command can emit machine-readable lists via ``--json`` or
``--yaml``. These structured modes are intended for scripting and agent use.
When used, the command outputs an array of objects with the keys:

- ``target``: the CLI dotted target (e.g. ``synergy.new_project``)
- ``owner_class``: the originating class name (e.g. ``Synergy``)
- ``kind``: ``method``, ``property``, or ``settable_property``
- ``suggested_command``: the best first CLI command for a human user
- ``commands``: only the applicable follow-up commands for that target, such as
  ``describe`` or ``invoke``

You can also request:

- ``--with-describe`` to embed the structured ``describe`` payload for each row
- ``--max-results`` to limit the number of rows returned after filtering

Examples:

.. code-block:: bash

   moldflow list --json
   moldflow list --filter NEW_PROJ --yaml

JSON output
-----------

For automation and agent-based tools it is often useful to receive structured
machine-readable output instead of human-oriented strings. The ``invoke``
command therefore supports a ``--json`` flag:

.. code-block:: bash

   moldflow invoke synergy.boundary_conditions.create_ndbc \
     some_param=... \
     --json

When ``--json`` is used, the CLI will attempt to convert common wrapper types
into structured JSON:

* **EntList** and similar objects with ``convert_to_string()`` and ``size``:

  .. code-block:: json

     {
       "type": "EntList",
       "size": 42,
       "string": "1:part:face1, 2:part:face2, ..."
     }

* **Vector**-like objects with ``x``, ``y``, ``z`` attributes:

  .. code-block:: json

     {
       "type": "Vector",
       "x": 0.0,
       "y": 1.0,
       "z": 2.0
     }

* **DoubleArray / IntegerArray / StringArray** (objects with ``to_list`` and
  ``size``):

  .. code-block:: json

     {
       "type": "DoubleArray",
       "size": 5,
       "values": [1.0, 2.0, 3.0, 4.0, 5.0]
     }

* **VectorArray**-like objects with ``size`` and ``x(i)``, ``y(i)``, ``z(i)``:

  .. code-block:: json

     {
       "type": "VectorArray",
       "size": 3,
       "values": [
         {"x": 0.0, "y": 0.0, "z": 0.0},
         {"x": 1.0, "y": 0.0, "z": 0.0},
         {"x": 0.0, "y": 1.0, "z": 0.0}
       ]
     }

* **Property**-like objects with ``id``, ``name`` and ``type``:

  .. code-block:: json

     {
       "type": "Property",
       "id": 123,
       "name": "Viscosity",
       "prop_type": 7
     }

If a result does not match any known pattern, the CLI falls back to returning a
JSON string containing ``repr(obj)``.

JSON input (for invoke)
-----------------------

The ``invoke`` command accepts structured parameter input in addition to the
traditional ``key=value`` syntax. This is useful to avoid complex shell quoting
or to provide nested objects conveniently.

There are three supported JSON input mechanisms (listed in precedence order):

- ``--params-json``: pass a JSON literal as a string on the command line. Example:

  .. code-block:: bash

     moldflow invoke synergy.new_project --params-json '{"name":"test","path":"C:\\\\Projects\\\\MyProject"}'

- ``--params-json-file <path>`` (alias ``-J``): read parameters from a JSON file.
  The CLI is lenient with byte-order-marks (BOM) and will decode UTF-8 files with
  or without a BOM transparently.

  .. code-block:: bash

     moldflow invoke synergy.new_project --params-json-file C:/tmp/params.json

- Single-positional-JSON shorthand: if the invoke command receives exactly one
  positional argument that begins with ``{`` or ``[``, it will be parsed as JSON
  and treated equivalently to ``--params-json``. This is a convenience for
  simple scripts but is less explicit than the ``--params-json`` option.

Notes:

- Only one JSON input source may be provided. Supplying both a JSON literal and a
  JSON file will cause the CLI to error.
- When JSON input is used, positional ``key=value`` arguments are not allowed.
- Top-level JSON payloads must be objects (mappings). Arrays/scalars are rejected.
- For multi-step targets, JSON input should group parameters by step name, for
  example ``{"find_plot_by_name": {"plot_name": "My Plot"}}``. For single-step
  targets, top-level keys map directly to parameters (nested dicts are preserved
  and passed through as values). Single-step targets also accept an optional
  wrapper object keyed by the step name (case-insensitive), e.g.
  ``{"FIND_PLOT_BY_NAME": {"plot_name": "My Plot"}}``.
- For more complex multi-step calls, include one object per step. For example,
  ``synergy.plot_manager.find_plot_by_name.get_probe_plot_probe_line`` can be
  invoked with
  ``{"find_plot_by_name":{"plot_name":"My Plot"},"get_probe_plot_probe_line":{"index":0,"start_pt":{"x":0,"y":0,"z":0},"end_pt":{"x":10,"y":0,"z":0}}}``.
- Methods with positional-only parameters are not supported by CLI named-argument routing.
- Within a step, duplicate argument paths (for example ``param=1`` and ``param=2``)
  or conflicting paths (for example ``param=1`` and ``param.attr=2``) are rejected.
- JSON-derived values are passed through as native Python types (lists, dicts,
  numbers, booleans).
- For wrapper parameters with CLI adapters, prefer the canonical typed JSON fields
  shown by ``describe``. For example, a target such as
  ``synergy.boundary_conditions.create_edge_loads`` can be written as
  ``{"nodes": {"entity_string": "N1,N2"},
  "force": {"xyz": [0.0, 0.0, -100.0]}}``.
  Array-backed wrappers follow the same pattern, for example
  ``{"value": {"values": [1.0, 2.5]}}`` when a target
  has a ``DoubleArray`` parameter named ``value``, or
  ``{"points": {"xyz": [[0, 0, 0], [1, 0, 0]]}}`` for a
  ``VectorArray`` parameter named ``points``.
- Advanced fallback only: ``__type__`` remains available for generic or annotation-free
  JSON payloads, but it is intentionally not part of the normal user-facing flow for
  annotated parameters. If the CLI already has wrapper context, such as a typed parameter
  or an existing nested wrapper-valued property, prefer the untagged wrapper-native form.
- In non-JSON mode, prefer direct parameter assignment for adapter-backed wrappers,
  for example ``nodes=N1,N2`` or ``force=0,0,-100``. The explicit dotted form is mainly
  an escape hatch for tooling or debugging; when needed, use the reflected canonical
  field name such as ``nodes.entity_string=...`` or ``force.xyz=...``. List-backed
  wrappers also accept shorthand such as ``levels=1.0,2.5``, and vector-array wrappers
  accept quoted series such as ``points="0,0,0;1,0,0"``.

JSON output (invoke)
--------------------

The invoke command supports emitting structured JSON results for automation and
LLM orchestration. The following JSON-output options are provided:

- ``--json`` is the canonical option for JSON stdout.
- ``--json-output`` is a legacy compatibility alias for ``--json``.
- ``--json-file-output <path>``: write JSON to the specified file without changing
  stdout mode. Combine it with ``--json`` when you also want JSON on stdout.
- JSON output now uses a stable invoke envelope with:
  - ``schema_version``
  - ``ok``: business-level success indicator (``False`` when target returns ``False``)
  - ``result_type``: Python type name of the raw return value
  - ``result``: serialized return payload
  - ``diagnostics`` (optional): extra failure context

Example:

.. code-block:: bash

   moldflow invoke synergy.cli_return_entlist --json --json-file-output out.json

Planning and automation modes
-----------------------------

The ``invoke`` command includes planning/debugging modes that are useful in CI and
agent workflows:

- ``--dry-run``: parse, validate, and build a resolved call plan without executing invoke steps.
- ``--trace``: emit trace events (JSON) for planning and runtime deferred-step binding.
- ``--batch-file``: execute multiple invoke calls from a JSON array file.
- ``--fail-on-false`` / ``--no-fail-on-false``: control whether a target returning
  ``False`` should produce a non-zero process exit code. Enabled by default.

For terminal use, ``--dry-run`` and ``--batch-file`` render
human-readable summaries by default. Add ``--json`` when you want the structured
JSON contract on stdout. ``--json-file-output`` writes the JSON payload to a
file without changing stdout mode, so it can be combined with the default human
summary or with ``--json``. Human-mode output also confirms where the structured
payload was written.

Dry-run example:

.. code-block:: bash

   moldflow invoke synergy.open_project path="C:/tmp/project.mfproj" --dry-run

For wrapper/object parameters, template output includes more than just a structural
shape. When the CLI recognizes a wrapper family it emits canonical JSON fields,
preferred non-JSON syntax, and concrete examples under ``input_hints``. Typical
examples include output for a target such as
``synergy.boundary_conditions.create_edge_loads``:

.. code-block:: json

   {
     "friendly_json_input": {
       "preferred_field": "entity_string"
     },
     "non_json_input": {
       "preferred_syntax": "nodes=<selection string>",
       "explicit_field_syntax": "nodes.entity_string=<selection string>"
     },
     "examples": {
       "preferred_params_json": {
         "nodes": {
           "entity_string": "N1,N2"
         }
       },
       "preferred_non_json": "nodes=N1,N2",
       "explicit_field_non_json": "nodes.entity_string=N1,N2"
     }
   }

Vector-like and list-backed wrappers expose similar hints, for example ``force=0,0,-100``
for a ``Vector`` parameter or ``values`` for wrappers such as ``DoubleArray``. Vector-array
wrappers expose the same pattern with triplet series such as ``points=0,0,0;1,0,0``.
If shorthand input becomes ambiguous or awkward to escape, switch to
``--params-json``.

Advanced fallback details, including tagged ``__type__`` shapes for generic or
annotation-free payloads, are grouped separately under ``input_hints.advanced_fallbacks``.
For multi-step JSON targets, if a payload fails step routing, group parameters by step
name as shown in the template output, for example
``{"find_plot_by_name": {"plot_name": "My Plot"}}``.

Trace example:

.. code-block:: bash

   moldflow invoke synergy.plot_manager.find_plot_by_name \
     find_plot_by_name.plot_name="My Plot" \
     --trace

Each trace line is a JSON object written to stderr with ``schema_version``,
``sequence``, ``event``, ``target``, and ``payload``. Events that refer to a
concrete invoke step or a property assignment also include ``step`` or
``property``. Explicit ``result`` and ``error`` events are emitted, and batch
runs include ``batch_index`` for per-item correlation.

Batch mode (invoke --batch-file)
--------------------------------

Batch mode reads a JSON array of call objects and executes them in order.

Each batch item supports:

- ``target`` (required, string): invoke target
- ``args`` (optional, list of strings): positional ``key=value`` arguments
- ``params_json`` (optional): JSON object (or JSON string) for structured params
- ``params_json_file`` (optional, string): path to a JSON params file

Example batch file:

.. code-block:: json

   [
     {
       "target": "synergy.open_project",
       "args": ["path=C:/tmp/a.mfproj"]
     },
     {
       "target": "synergy.import_file",
       "params_json": {
         "file": "C:/tmp/part.iges",
         "import_options": {"use_mdl": true}
       }
     },
     {
       "target": "synergy.plot_manager.find_plot_by_name",
       "params_json_file": "C:/tmp/find_plot_args.json"
     }
   ]

Run batch mode:

.. code-block:: bash

   moldflow invoke --batch-file C:/tmp/invoke_batch.json

Batch output is structured JSON:

- ``schema_version``
- ``summary`` with ``total``, ``succeeded``, and ``failed`` counts
- ``batch_results`` (array)
  - ``index``: item index in batch file
  - ``target``: item target (when available)
  - ``request``: normalized request preview for debugging and replay
  - ``ok``: success flag
  - ``result`` (on success) or ``error`` (on failure)
  - ``result_type``: Python type name of the target return value
  - ``diagnostics`` (optional): additional context for business-level failures
  - ``error_type`` (optional): machine-readable failure category such as
    ``batch_item_validation``, ``invoke_validation``, or ``business_failure``

For planning-only batch execution, combine with ``--dry-run``:

.. code-block:: bash

   moldflow invoke --batch-file C:/tmp/invoke_batch.json --dry-run

Any structured invoke mode can be written to file via ``--json-file-output``:

.. code-block:: bash

   moldflow invoke --batch-file C:/tmp/invoke_batch.json --json-file-output C:/tmp/batch_out.json

Add ``--json`` too if you want the same structured payload on stdout.

Structured output for `describe`
--------------------------------

The ``describe`` command can emit structured metadata about a target using the
``--json`` or ``--yaml`` flags. These are useful for automation, editor
integrations, or other tooling that needs to parse signatures and parameter
metadata.

Examples:

.. code-block:: bash

   # JSON output
   moldflow describe plot.get_probe_plot_probe_line --json

   # YAML output (requires PyYAML)
   moldflow describe plot.get_probe_plot_probe_line --yaml

Output shape:

- ``schema_version``: contract version for machine parsing
- ``target``: the dotted target string
- ``signature``: the human-readable signature line
- ``doc``: the docstring or null
- ``params``: a list of parameter metadata objects with ``name``, ``kind``,
  ``annotation``, and ``default`` (canonicalized text/default repr)
- ``params_json_template``: preferred JSON payload shape for ``invoke --params-json``
- ``invoke_examples``: recommended CLI command and preferred JSON examples when the
  target can also be invoked through the CLI

If ``--yaml`` is requested but PyYAML is not installed the CLI will exit with a helpful message indicating the missing dependency.

Template metadata includes per-parameter ``required`` and ``nullable`` fields so
tooling can distinguish required non-null inputs from nullable inputs that can be omitted.

Input validation and escaping
-----------------------------

The CLI performs lightweight input validation for malformed parameter values:

- The CLI rejects null bytes in any string parameter.
- For raw CLI ``key=value`` arguments, shell metacharacters are treated as normal literal characters in values.
- For JSON-derived parameters (``--params-json``/``--params-json-file``), shell metacharacter checks are not applied; only null bytes are rejected.
- The CLI does not perform path normalization or otherwise rewrite values; valid values are passed through unchanged to the target call.

Recommendations:

- Prefer quoting or escaping values that contain spaces:

.. code-block:: bash

   moldflow invoke synergy.open_path path="C:\\path with spaces\\file.txt"

- For complex structured inputs or to avoid shell-escaping issues entirely, use JSON input mechanisms (``--params-json`` or ``--params-json-file``) and consume structured output with ``--json``.
- When writing scripts that call the CLI, always use proper shell quoting (or pass arguments programmatically via subprocess APIs) to avoid accidental interpretation by the shell.

Error messages produced when validation fails indicate the parameter/path and a short reason (for example "contains a null byte", "duplicate argument path", or "unknown parameter").

Safety and side effects
-----------------------

* ``list`` and ``describe`` operate purely via reflection and do **not**
  instantiate Synergy or any COM objects.
* ``invoke`` validates arguments first (including required parameters) using
  introspection before constructing real objects, so invalid calls will fail
  early without opening the Synergy UI.


Testing and mocking
-------------------

The CLI is covered by unit tests under `tests/api/unit_tests/` that mock the Synergy integration so the real application never opens during CI or local runs.

Guidance for writing and running CLI tests:

- Always patch both `moldflow_cli.context.get_synergy` and `moldflow_cli.factories.get_synergy` when a test could instantiate runtime objects or call factory methods.
- When the test exercises the introspection path (e.g., `describe` or `list`) and the runtime invocation path (`invoke`), ensure the class-level shape visible to reflection (the `moldflow.Synergy` class) and the instance returned by `get_synergy()` expose the same callables. In tests this is commonly achieved by temporarily adding the needed method to `moldflow.Synergy` and restoring it after the test.
- Use the project's runner to run tests and coverage:

.. code-block:: bash

   # run CLI tests only
   python run.py test -m cli

   # or run a single test file with pytest
   python -m pytest tests/api/unit_tests -m cli -q

JSON output in tests
--------------------

When asserting `--json` output in tests, prefer parsing with `json.loads()` and asserting on keys/structure rather than exact string matches; the CLI will attempt to produce structured JSON for known wrapper types, but some fallbacks may emit reprs depending on runtime environment.

