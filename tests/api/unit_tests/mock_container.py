"""This module contains the MockContainer class for the moldflow-api unit tests."""

import inspect
from unittest.mock import Mock
from typing import Dict, Type
import moldflow


def _get_moldflow_classes() -> Dict[str, Type]:
    """Automatically discover all classes from the moldflow module using module names."""
    mock_definitions = {}

    for _, obj in inspect.getmembers(moldflow):
        if (
            inspect.isclass(obj)
            and hasattr(obj, '__module__')
            and obj.__module__
            and obj.__module__.startswith('moldflow.')
            and not obj.__module__.startswith('moldflow.common')
        ):
            module_name = obj.__module__.split('.')[-1]  # e.g., 'moldflow.ent_list' -> 'ent_list'
            mock_definitions[module_name] = obj

    return mock_definitions


class MockContainer:
    """Container for mock objects that provides attribute access with IntelliSense support."""

    def __init__(self):
        # Auto-generate mock definitions from moldflow module
        self._mock_definitions = _get_moldflow_classes()

        # Create mock objects for each type
        for key, value in self._mock_definitions.items():
            mock_obj = Mock(spec=value)
            setattr(mock_obj, key, Mock())
            setattr(self, key.upper(), mock_obj)

    # Explicit attribute definitions for IntelliSense support
    BOUNDARY_CONDITIONS: Mock
    BOUNDARY_LIST: Mock
    CAD_MANAGER: Mock
    CIRCUIT_GENERATOR: Mock
    DATA_TRANSFORM: Mock
    DIAGNOSIS_MANAGER: Mock
    DOUBLE_ARRAY: Mock
    ENT_LIST: Mock
    FOLDER_MANAGER: Mock
    IMPORT_OPTIONS: Mock
    INTEGER_ARRAY: Mock
    LAYER_MANAGER: Mock
    MATERIAL_FINDER: Mock
    MATERIAL_PLOT: Mock
    MATERIAL_SELECTOR: Mock
    MESH_EDITOR: Mock
    MESH_GENERATOR: Mock
    MODEL_DUPLICATOR: Mock
    MODELER: Mock
    MOLD_SURFACE_GENERATOR: Mock
    PLOT_MANAGER: Mock
    PLOT: Mock
    PREDICATE_MANAGER: Mock
    PREDICATE: Mock
    PROJECT: Mock
    PROPERTY_EDITOR: Mock
    PROP: Mock
    RUNNER_GENERATOR: Mock
    SERVER: Mock
    STRING_ARRAY: Mock
    STUDY_DOC: Mock
    SYSTEM_MESSAGE: Mock
    UNIT_CONVERSION: Mock
    USER_PLOT: Mock
    VECTOR_ARRAY: Mock
    VECTOR: Mock
    VIEWER: Mock

    def __getitem__(self, key):
        """Maintain backward compatibility with bracket notation."""
        # Convert lowercase keys to uppercase for backward compatibility
        if key in self._mock_definitions:
            return getattr(self, key.upper())
        return getattr(self, key)

    def items(self):
        """Maintain backward compatibility with dict.items() method."""
        for attr_name in self._mock_definitions:
            # Return lowercase keys for backward compatibility
            yield attr_name, getattr(self, attr_name.upper())
