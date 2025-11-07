# Integration Tests for moldflow-api

This document provides a complete guide for writing and managing **integration tests** for the `moldflow-api` module.  
It combines the marker-driven test suite conventions with the project fixtures and file-set model types used for real Moldflow Synergy COM interactions.

---

## Table of Contents

1. [Overview](#overview)  
2. [File Sets and Model Types](#file-sets-and-model-types)  
3. [Fixtures](#fixtures)  
4. [Marker-Based Structure & Naming Conventions](#marker-based-structure--naming-conventions)  
5. [Steps to Add a New Integration Test Suite](#steps-to-add-a-new-integration-test-suite)  
6. [Baseline Data Handling](#baseline-data-handling)  
7. [Generator Functions (generate_data.py)](#generator-functions-generatedatapy)  
8. [Metadata Tracking](#metadata-tracking)  
9. [Running Integration Tests](#running-integration-tests)  
10. [Example Test Suite](#example-test-suite)  
11. [Best Practices](#best-practices)  
12. [Appendix: Quick Checklist](#appendix-quick-checklist)

---

## Overview

Integration tests in this repo exercise **real interactions** with Moldflow Synergy COM objects (via the `Synergy` wrapper). They are written with `pytest` and organized per **marker**. Each marker is the canonical identifier for a test suite and governs:

- test file names
- test class names
- baseline JSON file names
- generator function names
- pytest markers and metadata entries

**Important:** Markers are always **snake_case**. The marker's human-readable form inside class names uses **PascalCase** (see naming conventions).

---

## File Sets and Model Types

Integration tests are parametrized over *file sets* and *model types* using enums.

### File Sets

`FileSet` (example values used in decorators):

| Enum value | Folder name | Description | Files |
|------------|-------------|-------------|-------|
| `FileSet.MESHED` | `meshed_studies` | Project containing meshed `.sdy` files (meshed studies) | dd_model.sdy <br> midplane_model.sdy <br> 3d_model.sdy |
| `FileSet.SINGLE` | `single_study` | Project containing meshed `.sdy` files (single study) for general tests (non model type dependedent) | mid_doe.sdy |

> Future file sets may include `RAW`, `ANALYZED`, etc.

### Model Types

`ModelType` specifies the study file types inside a project:

| Enum value | Typical filename / key | Model Type |
|------------|------------------------|------------|
| `ModelType.DD` | `dd_model` | Dual Domain |
| `ModelType.MIDPLANE` | `midplane_model` | Midplane |
| `ModelType.THREE_D` | `3d_model` | 3D |

These enums are used by fixtures to parametrize tests over the different models.

---

## Fixtures

The test framework provides several reusable fixtures to avoid duplication and to manage expensive operations (COM, project open):

| Fixture name | Scope | Purpose |
|--------------|-------|---------|
| `synergy` | `class` | Create & return a real `Synergy` instance. Teardown closes/quits the instance. |
| `project` | `class` | Open a project folder corresponding to the `@pytest.mark.file_set(...)` decorator. Depends on `synergy`. |
| `study_file` | `function` | Yields `(ModelType, file_path)` for each model in the project's file set (parameterized). |
| `opened_study` | `function` | Open the study (within the already opened project) and return the study object. |
| `study_with_project` | `function` | Convenience fixture that yields `(ModelType, file_path, project, opened_study)`. |
| `expected_data` | `class` | Load baseline JSON for the marker/test class (from `json_file_name` attribute on the class). |
| `expected_values` | `function` | Yield expected values for the current `ModelType`; skip the test if values missing. |

**Notes:**

- `synergy` and `project` are class-scoped to avoid repeatedly creating COM instances or reopening projects.
- `@pytest.mark.file_set(FileSet.<SET>)` on the class indicates which project folder to open for that entire test class.

---

## Marker-Based Structure & Naming Conventions (Very Important - Follow Strictly)

Everything revolves around the marker. ***Follow these strictly***.

### Marker definition
- A **marker** is a lowercase `snake_case` identifier. Examples: `sample_case`, `thickness_marker`.

### Naming rules

| Component | Convention | Example (marker = `sample_case`) |
|-----------|------------|----------------------------------|
| Pytest marker | snake_case | `@pytest.mark.sample_case` |
| Test file | `test_integration_<marker>.py` | `test_integration_sample_case.py` |
| Test class | `TestIntegration<Marker>` (PascalCase for Marker) | `TestIntegrationSampleCase` |
| Fixture (optional) | `<marker>` | `def sample_case(...):` |
| Baseline data file | `<marker>_data.json` | `sample_case_data.json` |
| Generator function | `generate_<marker>_data` | `generate_sample_case_data` |

### Required class decorators
Each integration test class **must** include:

```python
@pytest.mark.integration
@pytest.mark.<marker>           # e.g. @pytest.mark.sample_case
@pytest.mark.file_set(FileSet.<SET>)  # e.g. FileSet.MESHED or FileSet.SINGLE
```

Example summary: marker `sample_case` → class `TestIntegrationSampleCase`, test file `test_integration_sample_case.py`.

---

## Steps to Add a New Integration Test Suite

Follow these steps to add a new integration suite for marker `my_marker` (replace with your snake_case name):

1. **Add marker to `pytest.ini`**

   In `pytest.ini`, under `markers`, add:

   ```ini
   markers =
       my_marker: Description for my_marker tests
   ```

2. **Create the test file**

   `tests/api/integration_tests/test_integration_my_marker.py`

3. **Add the test class**

   Use PascalCase for the Marker part:

   ```python
   import pytest
   from moldflow.enums import FileSet, ModelType

   @pytest.mark.integration
   @pytest.mark.my_marker
   @pytest.mark.file_set(FileSet.MESHED)
   class TestIntegrationMyMarker:
       ...
   ```

4. **Define fixture (optional)**

   If the test requires setup/teardown, name the fixture same as marker:

   ```python
   @pytest.fixture
   def my_marker():
       # setup
       yield something
       # teardown
   ```

5. **Write tests using parametrized fixtures**

   Typical test signature:

   ```python
   def test_something(self, study_with_project, expected_values):
       model_type, file_path, project, study = study_with_project
       expected = expected_values.get(model_type.name)
       if expected is None:
           pytest.skip("No expected data for %s" % model_type)
       actual = study.do_something()
       assert actual == expected
   ```

6. **(Optional) Add a generator function** if baseline data is required (see next section).

---

## Baseline Data Handling

Baseline data (= expected values) is stored per-marker in JSON files. The standard location:

```
tests/api/integration_tests/data/<marker>_data.json
```

Example:
```
tests/api/integration_tests/data/sample_case_data.json
```

### Generating / Updating baseline data

Use the runner script to generate/update baselines:

```bash
python run.py generate-test-data <marker1> <marker2> ...
```

**Behavior:**
- If you pass one or more markers, only those markers' baseline files are generated/updated.
- If you pass **no markers**, **all** available test data baselines are generated/updated.
- Baseline files are **auto-created** the first time you run the generator; Its advised not to hand-create/self-edit them to avoid inconsistencies.
- The generator will write the baseline JSON and also update `metadata.json` for the updated markers (see Metadata section).

**Note:** The generator functions are expected to produce a `dict`.

**Baseline Update Workflow**

When we update the baseline:
1. A new baseline is first written to a temporary file named `temp_<marker>_data.json`.
2. Once **all marker generations** are successful, the data is committed to the permanent baseline files (`<marker>_data.json`).
3. This ensures **atomic updates**, preventing partial baseline overwrites if any generation fails.


---

## Generator Functions (generate_data.py)

All generator functions live in `generate_data.py`. The test runner locates and calls a generator by convention.

### Naming convention

```text
generate_<marker>_data
```

Example for marker `sample_case`:

```python
@generate_json(file_set=...)
def generate_sample_case_data():
    return {
        "DD": { ... },
        "MIDPLANE": { ... },
        "THREE_D": { ... }
    }
```

### Requirements

- The function must return a Python `dict` containing the baseline content to write to `<marker>_data.json`.
- The function should be idempotent: running it repeatedly should produce consistent results (unless intentionally changed).

---

## Metadata Tracking

`metadata.json` (located under `tests/api/integration_tests/data/`) keeps a simple audit of baseline updates.

For each marker entry includes:

| Key | Description |
|------------|------|
| `date` | Date of baseline generation/update [In **YYYY-MM-DD** format] |
| `time` | Time of baseline generation/update [In **HH:MM:SS** format] |
| `build_number` | Build Number of Synergy used to generate/update the baseline (eg 49.0.x, 49.1.198, etc) |
| `version` | Synergy Version used for baseline update (eg 2026, 2027, etc) |

When the baseline generator runs for a marker, only that marker’s metadata entry is updated (others remain unchanged).

---

## Running Integration Tests

| Task | Command |
|------|---------|
| Run all integration tests | `python run.py test --integration` |
| Run tests for a specific marker | `python run.py test -m <marker>` |
| Update / generate baseline data | `python run.py generate-test-data <marker1> <marker2> ...` |
| Update all baselines | `python run.py generate-test-data` (no markers) |

---

## Example Test Suite

Complete example using marker `sample_case`.

**1) Add marker to `pytest.ini`:**

```ini
markers =
    sample_case: Tests for the sample_case integration suite
```

**2) `tests/api/integration_tests/test_integration_sample_case.py`:**

```python
import pytest
from moldflow.enums import FileSet, ModelType

@pytest.mark.integration
@pytest.mark.sample_case
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationSampleCase:

    @pytest.fixture
    def sample_case(self):
        # optional setup for this marker
        yield
        # optional teardown

    def test_thickness_values(self, study_with_project, expected_values):
        model_type, file_path, project, study = study_with_project
        expected = expected_values.get(model_type.name)
        if expected is None:
            pytest.skip(f"No expected data for {model_type}")
        actual = study.get_thickness_results()
        assert actual == expected
```

**3) `generate_data.py`:**

```python
def generate_sample_case_data():
    # open synergy / project / read values programmatically
    return {
        "DD": {"thickness": 2.3},
        "MIDPLANE": {"thickness": 2.35},
        "THREE_D": {"thickness": 2.31}
    }
```

**4) Generate baseline:**

```bash
python run.py generate-test-data sample_case
```

After running you should see:
- Data file created: `tests/api/integration_tests/test_data/sample_case/sample_case_data.json`
- `metadata.json` updated to include `sample_case`

---

## Best Practices

- **Markers**: always snake_case (e.g., `sample_case`). Keep them descriptive but short [Usually Synergy API class names].
- **Class names**: use PascalCase for the Marker portion (e.g., `TestIntegrationSampleCase`).
- **Generator functions**: return serializable dictionaries only (no complex objects).
- **Metadata**: let the generator update `metadata.json` — do not edit manually.
- **Scope fixtures appropriately**: use class scope for expensive resources like COM instances.
- **Parameterize where possible**: reduce duplication by using `study_file` and `study_with_project`.
- **Document new markers**: add a short explanation in `pytest.ini`.

---

## Appendix: Quick Checklist

- [ ] Add marker to `pytest.ini`
- [ ] Create `test_integration_<marker>.py`
- [ ] Add `TestIntegration<Marker>` class with required decorators
- [ ] Add fixtures/tests
- [ ] Create `generate_<marker>_data` in `generate_data.py` if baseline required
- [ ] Run `python run.py generate-test-data <marker>` to generate baseline
- [ ] Commit `tests/api/integration_tests/test_data/<marker>/<marker>_data.json` and related changes

---
