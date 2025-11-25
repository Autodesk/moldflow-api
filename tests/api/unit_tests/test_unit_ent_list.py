# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for EntList Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import EntList, Predicate


@pytest.mark.unit
@pytest.mark.ent_list
class TestUnitEntList:
    """
    Test suite for the EntList class.
    """

    @pytest.fixture
    def mock_ent_list(self, mock_object) -> EntList:
        """
        Fixture to create a mock instance of EntList.
        Args:
            mock_object: Mock object for the EntList dependency.
        Returns:
            EntList: An instance of EntList with the mock object.
        """
        return EntList(mock_object)

    def test_entity(self, mock_ent_list, mock_object):
        """
        Test the entity method of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
        """
        mock_ent_list_return = Mock()
        mock_object.Entity.return_value = mock_ent_list_return
        mock_object.Size = 1
        result = mock_ent_list.entity(0)
        assert isinstance(result, EntList)
        assert result.ent_list == mock_ent_list_return
        mock_object.Entity.assert_called_once_with(0)

    @pytest.mark.parametrize("index, size", [(-1, 1), (1, 0), (10, 5)])
    def test_entity_invalid_index(self, mock_ent_list, mock_object, index, size, _):
        """
        Test the entity method of EntList with invalid index.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
        """
        mock_object.Size = size
        with pytest.raises(IndexError) as e:
            mock_ent_list.entity(index)
        assert _("Invalid") in str(e.value)

    def test_entity_none(self, mock_ent_list, mock_object, _):
        """
        Test the entity method of EntList with invalid index.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
        """
        mock_object.Size = 0
        with pytest.raises(TypeError) as e:
            mock_ent_list.entity(None)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("entity_string", ["", "test", "string"])
    def test_select_from_string(self, mock_ent_list, mock_object, entity_string):
        """
        Test the select_from_string method of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
            entity_string: String to test the method with.
        """
        mock_ent_list.select_from_string(entity_string)
        mock_object.SelectFromString.assert_called_once_with(entity_string)

    @pytest.mark.parametrize("entity_string", [1, 2, None, True, 10.0])
    def test_select_from_string_invalid(self, mock_ent_list, entity_string, _):
        """
        Test the select_from_string method of EntList with invalid input.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
        """
        with pytest.raises(TypeError) as e:
            mock_ent_list.select_from_string(entity_string)
        assert _("Invalid") in str(e.value)

    def test_select_from_predicate(self, mock_ent_list, mock_object):
        """
        Test the select_from_predicate method of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
            mock_predicate: Mock object for the Predicate dependency.
        """
        mock_predicate = Mock(spec=Predicate)
        mock_predicate.predicate = Mock()
        mock_ent_list.select_from_predicate(mock_predicate)
        mock_object.SelectFromPredicate.assert_called_once_with(mock_predicate.predicate)

    @pytest.mark.parametrize("predicate", [1, 2, True, 10.0])
    def test_select_from_predicate_invalid(self, mock_ent_list, predicate, _):
        """
        Test the select_from_predicate method of EntList with invalid input.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
        """
        with pytest.raises(TypeError) as e:
            mock_ent_list.select_from_predicate(predicate)
        assert _("Invalid") in str(e.value)

    def test_convert_to_string(self, mock_ent_list, mock_object):
        """
        Test the convert_to_string method of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
        """
        mock_object.ConvertToString = "test"
        result = mock_ent_list.convert_to_string()
        assert isinstance(result, str)
        assert result == "test"

    def test_select_from_saved_list(self, mock_ent_list, mock_object):
        """
        Test the select_from_saved_list method of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
        """
        mock_ent_list.select_from_saved_list("test")
        mock_object.SelectFromSavedList.assert_called_once_with("test")

    @pytest.mark.parametrize("list_name", [1, 2, None, True, 10.0])
    def test_select_from_saved_list_invalid(self, mock_ent_list, list_name, _):
        """
        Test the select_from_saved_list method of EntList with invalid input.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
        """
        with pytest.raises(TypeError) as e:
            mock_ent_list.select_from_saved_list(list_name)
        assert _("Invalid") in str(e.value)

    def test_size(self, mock_ent_list, mock_object):
        """
        Test the size property of EntList.
        Args:
            mock_ent_list: Instance of EntList with a mock object.
            mock_object: Mock object for the EntList dependency.
        """
        mock_object.Size = 5
        result = mock_ent_list.size
        assert isinstance(result, int)
        assert result == 5
