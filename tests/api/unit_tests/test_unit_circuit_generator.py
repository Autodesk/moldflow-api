# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for CircuitGenerator Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import CircuitGenerator


@pytest.mark.unit
class TestUnitCircuitGenerator:
    """
    Test suite for the CircuitGenerator class.
    """

    @pytest.fixture
    def mock_circuit_generator(self, mock_object) -> CircuitGenerator:
        """
        Fixture to create a mock instance of CircuitGenerator.
        Args:
            mock_object: Mock object for the CircuitGenerator dependency.
        Returns:
            CircuitGenerator: An instance of CircuitGenerator with the mock object.
        """
        return CircuitGenerator(mock_object)

    @pytest.mark.parametrize("generate", [True, False])
    def test_generate(self, mock_circuit_generator: CircuitGenerator, mock_object, generate):
        """
        Test the generate method of CircuitGenerator.
        Args:
            mock_circuit_generator: Mock instance of CircuitGenerator.
        """
        mock_object.Generate = generate
        result = mock_circuit_generator.generate()
        assert isinstance(result, bool)
        assert result == generate

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("Diameter", "diameter", 10),
            ("Diameter", "diameter", 1.1),
            ("Distance", "distance", 10),
            ("Distance", "distance", 1.1),
            ("Spacing", "spacing", 10),
            ("Spacing", "spacing", 1.1),
            ("Overhang", "overhang", 10),
            ("Overhang", "overhang", 1.1),
            ("NumChannels", "num_channels", 10),
            ("NumChannels", "num_channels", 1),
            ("DeleteOld", "delete_old", True),
            ("DeleteOld", "delete_old", False),
            ("UseHoses", "use_hoses", True),
            ("UseHoses", "use_hoses", False),
            ("XAlign", "x_align", True),
            ("XAlign", "x_align", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self,
        mock_circuit_generator: CircuitGenerator,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test Get properties of CircuitGenerator.

        Args:
            mock_circuit_generator: Instance of CircuitGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_circuit_generator, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("Diameter", "diameter", 10),
            ("Diameter", "diameter", 1.1),
            ("Distance", "distance", 10),
            ("Distance", "distance", 1.1),
            ("Spacing", "spacing", 10),
            ("Spacing", "spacing", 1.1),
            ("Overhang", "overhang", 10),
            ("Overhang", "overhang", 1.1),
            ("NumChannels", "num_channels", 10),
            ("NumChannels", "num_channels", 1),
            ("DeleteOld", "delete_old", True),
            ("DeleteOld", "delete_old", False),
            ("UseHoses", "use_hoses", True),
            ("UseHoses", "use_hoses", False),
            ("XAlign", "x_align", True),
            ("XAlign", "x_align", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self,
        mock_circuit_generator: CircuitGenerator,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test properties of CircuitGenerator.

        Args:
            mock_circuit_generator: Instance of CircuitGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_circuit_generator, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == value

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("diameter", "1"),
            ("diameter", True),
            ("diameter", None),
            ("distance", "1"),
            ("distance", True),
            ("distance", None),
            ("spacing", "1"),
            ("spacing", True),
            ("spacing", None),
            ("overhang", "1"),
            ("overhang", True),
            ("overhang", None),
            ("num_channels", "1"),
            ("num_channels", True),
            ("num_channels", None),
            ("num_channels", 1.1),
            ("delete_old", "1"),
            ("delete_old", 1),
            ("delete_old", None),
            ("use_hoses", "1"),
            ("use_hoses", 1),
            ("use_hoses", None),
            ("x_align", "1"),
            ("x_align", 1),
            ("x_align", None),
        ],
    )
    def test_invalid_properties(
        self, mock_circuit_generator: CircuitGenerator, property_name, value, _
    ):
        """
        Test invalid properties of CircuitGenerator.
        Args:
            mock_circuit_generator: Instance of CircuitGenerator.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_circuit_generator, property_name, value)
        assert _("Invalid") in str(e.value)
