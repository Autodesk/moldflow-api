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

- **Scope wisely**: Use class scope for heavy fixtures like synergy or project.
- **JSON-driven tests**: Keep expected values in JSON files inside tests/api/integration_tests/data/.
- **Marking tests**: Always use @pytest.mark.file_set(FileSet.<SET>) on the class.
- **Reusability**: Use study_with_project or opened_study fixtures to avoid duplicate project or study opening logic.
- **Skip gracefully**: Use pytest.skip() if the expected data or study is missing for the current model.

# Test Data Generation

The integration tests rely on expected data stored in JSON files. This data is generated from actual Moldflow Synergy projects to ensure accuracy and consistency.

## Generation Commands

### Using run.py (Recommended)

Generate all test data:
```bash
python run.py generate-test-data
```

Generate data for specific markers:
```bash
python run.py generate-test-data mesh_summary
```

## How It Works

### Data Generation Process

1. **Project Opening**: The generator opens Moldflow projects from the [study_files](/tests/api/integration_tests/study_files/) directory
2. **Model Iteration**: For each project, it iterates through all available model types (dd_model, midplane_model, 3d_model)
3. **Data Extraction**: Calls the appropriate API methods to extract data (e.g., mesh summary properties)
4. **JSON Output**: Saves the extracted data to JSON files in the [data](/tests/api/integration_tests/data/) directory

### File Structure

```
tests/api/integration_tests/
├── data/
│   ├── mesh_summary_data.json     # Generated expected values
│   └── data_generation/
│       ├── generate_data.py        # Main generation script
│       └── generate_data_helper.py # Helper functions and decorators
├── study_files/
│   └── Meshed/                     # Study files for data generation
│       ├── Meshed.mpi             # Project file
│       ├── dd_model.sdy           # Double-sided model
│       ├── midplane_model.sdy     # Midplane model
│       └── 3d_model.sdy           # 3D model
└── constants.py                    # Enums and constants
```

### Adding New Data Generation

To add generation for a new feature:

1. **Create a generation function** in `generate_data.py`:
```python
@generate_json(json_file_name=DataFile.MY_FEATURE, file_set=FileSet.MESHED)
def generate_my_feature(synergy: Synergy):
    """Extract my feature data from a study."""
    my_data = synergy.some_manager.get_my_data()
    return {
        "property1": my_data.property1,
        "property2": my_data.property2,
    }
```

2. **Add to GENERATE_FUNCTIONS** dictionary:
```python
GENERATE_FUNCTIONS = {
    "mesh_summary": generate_mesh_summary,
    "my_feature": generate_my_feature,  # Add this line
}
```

3. **Add DataFile enum** in `constants.py`:
```python
class DataFile(Enum):
    MESH_SUMMARY = "mesh_summary_data.json"
    MY_FEATURE = "my_feature_data.json"  # Add this line
```

4. **Generate the data**:
```bash
python run.py generate-test-data my_feature
```

### Data File Format

Generated JSON files follow this structure:
```json
{
    "dd_model": {
        "property1": value1,
        "property2": value2
    },
    "midplane_model": {
        "property1": value3,
        "property2": value4
    },
    "3d_model": {
        "property1": value5,
        "property2": value6
    }
}
```

Each model type has its own section with the extracted data properties.

## Best Practices for Data Generation

- **Consistency**: Always use the `@generate_json` decorator for new generation functions
- **Error Handling**: The decorator handles project opening/closing and error cleanup automatically
- **Selective Generation**: Use markers to generate only specific data sets during development
- **Version Control**: Commit generated JSON files to ensure consistent test data across environments
- **Validation**: After generation, run the corresponding tests to verify the data is correct
