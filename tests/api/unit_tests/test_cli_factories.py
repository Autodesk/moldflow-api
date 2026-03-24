# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Focused regression tests for moldflow_cli.factories helpers."""

from __future__ import annotations

from unittest.mock import patch
import typing

import pytest
from moldflow.cli_input_metadata import cli_input_adapter

from moldflow_cli.invoke_resolution import _resolve_return_class
from moldflow_cli.factories import configure_object_from_dict
from moldflow_cli.factories import _is_none_annotation
from moldflow_cli.factories import build_wrapper_instance
from moldflow_cli.factories import camel_to_snake
from moldflow_cli.factories import convert_value
from moldflow_cli.type_annotations import extract_non_none_annotation_type_names
from moldflow_cli.type_annotations import extract_non_none_type_names
from moldflow_cli.wrapper_input_adapters import build_wrapper_input_adapter_hints


@pytest.mark.cli
@pytest.mark.unit
def test_is_none_annotation_only_matches_nonetype():
    """Regression: broad types like object must not be treated as NoneType."""
    assert _is_none_annotation(type(None)) is True
    assert _is_none_annotation(object) is False
    assert _is_none_annotation(int) is False


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_nested_object_dict_conversion():
    """Test convert_value/configure_object_from_dict builds typed wrapper from dict shape."""

    class FakeObj:
        """Simple object used for typed conversion checks."""

        def __init__(self) -> None:
            self.example_field = None

    class Sy:
        """Fake Synergy host exposing import_options property."""

        import_options = FakeObj()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        typed = {"__type__": "ImportOptions", "example_field": 123}
        obj = convert_value(typed)
        # Should be a wrapper instance with attribute set.
        assert hasattr(obj, "example_field")
        assert obj.example_field == 123


@pytest.mark.cli
@pytest.mark.unit
def test_convert_value_rejects_non_public_typed_object_fields():
    """Typed-object conversion must reject non-public fields from JSON payloads."""

    class FakeObj:
        """Simple object used for typed conversion checks."""

    class Sy:
        """Fake Synergy host exposing import_options property."""

        import_options = FakeObj()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        with pytest.raises(ValueError, match="Non-public field '_private' is not allowed"):
            convert_value({"__type__": "ImportOptions", "_private": 1})


@pytest.mark.cli
@pytest.mark.unit
def test_invoke_build_wrapper_instance_failure_message():
    """build_wrapper_instance should raise a ValueError mentioning the unknown type."""

    with patch("moldflow_cli.factories.get_synergy", return_value=object()):
        with pytest.raises(ValueError) as exc:
            build_wrapper_instance("NoSuchType")
        assert "NoSuchType" in str(exc.value)


@pytest.mark.cli
@pytest.mark.unit
def test_camel_to_snake_handles_acronym_boundaries():
    """Acronym-heavy class names should map to stable snake_case CLI names."""

    assert camel_to_snake("CADManager") == "cad_manager"
    assert camel_to_snake("XMLParser") == "xml_parser"
    assert camel_to_snake("ImportOptions") == "import_options"


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_instance_handles_union_forward_ref():
    """build_wrapper_instance handles union-like forward-ref annotation strings."""

    class FakeImportOptions:
        """Dummy ImportOptions-like object for wrapper construction tests."""

        def __init__(self) -> None:
            self.example = "ok"

    class Sy:
        """Fake Synergy host exposing import_options property."""

        import_options = FakeImportOptions()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        inst = build_wrapper_instance("ImportOptions | None")
        assert isinstance(inst, FakeImportOptions)
        inst2 = build_wrapper_instance("'ImportOptions | None'")
        assert isinstance(inst2, FakeImportOptions)
        inst3 = build_wrapper_instance("ImportOptions|None")
        assert isinstance(inst3, FakeImportOptions)
        inst4 = build_wrapper_instance("Optional[ImportOptions]")
        assert isinstance(inst4, FakeImportOptions)
        inst5 = build_wrapper_instance("typing.Optional[ImportOptions]")
        assert isinstance(inst5, FakeImportOptions)
        inst6 = build_wrapper_instance(typing.Optional["ImportOptions"])
        assert isinstance(inst6, FakeImportOptions)
        inst7 = build_wrapper_instance(typing.Annotated[typing.Optional["ImportOptions"], "meta"])
        assert isinstance(inst7, FakeImportOptions)


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_instance_entlist_scans_synergy_related_providers():
    """EntList resolution should discover any related provider exposing create_entity_list."""

    class FakeEntList:
        """Dummy EntList-like object for provider discovery tests."""

    class PropertyEditorProvider:
        """Fake provider reachable through a Synergy property."""

        def create_entity_list(self) -> FakeEntList:
            """Return an entity-list instance through the discovered provider API."""

            return FakeEntList()

    class Sy:
        """Fake Synergy host exposing only property_editor as an EntList-capable provider."""

        @property
        def property_editor(self) -> PropertyEditorProvider:
            """Expose a provider that can create entity lists."""

            return PropertyEditorProvider()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        assert isinstance(build_wrapper_instance("EntList"), FakeEntList)


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_instance_derives_synergy_factory_names():
    """Known array/vector wrappers should resolve through derived Synergy factory names."""

    class FakeVector:
        """Dummy vector wrapper for factory-resolution tests."""

    class FakeVectorArray:
        """Dummy vector-array wrapper for factory-resolution tests."""

    class Sy:
        """Fake Synergy host exposing factory methods that follow the naming convention."""

        def create_vector(self) -> FakeVector:
            """Return a vector wrapper instance using the conventional factory name."""

            return FakeVector()

        def create_vector_array(self) -> FakeVectorArray:
            """Return a vector-array wrapper instance using the conventional factory name."""

            return FakeVectorArray()

    with patch("moldflow_cli.factories.get_synergy", return_value=Sy()):
        assert isinstance(build_wrapper_instance("Vector"), FakeVector)
        assert isinstance(build_wrapper_instance("VectorArray"), FakeVectorArray)


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_selection_adapter_uses_string_input():
    """Selection-like wrapper fields should route through select_from_string without setattr."""

    class FakeSelectionWrapper:
        """Dummy wrapper exposing select_from_string for adapter tests."""

        def __init__(self) -> None:
            """Initialize selection state for the test wrapper."""

            self.selected = None

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            """Capture the reflected selection string value."""

            self.selected = entity_string

    obj = FakeSelectionWrapper()
    configure_object_from_dict(obj, {"entity_string": "N1,N2"})
    assert obj.selected == "N1,N2"


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_selection_adapter_requires_string():
    """Selection-like JSON fields must remain strict strings."""

    class FakeSelectionWrapper:
        """Dummy wrapper exposing select_from_string for adapter tests."""

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:  # pragma: no cover
            """Fail fast if the adapter accepts a non-string selection payload."""

            raise AssertionError("select_from_string should not be called")

    with pytest.raises(ValueError, match="must be a string selection expression"):
        configure_object_from_dict(FakeSelectionWrapper(), {"entity_string": 42})


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_selection_adapter_uses_reflected_param_name():
    """Selection-like wrappers should use the reflected parameter name as the JSON field."""

    class FakeSelectionWrapper:
        """Dummy wrapper exposing select_from_string for adapter tests."""

        def __init__(self) -> None:
            """Initialize selection state for the test wrapper."""

            self.selected = None

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, value: str) -> None:
            """Capture the reflected parameter name chosen by adapter discovery."""

            self.selected = value

    obj = FakeSelectionWrapper()
    configure_object_from_dict(obj, {"value": "N1"})
    assert obj.selected == "N1"


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_vector_adapter_uses_xyz_triplet():
    """Vector-like wrappers should accept the canonical xyz adapter field."""

    class FakeVector:
        """Dummy vector wrapper exposing a vector-triplet adapter method."""

        def __init__(self) -> None:
            """Initialize vector state for the test wrapper."""

            self.value = None

        @cli_input_adapter(
            value_kind="vector_triplet", preferred_field="xyz", shorthand_supported=True
        )
        def set_xyz(self, x: float, y: float, z: float) -> None:
            """Store the adapted xyz triplet as floats."""

            self.value = (x, y, z)

    obj = FakeVector()
    configure_object_from_dict(obj, {"xyz": [1, 2, 3]})
    assert obj.value == (1.0, 2.0, 3.0)


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_list_values_adapter_uses_from_list():
    """List-backed wrappers should accept the canonical values adapter field."""

    class FakeDoubleArray:
        """Dummy list-backed wrapper exposing a values adapter method."""

        def __init__(self) -> None:
            """Initialize list state for the test wrapper."""

            self.values = None

        @cli_input_adapter(value_kind="list_values")
        def from_list(self, values: list[float]) -> None:
            """Store the adapted list payload."""

            self.values = list(values)

    obj = FakeDoubleArray()
    configure_object_from_dict(obj, {"values": [1.0, 2.5]})
    assert obj.values == [1.0, 2.5]


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_accepts_matching_type_alias_metadata():
    """Wrapper JSON may include a matching plain type field without changing the inferred target."""

    class FakeDoubleArray:
        """Dummy list-backed wrapper exposing a values adapter method."""

        def __init__(self) -> None:
            """Initialize list state for the test wrapper."""

            self.values = None

        @cli_input_adapter(value_kind="list_values")
        def from_list(self, values: list[float]) -> None:
            """Store the adapted list payload."""

            self.values = list(values)

    obj = FakeDoubleArray()
    configure_object_from_dict(obj, {"type": "FakeDoubleArray", "values": [1.0, 2.5]})
    assert obj.values == [1.0, 2.5]


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_rejects_mismatched_type_alias_metadata():
    """Wrapper JSON should fail fast on mismatched explicit type aliases."""

    class FakeDoubleArray:
        """Dummy list-backed wrapper exposing a values adapter method."""

        @cli_input_adapter(value_kind="list_values")
        def from_list(self, values: list[float]) -> None:
            """Accept list values for the wrapper."""

    with pytest.raises(ValueError, match="does not match expected wrapper 'FakeDoubleArray'"):
        configure_object_from_dict(FakeDoubleArray(), {"type": "Vector", "values": [1.0, 2.5]})


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_reuses_existing_nested_wrapper_context():
    """Nested wrapper-valued attributes should accept untagged JSON.

    An existing wrapper instance provides enough context to avoid a nested ``__type__`` tag.
    """

    class FakeVector:
        """Dummy vector wrapper exposing a vector-triplet adapter method."""

        def __init__(self) -> None:
            """Initialize vector state for the nested wrapper."""

            self.xyz = None

        @cli_input_adapter(
            value_kind="vector_triplet", preferred_field="xyz", shorthand_supported=True
        )
        def set_xyz(self, x: float, y: float, z: float) -> None:
            """Store the adapted xyz triplet."""

            self.xyz = (x, y, z)

    class FakeOuter:
        """Dummy wrapper exposing an already-instantiated nested vector object."""

        def __init__(self) -> None:
            """Initialize nested wrapper state."""

            self.direction = FakeVector()

    obj = FakeOuter()
    configure_object_from_dict(obj, {"direction": {"xyz": [1, 2, 3]}})
    assert obj.direction.xyz == (1.0, 2.0, 3.0)


@pytest.mark.cli
@pytest.mark.unit
def test_configure_object_from_dict_invalid_adapter_field_reports_guidance():
    """Unknown wrapper JSON fields should point users to the canonical adapter field."""

    class FakeSelectionWrapper:
        """Dummy selection wrapper exposing a canonical selection field."""

        @cli_input_adapter(value_kind="selection_text", shorthand_supported=True)
        def select_from_string(self, entity_string: str) -> None:
            """Accept a canonical selection string."""

    with pytest.raises(ValueError, match="entity_string") as exc_info:
        configure_object_from_dict(FakeSelectionWrapper(), {"value": "N1,N2"})

    assert "N1,N2" in str(exc_info.value)


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_input_adapter_hints_for_vector_prefers_xyz_triplet():
    """Template hints for vectors should expose canonical xyz input and shorthand."""

    hints = build_wrapper_input_adapter_hints("Vector")
    assert isinstance(hints, dict)
    friendly_json_input = hints.get("friendly_json_input")
    assert isinstance(friendly_json_input, dict)
    non_json_input = hints.get("non_json_input")
    assert isinstance(non_json_input, dict)
    examples = hints.get("examples")
    assert isinstance(examples, dict)
    assert friendly_json_input.get("preferred_field") == "xyz"
    assert non_json_input.get("preferred_syntax") == "<param>=0,0,1"
    assert examples.get("preferred_non_json") == "<param>=0,0,1"


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_input_adapter_hints_for_double_array_prefers_values():
    """Template hints for list-backed wrappers should expose canonical values input."""

    hints = build_wrapper_input_adapter_hints("DoubleArray")
    assert isinstance(hints, dict)
    friendly_json_input = hints.get("friendly_json_input")
    assert isinstance(friendly_json_input, dict)
    typed_json_shape = hints.get("typed_json_shape")
    assert isinstance(typed_json_shape, dict)
    examples = hints.get("examples")
    assert isinstance(examples, dict)
    preferred_param_value = examples.get("preferred_param_value")
    assert isinstance(preferred_param_value, dict)
    non_json_input = hints.get("non_json_input")
    assert isinstance(non_json_input, dict)
    assert friendly_json_input.get("preferred_field") == "values"
    assert typed_json_shape.get("__type__") == "DoubleArray"
    assert preferred_param_value.get("values")
    assert non_json_input.get("preferred_syntax") == "<param>=1.0,2.5"
    assert examples.get("preferred_non_json") == "<param>=1.0,2.5"


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_input_adapter_hints_normalizes_alias_to_canonical_type_name():
    """Alias-based hint lookups should still emit the canonical exported wrapper type."""

    hints = build_wrapper_input_adapter_hints("double_array")
    assert isinstance(hints, dict)
    typed_json_shape = hints.get("typed_json_shape")
    assert isinstance(typed_json_shape, dict)
    assert typed_json_shape.get("__type__") == "DoubleArray"


@pytest.mark.cli
@pytest.mark.unit
def test_build_wrapper_input_adapter_hints_for_vector_array_prefers_triplet_series():
    """Template hints for vector arrays should expose canonical series input and shorthand."""

    hints = build_wrapper_input_adapter_hints("VectorArray")
    assert isinstance(hints, dict)
    friendly_json_input = hints.get("friendly_json_input")
    assert isinstance(friendly_json_input, dict)
    non_json_input = hints.get("non_json_input")
    assert isinstance(non_json_input, dict)
    examples = hints.get("examples")
    assert isinstance(examples, dict)
    assert friendly_json_input.get("preferred_field") == "xyz"
    assert non_json_input.get("preferred_syntax") == "<param>=0,0,0;1,0,0"
    assert examples.get("preferred_non_json") == "<param>=0,0,0;1,0,0"


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_string_union_is_ignored_when_ambiguous():
    """String Union with multiple concrete wrappers should not infer a next class."""

    class Plot:
        """Dummy wrapper class for resolve_return_class tests."""

    class StudyDoc:
        """Dummy wrapper class for resolve_return_class tests."""

    cli_to_class = {"plot": Plot, "study_doc": StudyDoc}
    assert _resolve_return_class("Union[Plot, StudyDoc, None]", cli_to_class) is None


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_nested_generic_optional_does_not_infer_wrapper():
    """Nested generic return refs should not infer a direct chained wrapper class."""

    class Vector:
        """Dummy wrapper class for resolve_return_class tests."""

    cli_to_class = {"vector": Vector}
    assert _resolve_return_class("Optional[list[Vector]]", cli_to_class) is None


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_string_fully_qualified_name_pipe_optional():
    """Fully qualified wrapper names should resolve by leaf class name."""

    class Plot:
        """Dummy wrapper class for resolve_return_class tests."""

    cli_to_class = {"plot": Plot}
    assert _resolve_return_class("moldflow.plot.Plot | None", cli_to_class) is Plot


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_deduplicates_aliases_for_same_class():
    """Multiple CLI aliases for one class should still resolve unambiguously."""

    class Plot:
        """Dummy wrapper class for resolve_return_class alias tests."""

    cli_to_class = {"plot": Plot, "plot_alias": Plot}
    assert _resolve_return_class("Optional[Plot]", cli_to_class) is Plot


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_accepts_snake_case_alias_annotation():
    """Snake_case alias annotations should resolve to the underlying wrapper class."""

    class DoubleArray:
        """Dummy wrapper class for resolve_return_class snake_case alias tests."""

    cli_to_class = {"doublearray": DoubleArray}
    assert _resolve_return_class("double_array | None", cli_to_class) is DoubleArray


@pytest.mark.cli
@pytest.mark.unit
def test_resolve_return_class_annotated_string_type():
    """Annotated return type strings should resolve to the wrapped class."""

    class Plot:
        """Dummy wrapper class for annotated return resolution tests."""

    cli_to_class = {"plot": Plot}
    annotation = typing.Annotated["Plot", "meta"]
    assert _resolve_return_class(annotation, cli_to_class) is Plot


@pytest.mark.cli
@pytest.mark.unit
def test_extract_non_none_annotation_type_names_handles_annotated_string():
    """String Annotated[T, ...] should resolve to T for chain inference."""
    assert extract_non_none_annotation_type_names('Annotated["Plot", "meta"]') == ["Plot"]


@pytest.mark.cli
@pytest.mark.unit
def test_extract_non_none_type_names_handles_runtime_annotations():
    """Runtime annotation objects should resolve through the shared helper."""
    assert extract_non_none_type_names(typing.Optional["Plot"]) == ["Plot"]
    annotation = typing.Annotated[typing.Optional["Plot"], "meta"]
    assert extract_non_none_type_names(annotation) == ["Plot"]
    assert extract_non_none_type_names(typing.Optional[list["Plot"]]) == []


@pytest.mark.cli
@pytest.mark.unit
def test_annotation_string_malformed_input_gracefully_falls_back():
    """Malformed annotation strings should not raise and should resolve to no class."""

    class Plot:
        """Dummy wrapper class for malformed annotation tests."""

    names = extract_non_none_annotation_type_names("Optional[")
    assert isinstance(names, list)
    assert _resolve_return_class("Optional[", {"plot": Plot}) is None
