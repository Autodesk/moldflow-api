# Integration Tests for moldflow-api

This document provides a complete guide for writing and managing **integration tests** for the `moldflow-api` module.  
It combines the marker-driven test suite conventions with the project fixtures and file-set model types used for real Moldflow Synergy COM interactions.

---

## Table of Contents

1. [Overview](#overview)  
2. [File Sets and Model Types](#file-sets-and-model-types)  
3. [Fixtures](#fixtures)  
4. [Marker-Based Structure & Naming Conventions](#marker-based-structure--naming-conventions)  
   - [Parent and Child Markers](#parent-and-child-markers)  
   - [Test Execution with Parent-Child Markers](#test-execution-with-parent-child-markers)  
5. [Steps to Add a New Integration Test Suite](#steps-to-add-a-new-integration-test-suite)  
   - [Option A: Simple Marker](#option-a-simple-marker-single-test-scenario)  
   - [Option B: Parent-Child Markers](#option-b-parent-child-markers-multiple-test-scenarios)  
6. [Baseline Data Handling](#baseline-data-handling)  
7. [Generator Functions (generate_data.py)](#generator-functions-generatedatapy)  
8. [Child Markers Configuration](#child-markers-configuration)  
9. [Metadata Tracking](#metadata-tracking)  
10. [Running Integration Tests](#running-integration-tests)  
11. [Example Test Suite](#example-test-suite)  
    - [Example 1: Simple Marker](#example-1-simple-marker)  
    - [Example 2: Parent-Child Markers](#example-2-parent-child-markers)  
12. [Best Practices](#best-practices)  
13. [Appendix: Quick Checklist](#appendix-quick-checklist)  
    - [Step 1: Decide on Test Structure](#step-1-decide-on-test-structure)  
    - [Step 2A: For Simple Marker](#step-2a-for-simple-marker-single-test-scenario)  
    - [Step 2B: For Parent-Child Markers](#step-2b-for-parent-child-markers-multiple-test-scenarios)  
    - [Step 3: Verify and Test](#step-3-verify-and-test)

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
| `study_file` | `function` | Yields a model name string for each study file in the project's file set (parameterized). |
| `opened_study` | `function` | Open the study (within the already opened project) and return the study object. |
| `study_with_project` | `function` | Convenience fixture that yields `(study_file, project, opened_study)`. |
| `expected_data` | `class` | Load baseline JSON for the marker/test class. Uses `@pytest.mark.json_file_name()` if present, otherwise infers from marker name. |
| `expected_values` | `function` | Yield expected values for the current `study_file`; skip the test if values missing. |

**Notes:**

- `synergy` and `project` are class-scoped to avoid repeatedly creating COM instances or reopening projects.
- `@pytest.mark.file_set(FileSet.<SET>)` on the class indicates which project folder to open for that entire test class.

---

## Marker-Based Structure & Naming Conventions (Very Important - Follow Strictly)

Everything revolves around the marker. ***Follow these strictly***.

### Marker definition
- A **marker** is a lowercase `snake_case` identifier. Examples: `sample_case`, `thickness_marker`.
- Markers can be **parent markers** or **child markers** (see [Parent and Child Markers](#parent-and-child-markers)).

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
@pytest.mark.file_set(FileSet.<SET>)  # e.g. FileSet.MESHED or FileSet.SINGLE (optional - not required for all tests)
```

Example summary: marker `sample_case` → class `TestIntegrationSampleCase`, test file `test_integration_sample_case.py`.

### Parent and Child Markers

For more complex test suites, you can organize tests using **parent and child markers**. This is useful when testing a single API class with multiple test scenarios that are independent of each other and require different baseline data files.

**Example:** Testing the `Property` class:
- Parent marker: `prop` (represents the Property class)
- Child markers: `material_property`, `custom_property` (represent different test scenarios)

#### Setting up Parent-Child Relationships

1. **Define markers in `pytest.ini`:**

```ini
markers =
    prop: Tests the Property class

    material_property: Tests the pre-existing materials for Property class
    custom_property: Tests a new custom property for Property class
```

2. **Add mapping to `child_markers.json`** (in the repository root):

```json
{
    "prop": ["material_property", "custom_property"]
}
```

3. **Apply both markers to test classes:**

```python
@pytest.mark.integration
@pytest.mark.prop                # Parent marker
@pytest.mark.material_property   # Child marker
@pytest.mark.json_file_name("material_property")
class TestIntegrationMaterialProperty:
    ...

@pytest.mark.integration
@pytest.mark.prop                # Parent marker
@pytest.mark.custom_property     # Child marker
@pytest.mark.file_set(FileSet.SINGLE)
@pytest.mark.json_file_name("custom_property")
class TestIntegrationCustomProperty:
    ...
```

#### Test Execution with Parent-Child Markers

Understanding which tests run with which marker is crucial:

| Command | Tests Executed | Explanation |
|---------|---------------|-------------|
| `python run.py test -m prop` | **Both** `TestIntegrationMaterialProperty` **and** `TestIntegrationCustomProperty` | Running with parent marker executes **all** test classes that have the parent marker (both child test classes) |
| `python run.py test -m material_property` | **Only** `TestIntegrationMaterialProperty` | Running with child marker executes **only** the test class with that specific child marker |
| `python run.py test -m custom_property` | **Only** `TestIntegrationCustomProperty` | Running with child marker executes **only** the test class with that specific child marker |

**Key Points:**
- Both test classes have the **parent marker** (`prop`), so running `-m prop` runs **all** tests for that API class
- Each test class also has its **own child marker**, allowing you to run tests for specific scenarios independently
- This provides flexibility: run all Property tests together with `-m prop`, or run only material property tests with `-m material_property`

#### The `@pytest.mark.json_file_name()` Decorator

When using child markers, you **must** specify which baseline data file to use with the `@pytest.mark.json_file_name()` decorator:

***Note:** The suffix and file extension `_data.json` will be automatically added, please don't include in the argument.*

```python
@pytest.mark.json_file_name("material_property")
```

This tells the test framework to load `material_property_data.json` instead of inferring the filename from marker names.

**Without this decorator:** The framework would attempt to load `prop_data.json` (using the first non-standard marker found).

**With this decorator:** The framework explicitly loads `material_property_data.json` or `custom_property_data.json`.

#### File Organization with Parent-Child Markers

For parent marker `prop` with child markers `material_property` and `custom_property`:

```
tests/api/integration_tests/
├── test_integration_property.py          # Single file for both test classes
├── data/
│   ├── material_property_data.json       # Baseline for material_property
│   └── custom_property_data.json         # Baseline for custom_property
```

**Important:** 
- Both test classes can live in the **same test file** (`test_integration_property.py`)
- Each child marker has its **own baseline data file**
- The `child_markers.json` file is used by the data generation script to handle parent-child relationships

---

## Steps to Add a New Integration Test Suite

### Option A: Simple Marker (Single Test Scenario)

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
   from tests.api.integration_tests.constants import FileSet

   @pytest.mark.integration
   @pytest.mark.my_marker
   @pytest.mark.file_set(FileSet.MESHED)  # Optional - only if test needs project/study files
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

   Typical test signature (for tests requiring study files):

   ```python
   def test_something(self, study_with_project, expected_values):
       study_file, project, study = study_with_project
       expected = expected_values.get(study_file)
       if expected is None:
           pytest.skip("No expected data for %s" % study_file)
       actual = study.do_something()
       assert actual == expected
   ```

   For tests not requiring study files:

   ```python
   def test_something(self, synergy: Synergy, expected_data: dict):
       actual = synergy.do_something()
       assert actual == expected_data["key"]
   ```

6. **(Optional) Add a generator function** if baseline data is required (see next section).

### Option B: Parent-Child Markers (Multiple Test Scenarios)

Use this approach when testing a single API class with multiple distinct test scenarios requiring separate baseline data files.

1. **Add all markers to `pytest.ini`**

   Add the parent marker with other API class markers, and child markers at the bottom (after a blank line):

   ```ini
   markers =
       # ... other API class markers ...
       my_marker: Tests the MyClass API
       # ... other API class markers ...
       
       my_marker_scenario_a: Tests scenario A for MyClass
       my_marker_scenario_b: Tests scenario B for MyClass
   ```

2. **Add parent-child mapping to `child_markers.json`** (in repository root)

   ```json
   {
       "my_marker": ["my_marker_scenario_a", "my_marker_scenario_b"]
   }
   ```

3. **Create the test file**

   `tests/api/integration_tests/test_integration_my_marker.py`

4. **Add test classes with both parent and child markers**

   ```python
   import pytest
   from tests.api.integration_tests.constants import FileSet

   @pytest.mark.integration
   @pytest.mark.my_marker              # Parent marker
   @pytest.mark.my_marker_scenario_a   # Child marker
   @pytest.mark.json_file_name("my_marker_scenario_a")  # Required!
   class TestIntegrationMyMarkerScenarioA:
       ...

   @pytest.mark.integration
   @pytest.mark.my_marker              # Parent marker
   @pytest.mark.my_marker_scenario_b   # Child marker
   @pytest.mark.file_set(FileSet.SINGLE)
   @pytest.mark.json_file_name("my_marker_scenario_b")  # Required!
   class TestIntegrationMyMarkerScenarioB:
       ...
   ```

5. **Write tests for each scenario**

   Each test class follows the same patterns as Option A.

6. **Add generator functions for each child marker**

   See [Generator Functions](#generator-functions-generatedatapy) section.

**Key differences:**
- Multiple test classes in the **same file**
- Each test class has **both parent and child markers**
- Each test class **must** have `@pytest.mark.json_file_name()` decorator
- Each child marker has its **own baseline data file**
- `child_markers.json` tracks the parent-child relationships

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

### The `@generate_json` Decorator

All generator functions must use the `@generate_json` decorator if they want json files generated for the marker name:

**Parameters:**
- `file_set` (FileSet | None): The file set to iterate over (e.g., `FileSet.MESHED`, `FileSet.SINGLE`), or `None` if no project files are needed.
- `synergy_required` (bool): Whether a Synergy instance should be passed to the function. Default: `True`.
  - If `True`: Function receives `synergy=<Synergy instance>` parameter
  - If `False`: Function is called without Synergy (use for static data generation)

**Example:**

```python
@generate_json(file_set=...)  # synergy_required is True by default
def generate_sample_case_data(synergy: Synergy = None):
    return {
        "dd_model": { ... },
        "midplane_model": { ... },
        "3d_model": { ... }
    }
```

### Requirements

- The function must return a Python `dict` containing the baseline content to write to `<marker>_data.json`.
- The function should be idempotent: running it repeatedly should produce consistent results (unless intentionally changed).
- Use `synergy_required=False` only when generating static test data that doesn't need Synergy instantiation.

---

## Child Markers Configuration

The `child_markers.json` file (located at the repository root) defines parent-child relationships between markers. This is essential for the data generation script to understand marker hierarchies.

### File Structure

```json
{
    "parent_marker": ["child_marker_1", "child_marker_2"]
}
```

### Example

```json
{
    "prop": ["material_property", "custom_property"]
}
```

### Usage in Data Generation

When you run `python run.py generate-test-data <parent_marker>`, the script:
1. Reads `child_markers.json` to find all child markers
2. Generates baseline data for **each child marker** by calling `generate_<child_marker>_data()`
3. Creates separate JSON files: `<child_marker>_data.json` for each child

When you run `python run.py generate-test-data <child_marker>`, the script:
1. Generates baseline data only for that specific child marker
2. Creates/updates only `<child_marker>_data.json`

**Important:** Always update `child_markers.json` when adding new parent-child marker relationships. This file must be committed to the repository.

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

| Task | Command | Example |
|------|---------|---------|
| Run all integration tests | `python run.py test --integration` | |
| Run tests for a specific marker | `python run.py test -m <marker>` | `python run.py test -m prop` |
| Run tests for a child marker | `python run.py test -m <child_marker>` | `python run.py test -m material_property` |
| Update / generate baseline data | `python run.py generate-test-data <marker1> <marker2> ...` | `python run.py generate-test-data material_property custom_property` |
| Update baseline for parent marker | `python run.py generate-test-data <parent_marker>` | `python run.py generate-test-data prop` (updates all child markers) |
| Update all baselines | `python run.py generate-test-data` (no markers) | |

**Notes on Parent-Child Markers:**

*For detailed information on which tests run with which markers, see [Test Execution with Parent-Child Markers](#test-execution-with-parent-child-markers).*

**Test Execution:**
- Running tests with a **parent marker** (e.g., `-m prop`) will run **all** test classes marked with that parent marker (i.e., all child test scenarios)
- Running tests with a **child marker** (e.g., `-m material_property`) will run **only** the test class with that specific child marker

**Baseline Data Generation:**
- Generating baseline data for a **parent marker** will automatically generate baselines for **all child markers**
- Generating baseline data for a **child marker** will generate baseline for **only** that child marker

---

## Example Test Suite

### Example 1: Simple Marker

Complete example using marker `sample_case`.

**1) Add marker to `pytest.ini`:**

```ini
markers =
    sample_case: Tests for the sample_case integration suite
```

**2) `tests/api/integration_tests/test_integration_sample_case.py`:**

```python
import pytest
from tests.api.integration_tests.constants import FileSet

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
        study_file, project, study = study_with_project
        expected = expected_values.get(study_file)
        if expected is None:
            pytest.skip(f"No expected data for {study_file}")
        actual = study.get_thickness_results()
        assert actual == expected
```

**3) `generate_data.py`:**

```python
def generate_sample_case_data():
    # open synergy / project / read values programmatically
    return {
        "dd_model": {"thickness": 2.3},
        "midplane_model": {"thickness": 2.35},
        "3d_model": {"thickness": 2.31}
    }
```

**4) Generate baseline:**

```bash
python run.py generate-test-data sample_case
```

After running you should see:
- Data file created: `tests/api/integration_tests/data/sample_case_data.json`
- `metadata.json` updated to include `sample_case`

### Example 2: Parent-Child Markers

Complete example using parent marker `prop` with child markers `material_property` and `custom_property`.

**1) Add markers to `pytest.ini`:**

```ini
markers =
    # ... other API class markers ...
    prop: Tests the Property class
    # ... other API class markers ...
    
    material_property: Tests the pre-existing materials for Property class
    custom_property: Tests a new custom property for Property class
```

**2) Add mapping to `child_markers.json` (in repository root):**

```json
{
    "prop": ["material_property", "custom_property"]
}
```

**3) `tests/api/integration_tests/test_integration_property.py`:**

```python
import pytest
from moldflow import Synergy, Property
from tests.api.integration_tests.constants import FileSet

@pytest.mark.integration
@pytest.mark.prop
@pytest.mark.material_property
@pytest.mark.json_file_name("material_property")
class TestIntegrationMaterialProperty:
    
    @pytest.fixture
    def material_property(self, synergy: Synergy):
        mf = synergy.material_finder
        mf.set_data_domain("GLOBAL", 1)
        mat = mf.get_first_material()
        return mat

    def test_metadata(self, material_property: Property, expected_data: dict):
        assert material_property.name == expected_data["material_name"]
        assert material_property.id == expected_data["material_id"]

@pytest.mark.integration
@pytest.mark.prop
@pytest.mark.custom_property
@pytest.mark.file_set(FileSet.SINGLE)
@pytest.mark.json_file_name("custom_property")
class TestIntegrationCustomProperty:
    
    @pytest.fixture()
    def custom_property(self, synergy: Synergy, study_with_project):
        pe = synergy.property_editor
        prop = pe.create_property(10, 1, True)
        prop.name = "Test Name"
        yield prop
        pe.delete_property(10, 1)

    def test_metadata(self, custom_property: Property, expected_data: dict):
        assert custom_property.name == expected_data["property_name"]
        assert custom_property.id == expected_data["property_id"]
```

**4) `generate_data.py`:**

```python
def generate_material_property_data():
    # open synergy / get material / read values programmatically
    return {
        "material_name": "Coolanol 25 : Chevron",
        "material_id": 14,
        "material_type": 20010,
        # ... more fields
    }

def generate_custom_property_data():
    # create custom property / read values programmatically
    return {
        "property_name": "Test Name",
        "property_id": 1,
        "property_type": 10,
        # ... more fields
    }
```

**5) Generate baselines:**

Option 1: Generate all child markers at once using parent marker
```bash
python run.py generate-test-data prop
```

Option 2: Generate individual child markers
```bash
python run.py generate-test-data material_property custom_property
```

After running you should see:
- Data files created:
  - `tests/api/integration_tests/data/material_property_data.json`
  - `tests/api/integration_tests/data/custom_property_data.json`
- `metadata.json` updated to include both child markers

---

## Best Practices

- **Markers**: always snake_case (e.g., `sample_case`). Keep them descriptive but short [Usually Synergy API class names].
- **Class names**: use PascalCase for the Marker portion (e.g., `TestIntegrationSampleCase`).
- **Generator functions**: return serializable dictionaries only (no complex objects).
- **Metadata**: let the generator update `metadata.json` — do not edit manually.
- **Scope fixtures appropriately**: use class scope for expensive resources like COM instances.
- **Parameterize where possible**: reduce duplication by using `study_file` and `study_with_project`.
- **Document new markers**: add a short explanation in `pytest.ini`.
- **Marker organization in pytest.ini**: 
  - Group markers logically (unit, integration, core markers at top; API class markers in middle)
  - Place child markers at the bottom, separated by a blank line for clarity
  - This makes it easy to identify parent-child relationships at a glance
- **Parent-Child markers**:
  - Use when testing a **single API class** with **multiple distinct scenarios** requiring different baseline data files
  - Parent marker should be named after the API class (e.g., `prop` for `Property` class)
  - Child markers should describe the specific test scenario (e.g., `material_property`, `custom_property`)
  - **Always** include `@pytest.mark.json_file_name()` decorator when using child markers
  - Keep all related test classes in the **same test file** if possible (separating is allowed)
  - Update `child_markers.json` to track parent-child relationships
- **Simple markers**:
  - Use for straightforward test suites with a single test scenario
  - Typically one test class per marker
  - No need for `@pytest.mark.json_file_name()` decorator (unless you want to override the default)

---

## Appendix: Quick Checklist

### Step 1: Decide on Test Structure

- [ ] **Choose your approach:**
  - [ ] **Simple Marker**: Single test scenario, one baseline file → Continue to Step 2A
  - [ ] **Parent-Child Markers**: Multiple independent test scenarios, separate baseline files → Continue to Step 2B

---

### Step 2A: For Simple Marker (Single Test Scenario)

- [ ] Add marker to `pytest.ini` with description (place with other API class markers)
- [ ] Create `test_integration_<marker>.py`
- [ ] Add `TestIntegration<Marker>` class with required decorators:
  - [ ] `@pytest.mark.integration`
  - [ ] `@pytest.mark.<marker>`
  - [ ] `@pytest.mark.file_set(FileSet.<SET>)` (if test needs project/study files)
- [ ] Add fixtures/tests inside the test class
- [ ] If baseline data required:
  - [ ] Create `generate_<marker>_data()` function in `generate_data.py`
  - [ ] Run `python run.py generate-test-data <marker>` to generate baseline
- [ ] Commit changes:
  - [ ] `test_integration_<marker>.py`
  - [ ] `pytest.ini`
  - [ ] `data/<marker>_data.json` (if baseline was generated)
  - [ ] `data/metadata.json` (if baseline was generated)

→ **Done!** Skip to Step 3.

---

### Step 2B: For Parent-Child Markers (Multiple Test Scenarios)

- [ ] Add **all markers** to `pytest.ini` with descriptions:
  - [ ] Parent marker (place with other API class markers)
  - [ ] Child markers (place at bottom after blank line)
- [ ] Add parent-child mapping to `child_markers.json` in repository root:
- [ ] Create `test_integration_<parent_marker>.py` (use parent marker name, can be split into more files if required)
- [ ] **For each child marker**, add a test class with required decorators:
  - [ ] `@pytest.mark.integration`
  - [ ] `@pytest.mark.<parent_marker>` (parent marker)
  - [ ] `@pytest.mark.<child_marker>` (child marker)
  - [ ] `@pytest.mark.json_file_name("<child_marker>")` **(required!)**
  - [ ] `@pytest.mark.file_set(FileSet.<SET>)` (if test needs project/study files)
  - [ ] Add fixtures/tests inside each test class
- [ ] If baseline data required:
  - [ ] Create `generate_<child_marker>_data()` function in `generate_data.py` for **each child marker**
  - [ ] Run `python run.py generate-test-data <parent_marker>` to generate all baselines at once
- [ ] Commit changes:
  - [ ] `test_integration_<parent_marker>.py`
  - [ ] `pytest.ini`
  - [ ] `child_markers.json`
  - [ ] `data/<child_marker_1>_data.json` (if baseline was generated)
  - [ ] `data/<child_marker_2>_data.json` (if baseline was generated)
  - [ ] `data/metadata.json` (if baselines were generated)

---

### Step 3: Verify and Test

- [ ] Run tests to verify everything works:
  - [ ] Simple marker: `python run.py test -m <marker>`
  - [ ] Parent-child: `python run.py test -m <parent_marker>` (runs all child tests)
  - [ ] Parent-child: `python run.py test -m <child_marker>` (runs only that child's tests)
- [ ] Check that all tests pass
- [ ] Review baseline data files for correctness
- [ ] Confirm the baseline generation commands work as expected
  - [ ] Simple marker: `python run.py generate-test-data <marker>`
  - [ ] Parent-child: `python run.py generate-test-data <parent_marker>` (runs all child baseline updates with metadata)
  - [ ] Parent-child: `python run.py generate-test-data <child_marker>` (runs only that child's baseline update with its metadata)
- [ ] Push changes to repository

---