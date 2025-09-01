# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for MoldSurfaceGenerator Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import MoldSurfaceGenerator, Vector


@pytest.mark.unit
class TestUnitMoldSurfaceGenerator:
    """
    Test suite for the MoldSurfaceGenerator class.
    """

    @pytest.fixture
    def mock_mold_surface_generator(self, mock_object) -> MoldSurfaceGenerator:
        """
        Fixture to create a mock instance of MoldSurfaceGenerator.
        Args:
            mock_object: Mock object for the MoldSurfaceGenerator dependency.
        Returns:
            MoldSurfaceGenerator: An instance of MoldSurfaceGenerator with the mock object.
        """
        return MoldSurfaceGenerator(mock_object)

    @pytest.mark.parametrize("generate", [True, False])
    def test_generate(
        self, mock_mold_surface_generator: MoldSurfaceGenerator, mock_object, generate
    ):
        """
        Test the generate method of MoldSurfaceGenerator.
        Args:
            mock_mold_surface_generator: Mock instance of MoldSurfaceGenerator.
        """
        mock_object.Generate = generate
        result = mock_mold_surface_generator.generate()
        assert isinstance(result, bool)
        assert result == generate

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("Centered", "centered", True),
            ("Centered", "centered", False),
            ("SaveAsCAD", "save_as_cad", True),
            ("SaveAsCAD", "save_as_cad", False),
            ("UseCADMergeTolerance", "use_cad_merge_tolerance", True),
            ("UseCADMergeTolerance", "use_cad_merge_tolerance", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self,
        mock_mold_surface_generator: MoldSurfaceGenerator,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test Get properties of MoldSurfaceGenerator.

        Args:
            mock_mold_surface_generator: Instance of MoldSurfaceGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_mold_surface_generator, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("Centered", "centered", True),
            ("Centered", "centered", False),
            ("SaveAsCAD", "save_as_cad", True),
            ("SaveAsCAD", "save_as_cad", False),
            ("UseCADMergeTolerance", "use_cad_merge_tolerance", True),
            ("UseCADMergeTolerance", "use_cad_merge_tolerance", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self,
        mock_mold_surface_generator: MoldSurfaceGenerator,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test properties of MoldSurfaceGenerator.

        Args:
            mock_mold_surface_generator: Instance of MoldSurfaceGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_mold_surface_generator, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == value

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("centered", 1),
            ("centered", None),
            ("centered", "1"),
            ("origin", 1),
            ("origin", 1.1),
            ("origin", "1"),
            ("dimensions", 1),
            ("dimensions", 1.1),
            ("dimensions", "1"),
            ("save_as_cad", 1),
            ("save_as_cad", None),
            ("save_as_cad", "1"),
            ("use_cad_merge_tolerance", 1),
            ("use_cad_merge_tolerance", None),
            ("use_cad_merge_tolerance", "1"),
        ],
    )
    def test_invalid_properties(
        self, mock_mold_surface_generator: MoldSurfaceGenerator, property_name, value, _
    ):
        """
        Test invalid properties of MoldSurfaceGenerator.
        Args:
            mock_mold_surface_generator: Instance of MoldSurfaceGenerator.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_mold_surface_generator, property_name, value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("Origin", "origin"), ("Dimensions", "dimensions")]
    )
    def test_origin_dimensions(
        self,
        mock_mold_surface_generator: MoldSurfaceGenerator,
        mock_object,
        pascal_name,
        property_name,
    ):
        """
        Test origin and dimensions properties of MoldSurfaceGenerator.
        Args:
            mock_mold_surface_generator: Instance of MoldSurfaceGenerator.
        """
        vector_mock = Mock()
        mock_sample = Mock(spec=Vector)
        mock_sample.vector = vector_mock
        setattr(mock_object, pascal_name, vector_mock)
        result = getattr(mock_mold_surface_generator, property_name)
        assert isinstance(result, Vector)
        assert result.vector == vector_mock

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("Origin", "origin"), ("Dimensions", "dimensions")]
    )
    def test_origin_dimensions_set(
        self,
        mock_mold_surface_generator: MoldSurfaceGenerator,
        mock_object,
        pascal_name,
        property_name,
    ):
        """
        Test origin and dimensions properties of MoldSurfaceGenerator.
        Args:
            mock_mold_surface_generator: Instance of MoldSurfaceGenerator.
        """
        vector_mock = Mock()
        mock_sample = Mock(spec=Vector)
        mock_sample.vector = vector_mock
        setattr(mock_mold_surface_generator, property_name, mock_sample)
        result = getattr(mock_object, pascal_name)
        assert result == vector_mock

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("Origin", "origin"), ("Dimensions", "dimensions")]
    )
    def test_property_return_none(
        self,
        mock_mold_surface_generator: MoldSurfaceGenerator,
        mock_object,
        pascal_name,
        property_name,
    ):
        """
        Test the return value of the function is None.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_mold_surface_generator, property_name)
        assert result is None
