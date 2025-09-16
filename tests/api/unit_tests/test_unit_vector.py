# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for Vector Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import Vector


@pytest.mark.unit
@pytest.mark.vector
class TestUnitVector:
    """
    Test suite for the Vector class.
    """

    @pytest.fixture
    def mock_vector(self, mock_object) -> Vector:
        """
        Fixture to create a mock instance of Vector.
        Args:
            mock_object: Mock object for the Vector dependency.
        Returns:
            Vector: An instance of Vector with the mock object.
        """
        return Vector(mock_object)

    @pytest.mark.parametrize("x, y, z", [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)])
    # pylint: disable-next=R0913, R0917
    def test_set_xyz(self, mock_vector: Vector, mock_object, x, y, z):
        """
        Test set_xyz method of Vector class.
        Args:
            mock_vector: Instance of Vector class.
            mock_object: Mock object for the Vector dependency.
        """
        mock_vector.set_xyz(x, y, z)
        mock_object.SetXYZ.assert_called_once_with(x, y, z)

    @pytest.mark.parametrize("x, y, z", [("1.0", 2.0, 3.0), (4.0, True, 6.0)])
    # pylint: disable-next=R0913, R0917
    def test_set_xyz_invalid(self, mock_vector: Vector, mock_object, x, y, z, _):
        """
        Test set_xyz method of Vector class with invalid arguments.
        Args:
            mock_vector: Instance of Vector class.
            mock_object: Mock object for the Vector dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_vector.set_xyz(x, y, z)
        assert _("Invalid") in str(e.value)
        mock_object.SetXYZ.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("X", "x", 10.0),
            ("Y", "y", 20.0),
            ("Z", "z", 30.0),
            ("X", "x", 10),
            ("Y", "y", 20),
            ("Z", "z", 30),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_vector: Vector, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of Vector.

        Args:
            mock_vector: Instance of Vector.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_vector, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "property_name, pascal_case, value",
        [
            ("x", "X", 5.0),
            ("x", "X", 2),
            ("y", "Y", 5.0),
            ("y", "Y", 3),
            ("z", "Z", 6.5),
            ("z", "Z", 2),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_vector: Vector, mock_object, property_name, pascal_case, value
    ):
        """
        Test Set properties of Vector.
        """
        setattr(mock_vector, property_name, value)
        result = getattr(mock_object, pascal_case)
        assert isinstance(result, type(value))
        assert result == value
