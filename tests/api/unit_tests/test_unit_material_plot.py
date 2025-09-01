# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the MaterialPlot wrapper class in the moldflow-api module.
"""

import pytest
from moldflow import MaterialPlot


@pytest.mark.unit
class TestUnitMaterialPlot:
    """
    Test suite for the MaterialPlot class.
    """

    @pytest.fixture
    def mock_material_plot(self, mock_object) -> MaterialPlot:
        """
        Fixture to create a mock instance of MaterialPlot.
        Args:
            mock_object: Mock object for the MaterialPlot dependency.
        Returns:
            MaterialPlot: An instance of MaterialPlot with the mock object.
        """
        return MaterialPlot(mock_object)

    @pytest.mark.parametrize("file_name", ["test_image.png", "test_data.txt"])
    def test_save_image(self, mock_material_plot: MaterialPlot, mock_object, file_name):
        """
        Test saving image of MaterialPlot.
        Args:
            mock_material_plot: Instance of MaterialPlot.
            file_name: Name of the file to save the image to.
        """
        mock_material_plot.save_image(file_name)
        mock_object.SaveImage.assert_called_once_with(file_name)

    @pytest.mark.parametrize("file_name", ["test_image.png", "test_data.txt"])
    def test_save_data(self, mock_material_plot: MaterialPlot, mock_object, file_name):
        """
        Test saving data of MaterialPlot.
        Args:
            mock_material_plot: Instance of MaterialPlot.
            file_name: Name of the file to save the data to.
        """
        mock_material_plot.save_data(file_name)
        mock_object.SaveData.assert_called_once_with(file_name)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("DefaultValueRangeX", "default_value_range_x", True),
            ("DefaultValueRangeX", "default_value_range_x", False),
            ("DefaultValueRangeY", "default_value_range_y", True),
            ("DefaultValueRangeY", "default_value_range_y", False),
            ("ValueRangeMinX", "value_range_min_x", 10),
            ("ValueRangeMinX", "value_range_min_x", 1.0),
            ("ValueRangeMaxX", "value_range_max_x", 10),
            ("ValueRangeMaxX", "value_range_max_x", 1.0),
            ("ValueRangeMinY", "value_range_min_y", 10),
            ("ValueRangeMinY", "value_range_min_y", 1.0),
            ("ValueRangeMaxY", "value_range_max_y", 10),
            ("ValueRangeMaxY", "value_range_max_y", 1.0),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_material_plot: MaterialPlot, mock_object, pascal_name, property_name, value
    ):
        """
        Test properties of MaterialPlot.
        Args:
            mock_material_plot: Instance of MaterialPlot.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_material_plot, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("DefaultValueRangeX", "default_value_range_x", True),
            ("DefaultValueRangeX", "default_value_range_x", False),
            ("DefaultValueRangeY", "default_value_range_y", True),
            ("DefaultValueRangeY", "default_value_range_y", False),
            ("ValueRangeMinX", "value_range_min_x", 10),
            ("ValueRangeMinX", "value_range_min_x", 1.0),
            ("ValueRangeMaxX", "value_range_max_x", 10),
            ("ValueRangeMaxX", "value_range_max_x", 1.0),
            ("ValueRangeMinY", "value_range_min_y", 10),
            ("ValueRangeMinY", "value_range_min_y", 1.0),
            ("ValueRangeMaxY", "value_range_max_y", 10),
            ("ValueRangeMaxY", "value_range_max_y", 1.0),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_material_plot: MaterialPlot, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of MaterialPlot.
        Args:
            mock_material_plot: Instance of MaterialPlot.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_material_plot, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("default_value_range_x", "100"),
            ("default_value_range_x", 10),
            ("default_value_range_y", "200"),
            ("default_value_range_y", 10),
            ("value_range_min_x", True),
            ("value_range_min_x", "110"),
            ("value_range_max_x", False),
            ("value_range_max_x", "120"),
            ("value_range_min_y", True),
            ("value_range_min_y", "130"),
            ("value_range_max_y", False),
            ("value_range_max_y", "140"),
        ],
    )
    def test_invalid_properties(self, mock_material_plot: MaterialPlot, property_name, value):
        """
        Test invalid properties of MaterialPlot.
        Args:
            mock_material_plot: Instance of MaterialPlot.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_material_plot, property_name, value)
        assert "Invalid" in str(e.value)
