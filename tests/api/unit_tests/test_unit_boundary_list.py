# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for BoundaryList Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import BoundaryList


@pytest.mark.unit
class TestUnitBoundaryList:
    """
    Test suite for the BoundaryList class.
    """

    @pytest.fixture
    def mock_boundary_list(self, mock_object) -> BoundaryList:
        """
        Fixture to create a mock instance of BoundaryList.
        Args:
            mock_object: Mock object for the BoundaryList dependency.
        Returns:
            BoundaryList: An instance of BoundaryList with the mock object.
        """
        return BoundaryList(mock_object)

    @pytest.mark.parametrize("value", ["test", "value", "string"])
    def test_select_from_string(self, mock_boundary_list: BoundaryList, mock_object, value):
        """
        Test select_from_string method of BoundaryList.
        """
        mock_boundary_list.select_from_string(value)
        mock_object.SelectFromString.assert_called_once_with(value)

    @pytest.mark.parametrize("value", [False, 1])
    def test_select_from_string_invalid(
        self, mock_boundary_list: BoundaryList, mock_object, value, _
    ):
        """
        Test select_from_string method of BoundaryList with invalid values.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_list.select_from_string(value)
        assert _("Invalid") in str(e.value)
        mock_object.SelectFromString.assert_not_called()

    @pytest.mark.parametrize("value", ["test", "value", "string"])
    def test_convert_to_string(self, mock_boundary_list: BoundaryList, mock_object, value):
        """
        Test convert_to_string method of BoundaryList.
        """
        mock_object.ConvertToString = value
        result = mock_boundary_list.convert_to_string()
        assert isinstance(result, str)
        assert result == value

    @pytest.mark.parametrize("index", [0, 3, 7, 1])
    def test_entity(self, mock_boundary_list, mock_object, index):
        """
        Test entity method of BoundaryList.
        """
        mock_object.Entity.return_value = BoundaryList(mock_object)
        mock_object.Size = 10
        result = mock_boundary_list.entity(index)
        assert isinstance(result, BoundaryList)
        mock_object.Entity.assert_called_once()

    @pytest.mark.parametrize("index", [True, "5"])
    def test_entity_invalid(self, mock_boundary_list, mock_object, index, _):
        """
        Test entity method of BoundaryList.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_list.entity(index)
        assert _("Invalid") in str(e.value)
        mock_object.Entity.assert_not_called()

    @pytest.mark.parametrize("index", [-1, 5])
    def test_entity_invalid_index(self, mock_boundary_list, mock_object, index, _):
        """
        Test entity method of BoundaryList.
        """
        mock_object.Size = 5
        with pytest.raises(IndexError) as e:
            mock_boundary_list.entity(index)
        assert _("Invalid") in str(e.value)
        mock_object.Entity.assert_not_called()

    @pytest.mark.parametrize("index", [0, 3, 7, 1])
    def test_cad_entity(self, mock_boundary_list, mock_object, index):
        """
        Test cad_entity method of BoundaryList.
        """
        mock_object.CadEntity.return_value = BoundaryList(mock_object)
        mock_object.SizeCad = 10
        result = mock_boundary_list.cad_entity(index)
        assert isinstance(result, BoundaryList)
        mock_object.CadEntity.assert_called_once()

    @pytest.mark.parametrize("index", [True, "5"])
    def test_cad_entity_invalid(self, mock_boundary_list, mock_object, index, _):
        """
        Test cad_entity method of BoundaryList with invalid values.
        """
        with pytest.raises(TypeError) as e:
            mock_boundary_list.cad_entity(index)
        assert _("Invalid") in str(e.value)
        mock_object.CadEntity.assert_not_called()

    @pytest.mark.parametrize("index", [-1, 5])
    def test_cad_entity_invalid_index(self, mock_boundary_list, mock_object, index, _):
        """
        Test cad_entity method of BoundaryList with invalid values.
        """
        mock_object.SizeCad = 5
        with pytest.raises(IndexError) as e:
            mock_boundary_list.cad_entity(index)
        assert _("Invalid") in str(e.value)
        mock_object.CadEntity.assert_not_called()

    @pytest.mark.parametrize("size", [1, 2, 3])
    def test_size(self, mock_boundary_list, mock_object, size):
        """
        Test size method of BoundaryList.
        """
        mock_object.Size = size
        result = mock_boundary_list.size
        assert isinstance(result, int)
        assert result == size

    @pytest.mark.parametrize("size", [1, 2, 3])
    def test_size_cad(self, mock_boundary_list, mock_object, size):
        """
        Test size_cad method of BoundaryList with invalid values.
        """
        mock_object.SizeCad = size
        result = mock_boundary_list.size_cad
        assert isinstance(result, int)
        assert result == size

    @pytest.mark.parametrize(
        "pascal_name, property_name, size_prop",
        [("Entity", "entity", "Size"), ("CadEntity", "cad_entity", "SizeCad")],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_boundary_list: BoundaryList, mock_object, pascal_name, property_name, size_prop
    ):
        """
        Test the return value of the function is None.
        """
        setattr(mock_object, size_prop, 10)
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_boundary_list, property_name)(1)
        assert result is None
