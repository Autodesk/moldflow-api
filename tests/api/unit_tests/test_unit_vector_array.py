# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for VectorArray Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import VectorArray


@pytest.mark.unit
class TestUnitVectorArray:
    """
    Test suite for the VectorArray class.
    """

    @pytest.fixture
    def mock_vector_array(self, mock_object) -> VectorArray:
        """
        Fixture to create a mock instance of VectorArray.
        Args:
            mock_object: Mock object for the VectorArray dependency.
        Returns:
            VectorArray: An instance of VectorArray with the mock object.
        """
        return VectorArray(mock_object)

    def test_clear(self, mock_vector_array: VectorArray, mock_object):
        """
        Test clear method of VectorArray.
        """
        mock_vector_array.clear()
        mock_object.Clear.assert_called_once()

    @pytest.mark.parametrize("x, y, z", [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)])
    # pylint: disable-next=R0913, R0917
    def test_add_xyz(self, mock_vector_array: VectorArray, mock_object, x, y, z):
        """
        Test add_xyz method of VectorArray class.
        Args:
            mock_vector_array: Instance of VectorArray class.
            mock_object: Mock object for the VectorArray dependency.
        """
        mock_vector_array.add_xyz(x, y, z)
        mock_object.AddXYZ.assert_called_once_with(x, y, z)

    @pytest.mark.parametrize("x, y, z", [("1.0", 2.0, 3.0), (4.0, True, 6.0), (7.0, 8.0, "9.0")])
    # pylint: disable-next=R0913, R0917
    def test_add_xyz_invalid(self, mock_vector_array: VectorArray, mock_object, x, y, z, _):
        """
        Test add_xyz method of VectorArray class with invalid arguments.
        Args:
            mock_vector_array: Instance of VectorArray class.
            mock_object: Mock object for the VectorArray dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_vector_array.add_xyz(x, y, z)
        assert _("Invalid") in str(e.value)
        mock_object.AddXYZ.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value", [("Size", "size", 5), ("Size", "size", 3)]
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_vector_array: VectorArray, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of VectorArray.

        Args:
            mock_vector_array: Instance of VectorArray.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_vector_array, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize("index, size", [(1, 3), (2, 4)])
    def test_x(self, mock_vector_array: VectorArray, mock_object, index, size):
        """
        Test x method of VectorArray.
        """
        mock_object.Size = size
        mock_vector_array.x(index)
        mock_object.X.assert_called_once_with(index)

    @pytest.mark.parametrize("index, size", [("1", 3), (True, 3)])
    def test_x_invalid_type(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test x method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(TypeError) as e:
            mock_vector_array.x(index)
        assert _("Invalid") in str(e.value)
        mock_object.X.assert_not_called()

    @pytest.mark.parametrize("index, size", [(-1, 3), (4, 4), (4, 3)])
    def test_x_invalid_index(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test x method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(IndexError) as e:
            mock_vector_array.x(index)
        assert _("Invalid") in str(e.value)
        mock_object.X.assert_not_called()

    @pytest.mark.parametrize("index, size", [(1, 3), (2, 4)])
    def test_y(self, mock_vector_array: VectorArray, mock_object, index, size):
        """
        Test y method of VectorArray.
        """
        mock_object.Size = size
        mock_vector_array.y(index)
        mock_object.Y.assert_called_once_with(index)

    @pytest.mark.parametrize("index, size", [("1", 3), (True, 3)])
    def test_y_invalid_type(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test y method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(TypeError) as e:
            mock_vector_array.y(index)
        assert _("Invalid") in str(e.value)
        mock_object.Y.assert_not_called()

    @pytest.mark.parametrize("index, size", [(-1, 3), (4, 4), (4, 3)])
    def test_y_invalid_index(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test y method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(IndexError) as e:
            mock_vector_array.y(index)
        assert _("Invalid") in str(e.value)
        mock_object.Y.assert_not_called()

    @pytest.mark.parametrize("index, size", [(1, 3), (2, 4)])
    def test_z(self, mock_vector_array: VectorArray, mock_object, index, size):
        """
        Test z method of VectorArray.
        """
        mock_object.Size = size
        mock_vector_array.z(index)
        mock_object.Z.assert_called_once_with(index)

    @pytest.mark.parametrize("index, size", [("1", 3), (True, 3)])
    def test_z_invalid_type(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test z method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(TypeError) as e:
            mock_vector_array.z(index)
        assert _("Invalid") in str(e.value)
        mock_object.Z.assert_not_called()

    @pytest.mark.parametrize("index, size", [(-1, 3), (4, 4), (4, 3)])
    def test_z_invalid_index(self, mock_vector_array: VectorArray, mock_object, index, size, _):
        """
        Test z method of VectorArray.
        """
        mock_object.Size = size
        with pytest.raises(IndexError) as e:
            mock_vector_array.z(index)
        assert _("Invalid") in str(e.value)
        mock_object.Z.assert_not_called()
