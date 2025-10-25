# Integration Tests for moldflow-api

This document provides guidance on writing integration tests for the `moldflow-api` module using the new test structure and fixtures. The tests focus on real interactions with Moldflow Synergy COM objects and are designed to be reusable and parametrized over multiple models and file sets.

---

## Table of Contents

1. [Overview](#overview)  
2. [File Sets and Model Types](#file-sets-and-model-types)  
3. [Fixtures](#fixtures)  
4. [Writing a Test Suite](#writing-a-test-suite)  
5. [Example Test Suite](#example-test-suite)  
6. [Best Practices](#best-practices)  

---

## Overview

The integration tests are designed to:

- Open a Moldflow project (Raw, Meshed, Analyzed).
- Open individual study files (dd_model, midplane_model, 3d_model) inside the project.
- Compare actual data with expected values stored in JSON files.

The new fixtures and helpers make it easier to write reusable and parametrized tests without duplicating logic.

---

## File Sets and Model Types

### File Sets

The `FileSet` enum defines different categories of study files. Currently supported:

| Enum           | Folder Name | Description |
|----------------|-------------|-------------|
| `FileSet.MESHED` | `Meshed`   | Contains sdy files that are meshed |

> Future expansions will include `RAW` or `ANALYZED`.

### Model Types

The `ModelType` enum defines the types of models in each file set:

| Enum               | Filename in FileSet folder |
|-------------------|---------------------------|
| `ModelType.DD`     | `dd_model`            |
| `ModelType.MIDPLANE` | `midplane_model`     |
| `ModelType.THREE_D` | `3d_model`           |

These enums are used to parametrize tests automatically.

---

## Fixtures

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `synergy` | `class` | Creates a real `Synergy` instance for all tests in a class. Automatically cleans up after tests. |
| `project` | `class` | Opens the project corresponding to the file set specified by `@pytest.mark.file_set(FileSet.<SET>)`. Uses the `synergy` fixture. |
| `study_file` | `function` | Provides `(ModelType, file_path)` tuple for each parametrized test, automatically generated from the file set. |
| `opened_study` | `function` | Opens the study inside the already opened project. Returns the study object. |
| `study_with_project` | `function` | Convenience fixture combining `(ModelType, file_path, project, opened_study)`. |
| `expected_data` | `class` | Loads expected values from a JSON file defined as `json_file_name` in the test class. |
| `expected_values` | `function` | Provides expected values for the current model type. Skips test if no data exists. |

> **Note:** `synergy` and `project` are `class` scoped because creating a COM instance or opening a project is time expensive.

---

## Writing a Test Suite

### 1. Mark the class with file set and integration type

```python
@pytest.mark.integration
@pytest.mark.file_set(FileSet.MESHED)
class TestMyFeature:
    json_file_name = "expected_data.json"
```
The file_set marker determines which set of study files will be used.

The json_file_name attribute points to a file in [data folder](/tests/api/integration_tests/data/) containing expected values.

### 2. Use study_with_project for test functions

```python
def test_something(self, study_with_project):
    model_type, file_path, project, opened_study = study_with_project
    # Now you can use project or opened_study
```

This fixture automatically provides the model type, file path, project handle, and the opened study object.

### 3. Access expected values

```python
def test_mesh_summary(self, study_with_project, expected_values):
    model_type, _, _, _ = study_with_project
    mesh_summary_data = expected_values[model_type.value]
    # Use mesh_summary_data to validate results
```

expected_values returns a dictionary specific to the current model type and the specified json file name at the class level.

The json file structure needs to have all the ModelTypes.value (`dd_model`, `midplane_model`, `3d_model`) as keys, the value for the keys can be as required.

```json
{
    "dd_model": {
        // ...
    },
    "midplane_model": {
        // ...
    },
    "3d_model": {
        // ...
    }
}
```

Skips the test if no expected data exists.

### 4. Create wrapper-specific fixtures

For example, MeshSummary:

```python
@pytest.fixture
def mesh_summary(self, synergy, study_with_project):
    model_type, file_path, _, _ = study_with_project
    diagnosis_manager = synergy.diagnosis_manager
    summary = diagnosis_manager.get_mesh_summary(
        element_only=True, inc_beams=True, inc_match=True, recalculate=True
    )
    if summary is None:
        pytest.skip(f"No mesh summary available for {model_type.value} model")
    return summary
```

## Example Test Suite

```python
import pytest
from moldflow import MeshSummary
from tests.api.integration_tests.conftest import FileSet

@pytest.mark.integration
@pytest.mark.mesh_summary
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationMeshSummary:
    json_file_name = "mesh_summary_data.json"

    @pytest.fixture
    def mesh_summary(self, synergy, study_with_project):
        model_type, file_path, _, _ = study_with_project
        diagnosis_manager = synergy.diagnosis_manager
        summary = diagnosis_manager.get_mesh_summary(
            element_only=True, inc_beams=True, inc_match=True, recalculate=True
        )
        if summary is None:
            pytest.skip(f"No mesh summary available for {model_type.value} model")
        return summary

    def test_aspect_ratio_properties(self, mesh_summary: MeshSummary, expected_values: dict):
        min_ar = mesh_summary.min_aspect_ratio
        max_ar = mesh_summary.max_aspect_ratio
        ave_ar = mesh_summary.ave_aspect_ratio

        assert isinstance(min_ar, float)
        assert min_ar <= ave_ar <= max_ar
        assert abs(min_ar - expected_values["min_aspect_ratio"]) < 0.01
```

> Parametrization is automatically handled based on the FileSet and ModelType.

## Best Practices

- Scope wisely: Use class scope for heavy fixtures like synergy or project.

- JSON-driven tests: Keep expected values in JSON files inside tests/api/integration_tests/data/.

- Marking tests: Always use @pytest.mark.file_set(FileSet.<SET>) on the class.

- Reusability: Use study_with_project or opened_study fixtures to avoid duplicate project or study opening logic.

- Skip gracefully: Use pytest.skip() if the expected data or study is missing for the current model.

# Updating Baseline

## Manual
## Automated