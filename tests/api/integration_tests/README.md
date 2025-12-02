# Integration Tests for moldflow-api

This document provides a complete guide for writing and managing **integration tests** for the `moldflow-api` module.  
It combines the marker-driven test suite conventions with the project fixtures and file-set model types used for real Moldflow Synergy COM interactions.

---

## Table of Contents

1. [Overview](#overview)  
2. [File Sets and Model Types](#file-sets-and-model-types)  
3. [Fixtures](#fixtures)  
4. [Marker-Based Structure & Naming Conventions](#marker-based-structure--naming-conventions)  
5. [Folder Structure](#folder-structure)  
6. [Steps to Add a New Integration Test Suite](#steps-to-add-a-new-integration-test-suite)  
7. [Baseline Data Handling](#baseline-data-handling)  
8. [Generator Functions](#generator-functions)  
9. [Metadata Tracking](#metadata-tracking)  
10. [Running Integration Tests](#running-integration-tests)  
11. [Example Test Suite](#example-test-suite)  
12. [Best Practices](#best-practices)  
13. [Appendix: Quick Checklist](#appendix-quick-checklist)

---

## Overview

Integration tests in this repo exercise **real interactions** with Moldflow Synergy COM objects (via the `Synergy` wrapper). They are written with `pytest` and organized per **marker**. Each marker is the canonical identifier for a test suite and governs:

- test file names
- test class names
- test suite names
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
| `FileSet.SINGLE` | `single_study` | Project containing analyzed `.sdy` file (single study) for general tests (non model type dependent) | mid_doe_model.sdy |
| `FileSet.CAD_MANAGER` | `cad_manager_studies` | Project containing study with CAD for CADManager tests | back_cover_part_study.sdy |

---

## Fixtures

The test framework provides several reusable fixtures to avoid duplication and to manage expensive operations (COM, project open):

| Fixture name | Scope | Purpose |
|--------------|-------|---------|
| `synergy` | `class` | Create & return a real `Synergy` instance. Teardown closes/quits the instance. |
| `project` | `class` | Open a project folder corresponding to the `@pytest.mark.file_set(...)` decorator. Depends on `synergy`. |
| `study_file` | `function` | Yields a model name string for each study file in the project's file set (parameterized). |
| `opened_study` | `function` | Open the study (within the already opened project) and return the study object. |
| `study_with_project` | `function` | Convenience fixture that yields `(study_file, project, opened_study)`. |
| `expected_data` | `class` | Load baseline JSON (`data.json`) for the marker/test class. Uses `@pytest.mark.json_file_name()` if present, otherwise infers from marker name. |
| `expected_values` | `function` | Yield expected values for the current `study_file`; skip the test if values missing. |
| `temp_dir` | `class` | Create a temporary directory for integration testing. |

**Notes:**

- `synergy` and `project` are class-scoped to avoid repeatedly creating COM instances or reopening projects.
- `@pytest.mark.file_set(FileSet.<SET>)` on the class indicates which project folder to open for that entire test class.

---

## Marker-Based Structure & Naming Conventions (Very Important - Follow Strictly)

Everything revolves around the marker. ***Follow these strictly***.

### Marker definition
- A **marker** is a lowercase `snake_case` identifier. Examples: `mesh_summary`, `synergy`, `material_property`.
- Each marker represents a distinct test suite, typically testing a specific API class or functionality.

### Naming rules

| Component | Convention | Example (marker = `mesh_summary`) |
|-----------|------------|----------------------------------|
| Pytest marker | snake_case | `@pytest.mark.mesh_summary` |
| Test suite folder | `test_suite_<marker>/` | `test_suite_mesh_summary/` |
| Test file | `test_suite_<marker>/test_integration_<marker>.py` | `test_suite_mesh_summary/test_integration_mesh_summary.py` |
| Test class | `TestIntegration<Marker>` (PascalCase for Marker) | `TestIntegrationMeshSummary` |
| Fixture (optional) | `<marker>` | `def mesh_summary(...):` |
| Baseline data file | `test_suite_<marker>/data.json` | `test_suite_mesh_summary/data.json` |
| Generator file | `test_suite_<marker>/generate_test_data_<marker>.py` | `test_suite_mesh_summary/generate_test_data_mesh_summary.py` |
| Generator function | `generate_<marker>_data` | `generate_mesh_summary_data` |

### Required class decorators
Each integration test class **must** include:

```python
@pytest.mark.integration
@pytest.mark.<marker>           # e.g. @pytest.mark.mesh_summary
@pytest.mark.file_set(FileSet.<SET>)  # e.g. FileSet.MESHED or FileSet.SINGLE (optional - not required for all tests)
```

Example summary: marker `mesh_summary` → folder `test_suite_mesh_summary/`, test file `test_integration_mesh_summary.py`, class `TestIntegrationMeshSummary`.

## Folder Structure

Each integration test suite is organized in its own dedicated folder following a consistent structure:

```
tests/api/integration_tests/
├── conftest.py                           # Shared fixtures for all integration tests
├── constants.py                          # Shared constants (FileSet enum, paths, etc.)
├── metadata.json                         # Tracks baseline generation metadata
├── data_generation/                      # Data generation utilities
│   ├── generate_data.py                  # Main data generation script
│   ├── generate_data_helper.py           # Helper functions and decorators
│   └── generate_data_logger.py           # Logging utilities
├── common_test_utilities/                # Shared test helper functions
│   └── helpers.py
├── study_files/                          # Project files for testing
│   ├── project_meshed_studies/
│   ├── project_single_study/
│   └── project_cad_manager_studies/
└── test_suite_<marker>/                  # One folder per test suite
    ├── test_integration_<marker>.py      # Test file
    ├── generate_test_data_<marker>.py    # Data generator for this suite
    ├── data.json                         # Baseline data for this suite
    └── constants.py                      # (Optional) Suite-specific constants
```

### Example: MeshSummary Test Suite

```
test_suite_mesh_summary/
├── test_integration_mesh_summary.py      # Contains TestIntegrationMeshSummary class
├── generate_test_data_mesh_summary.py    # Contains generate_mesh_summary_data() function
└── data.json                             # Baseline data with expected values
```

### Key Points

- **One folder per marker**: Each test suite has its own `test_suite_<marker>/` folder
- **Self-contained**: Each folder contains its test file, generator, and baseline data
- **Independent**: Test suites are completely independent of each other

---

## Steps to Add a New Integration Test Suite

Follow these steps to add a new integration suite for marker `my_marker` (replace with your snake_case name):

### 1. Add marker to `pytest.ini`

In `pytest.ini`, under `markers`, add:

```ini
markers =
    my_marker: Description for my_marker tests
```

### 2. Create the test suite folder

Create a new folder following the naming convention:

```
tests/api/integration_tests/test_suite_my_marker/
```

### 3. Create the test file

Inside the test suite folder, create `test_integration_my_marker.py`:

```python
import pytest
from moldflow import Synergy
from tests.api.integration_tests.constants import FileSet

@pytest.mark.integration
@pytest.mark.my_marker
@pytest.mark.file_set(FileSet.MESHED)  # Optional - only if test needs project/study files
class TestIntegrationMyMarker:
    """
    Integration test suite for the MyMarker class.
    """
    
    @pytest.fixture
    def my_marker(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real MyMarker instance for integration testing.
        """
        # Setup code here
        my_marker_instance = synergy.get_my_marker()
        yield my_marker_instance
        # Teardown code here (if needed)
    
    def test_something(self, my_marker, expected_values):
        """Test description."""
        actual = my_marker.some_property
        assert actual == expected_values["some_property"]
```

### 4. Write tests using parametrized fixtures

**For tests requiring study files:**

```python
def test_something(self, study_with_project, expected_values):
    study_file, project, study = study_with_project
    actual = study.do_something()
    assert actual == expected_values["some_key"]
```

**For tests not requiring study files:**

```python
def test_something(self, synergy: Synergy, expected_data: dict):
    actual = synergy.do_something()
    assert actual == expected_data["key"]
```

### 5. Create the generator file (if needed)

Inside the test suite folder, create `generate_test_data_my_marker.py`:

```python
from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet

@generate_json(file_set=FileSet.MESHED)  # Or None if no project needed
def generate_my_marker_data(synergy: Synergy = None):
    """
    Generate data for the MyMarker class.
    Returns a dict with relevant properties.
    """
    my_marker = synergy.get_my_marker()
    
    return {
        "some_property": my_marker.some_property,
        "another_property": my_marker.another_property,
    }

if __name__ == "__main__":
    generate_my_marker_data()
```

### 6. Generate baseline data (if step 5 executed)

Run the data generation command:

```bash
python run.py generate-test-data my_marker
```

This will create `test_suite_my_marker/data.json` with the baseline data.

### 7. (Optional) Add suite-specific constants

If needed, create `constants.py` in the test suite folder:

```python
# Suite-specific constants
MY_CONSTANT = "value"
```

---

## Baseline Data Handling

Baseline data (= expected values) is stored per-marker in JSON files. The standard location:

```
tests/api/integration_tests/test_suite_<marker>/data.json
```

Example:
```
tests/api/integration_tests/test_suite_mesh_summary/data.json
```

### Generating / Updating baseline data

Use the runner script to generate/update baselines:

```bash
python run.py generate-test-data <marker1> <marker2> ...
```

**Behavior:**
- If you pass one or more markers, only those markers' baseline files are generated/updated.
- If you pass **no markers**, **all** available test data baselines are generated/updated.
- Baseline files are **auto-created** the first time you run the generator; it's advised not to hand-create/self-edit them to avoid inconsistencies.
- The generator will write the baseline JSON and also update `metadata.json` for the updated markers (see Metadata section).

**Note:** The generator functions are expected to produce a `dict`.

**Baseline Update Workflow**

When we update the baseline:
1. A new baseline is first written to a temporary file named `test_suite_<marker>/temp_data.json`.
2. Once **all marker generations** are successful, the data is committed to the permanent baseline files (`data.json`).
3. This ensures **atomic updates**, preventing partial baseline overwrites if any generation fails.


---

## Generator Functions

Each test suite has its own generator file located in its test suite folder.

### File Location

```
tests/api/integration_tests/test_suite_<marker>/generate_test_data_<marker>.py
```

### Naming convention

The generator function must follow this pattern:

```python
generate_<marker>_data
```

### The `@generate_json` Decorator

All generator functions must use the `@generate_json` decorator:

**Parameters:**
- `file_set` (FileSet | None): The file set to iterate over (e.g., `FileSet.MESHED`, `FileSet.SINGLE`), or `None` if no project files are needed.
- `synergy_required` (bool): Whether a Synergy instance should be passed to the function. Default: `True`.
  - If `True`: Function receives `synergy=<Synergy instance>` parameter
  - If `False`: Function is called without Synergy (use for static data generation)

### Example: With File Set (Parameterized over study files)

```python
from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet

@generate_json(file_set=FileSet.MESHED)
def generate_mesh_summary_data(synergy: Synergy = None):
    """
    Generate data for the MeshSummary class.
    Returns a dict with relevant properties for the current study.
    """
    mesh_summary = synergy.diagnosis_manager.get_mesh_summary(
        element_only=False, inc_beams=True, inc_match=True, recalculate=True
    )
    
    return {
        "min_aspect_ratio": mesh_summary.min_aspect_ratio,
        "max_aspect_ratio": mesh_summary.max_aspect_ratio,
        # ... more properties
    }

if __name__ == "__main__":
    generate_mesh_summary_data()
```

**Output:** Creates `data.json` with structure:
```json
{
  "dd_model": { "min_aspect_ratio": 1.5, ... },
  "midplane_model": { "min_aspect_ratio": 1.2, ... },
  "3d_model": { "min_aspect_ratio": 1.8, ... }
}
```

### Example: Without File Set (Single data set)

```python
from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json

@generate_json(file_set=None)
def generate_material_property_data(synergy: Synergy = None):
    """
    Generate data for the Material Property class.
    Returns a dict with relevant properties.
    """
    mf = synergy.material_finder
    mf.set_data_domain("GLOBAL", 1)
    mat = mf.get_first_material()
    
    return {
        "material_name": mat.name,
        "material_id": mat.id,
        # ... more properties
    }

if __name__ == "__main__":
    generate_material_property_data()
```

**Output:** Creates `data.json` with structure:
```json
{
  "material_name": "Coolanol 25 : Chevron",
  "material_id": 14,
  ...
}
```

### Example: Static Data (No Synergy)

```python
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json

@generate_json(file_set=None, synergy_required=False)
def generate_custom_property_data():
    """
    Generate static data for custom property tests.
    Returns a dict with expected values.
    """
    return {
        "property_name": "Test Name",
        "property_id": 1,
        # ... more static data
    }

if __name__ == "__main__":
    generate_custom_property_data()
```

### Requirements

- The function must return a Python `dict` containing the baseline content.
- The function should be idempotent: running it repeatedly should produce consistent results (unless intentionally changed).
- Use `synergy_required=False` only when generating static test data that doesn't need Synergy instantiation.
- When `file_set` is specified, the function is called once per study file in that file set, and results are aggregated into a dict keyed by study file name.

---

## The `@pytest.mark.json_file_name()` Decorator (Optional)

By default, the test framework automatically infers the baseline data file from the marker name. However, you can override this behavior using the `@pytest.mark.json_file_name()` decorator.

### When to Use

- When you want to explicitly specify which baseline data file to use
- When the marker name doesn't match the desired data file name
- For clarity in complex test setups

### Usage

```python
@pytest.mark.integration
@pytest.mark.my_marker
@pytest.mark.json_file_name("my_marker")  # Explicitly specify the marker name
class TestIntegrationMyMarker:
    ...
```

**Note:** The decorator takes just the marker name (not including `_data.json` or the folder path). The framework automatically looks for `test_suite_<marker>/data.json`.

### Default Behavior (Without Decorator)

If you don't use `@pytest.mark.json_file_name()`, the framework:
1. Looks at all markers on the test class
2. Excludes standard markers (`integration`, `file_set`, `parametrize`, `json_file_name`)
3. Uses the remaining marker to find the data file
4. If multiple non-standard markers exist, it fails with an error asking you to specify which one to use

### Example

```python
@pytest.mark.integration
@pytest.mark.material_property
@pytest.mark.json_file_name("material_property")  # Optional but explicit
class TestIntegrationMaterialProperty:
    ...
```

This loads: `test_suite_material_property/data.json`

---

## Metadata Tracking

`metadata.json` (located at `tests/api/integration_tests/metadata.json`) keeps a simple audit of baseline updates.

For each marker entry includes:

| Key | Description |
|------------|------|
| `date` | Date of baseline generation/update [In **YYYY-MM-DD** format] |
| `time` | Time of baseline generation/update [In **HH:MM:SS** format] |
| `build_number` | Build Number of Synergy used to generate/update the baseline (e.g., 49.0.x, 49.1.198, etc) |
| `version` | Synergy Version used for baseline update (e.g., 2026, 2027, etc) |

### Example

```json
{
  "mesh_summary": {
    "date": "2025-12-02",
    "time": "01:46:35",
    "build_number": "49.1.198",
    "version": "2026"
  },
  "synergy": {
    "date": "2025-12-02",
    "time": "01:46:35",
    "build_number": "49.1.198",
    "version": "2026"
  }
}
```

When the baseline generator runs for a marker, only that marker's metadata entry is updated (others remain unchanged).

---

## Running Integration Tests

| Task | Command | Example |
|------|---------|---------|
| Run all integration tests | `python run.py test --integration` | |
| Run tests for a specific marker | `python run.py test -m <marker>` | `python run.py test -m mesh_summary` |
| Update / generate baseline data for specific markers | `python run.py generate-test-data <marker1> <marker2> ...` | `python run.py generate-test-data mesh_summary synergy` |
| Update all baselines | `python run.py generate-test-data` (no markers) | |

### Examples

**Run all integration tests:**
```bash
python run.py test --integration
```

**Run tests for MeshSummary class:**
```bash
python run.py test -m mesh_summary
```

**Generate baseline data for MeshSummary:**
```bash
python run.py generate-test-data mesh_summary
```

**Generate baseline data for multiple test suites:**
```bash
python run.py generate-test-data mesh_summary synergy material_property
```

**Regenerate all baseline data:**
```bash
python run.py generate-test-data
```

---

## Example Test Suite

Complete example using marker `mesh_summary`.

### 1. Add marker to `pytest.ini`

```ini
markers =
    mesh_summary: Tests the MeshSummary class
```

### 2. Create test suite folder

```
tests/api/integration_tests/test_suite_mesh_summary/
```

### 3. Create test file: `test_integration_mesh_summary.py`

```python
import pytest
from moldflow import MeshSummary, Synergy
from tests.api.integration_tests.constants import FileSet

@pytest.mark.integration
@pytest.mark.mesh_summary
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationMeshSummary:
    """
    Integration test suite for the MeshSummary class.
    Tests are run against meshed models to ensure mesh summary data is available.
    """

    @pytest.fixture
    def mesh_summary(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real MeshSummary instance for integration testing.
        """
        model_name, _, _ = study_with_project

        # Get diagnosis manager and mesh summary
        diagnosis_manager = synergy.diagnosis_manager
        mesh_summary = diagnosis_manager.get_mesh_summary(
            element_only=False, inc_beams=True, inc_match=True, recalculate=True
        )

        if mesh_summary is None:
            pytest.skip(f"No mesh summary available for {model_name} model")

        return mesh_summary

    def test_aspect_ratio_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        """
        Test aspect ratio related properties.
        """
        min_ar = mesh_summary.min_aspect_ratio
        max_ar = mesh_summary.max_aspect_ratio
        ave_ar = mesh_summary.ave_aspect_ratio

        assert isinstance(min_ar, float)
        assert isinstance(max_ar, float)
        assert isinstance(ave_ar, float)

        assert min_ar <= ave_ar <= max_ar

        assert abs(min_ar - expected_values["min_aspect_ratio"]) < 0.01
        assert abs(max_ar - expected_values["max_aspect_ratio"]) < 0.01
        assert abs(ave_ar - expected_values["ave_aspect_ratio"]) < 0.01
```

### 4. Create generator file: `generate_test_data_mesh_summary.py`

```python
from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet

@generate_json(file_set=FileSet.MESHED)
def generate_mesh_summary_data(synergy: Synergy = None):
    """
    Extract mesh summary data from a study.
    Returns a dict with relevant properties.
    """
    mesh_summary = synergy.diagnosis_manager.get_mesh_summary(
        element_only=False, inc_beams=True, inc_match=True, recalculate=True
    )

    return {
        "min_aspect_ratio": mesh_summary.min_aspect_ratio,
        "max_aspect_ratio": mesh_summary.max_aspect_ratio,
        "ave_aspect_ratio": mesh_summary.ave_aspect_ratio,
        "triangles_count": mesh_summary.triangles_count,
        "nodes_count": mesh_summary.nodes_count,
        # ... more properties
    }

if __name__ == "__main__":
    generate_mesh_summary_data()
```

### 5. Generate baseline data

```bash
python run.py generate-test-data mesh_summary
```

After running you should see:
- Data file created: `tests/api/integration_tests/test_suite_mesh_summary/data.json`
- `metadata.json` updated to include `mesh_summary`

### 6. Resulting folder structure

```
test_suite_mesh_summary/
├── test_integration_mesh_summary.py
├── generate_test_data_mesh_summary.py
└── data.json
```

### 7. Example `data.json` content

```json
{
  "dd_model": {
    "min_aspect_ratio": 1.5,
    "max_aspect_ratio": 45.2,
    "ave_aspect_ratio": 8.3,
    "triangles_count": 12543,
    "nodes_count": 6789
  },
  "midplane_model": {
    "min_aspect_ratio": 1.2,
    "max_aspect_ratio": 38.7,
    "ave_aspect_ratio": 7.1,
    "triangles_count": 8921,
    "nodes_count": 4567
  },
  "3d_model": {
    "min_aspect_ratio": 1.8,
    "max_aspect_ratio": 52.3,
    "ave_aspect_ratio": 9.5,
    "triangles_count": 0,
    "nodes_count": 15234
  }
}
```


---

## Best Practices

- **Markers**: always snake_case (e.g., `mesh_summary`, `synergy`). Keep them descriptive but short, usually matching Synergy API class names.
- **Class names**: use PascalCase for the Marker portion (e.g., `TestIntegrationMeshSummary`).
- **Folder structure**: each test suite gets its own `test_suite_<marker>/` folder containing all related files.
- **Generator functions**: return serializable dictionaries only (no complex objects).
- **Metadata**: let the generator update `metadata.json` — do not edit manually.
- **Scope fixtures appropriately**: use class scope for expensive resources like COM instances.
- **Parameterize where possible**: reduce duplication by using `study_file` and `study_with_project`.
- **Document new markers**: add a short explanation in `pytest.ini`.
- **Baseline data**: never hand-edit `data.json` files — always regenerate using the data generation script.
- **Self-contained suites**: each test suite folder should be independent and contain everything needed for that suite.
- **Consistent naming**: strictly follow the naming conventions for all files and functions.
- **Test organization**: 
  - One test suite per API class or major functionality
  - Multiple test classes in a suite are allowed if they test different aspects
  - Use descriptive test method names that explain what is being tested

---

## Appendix: Quick Checklist

### Step 1: Add Marker to pytest.ini

- [ ] Add marker to `pytest.ini` with description
  ```ini
  markers =
      my_marker: Description for my_marker tests
  ```

### Step 2: Create Test Suite Folder

- [ ] Create folder: `tests/api/integration_tests/test_suite_<marker>/`

### Step 3: Create Test File

- [ ] Create `test_suite_<marker>/test_integration_<marker>.py`
- [ ] Add `TestIntegration<Marker>` class with required decorators:
  - [ ] `@pytest.mark.integration`
  - [ ] `@pytest.mark.<marker>`
  - [ ] `@pytest.mark.file_set(FileSet.<SET>)` (if test needs project/study files)
- [ ] Add fixtures (if needed)
- [ ] Add test methods

### Step 4: Create Generator File (if baseline data needed)

- [ ] Create `test_suite_<marker>/generate_test_data_<marker>.py`
- [ ] Add `generate_<marker>_data()` function with `@generate_json` decorator
- [ ] Implement data collection logic
- [ ] Add `if __name__ == "__main__":` block

### Step 5: Generate Baseline Data

- [ ] Run `python run.py generate-test-data <marker>`
- [ ] Verify `test_suite_<marker>/data.json` was created
- [ ] Verify `metadata.json` was updated

### Step 6: Verify and Test

- [ ] Run tests: `python run.py test -m <marker>`
- [ ] Check that all tests pass
- [ ] Review baseline data files for correctness
- [ ] Confirm the baseline generation command works as expected

### Step 7: Commit Changes

- [ ] `pytest.ini`
- [ ] `test_suite_<marker>/test_integration_<marker>.py`
- [ ] `test_suite_<marker>/generate_test_data_<marker>.py`
- [ ] `test_suite_<marker>/data.json`
- [ ] `test_suite_<marker>/constants.py` (if created)
- [ ] `metadata.json`
- [ ] Push changes to repository

---