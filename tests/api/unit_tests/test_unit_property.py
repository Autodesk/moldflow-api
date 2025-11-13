# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for Property Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import Property, DoubleArray, StringArray
from tests.api.unit_tests.conftest import VALID_MOCK
from tests.conftest import POSITIVE_INT, pad_and_zip, INVALID_INT, INVALID_STR, VALID_STR


@pytest.mark.unit
@pytest.mark.prop
class TestUnitProperty:
    """
    Unit Test suite for the Property class.
    """

    @pytest.fixture
    def mock_property(self, mock_object) -> Property:
        """
        Fixture to create a mock instance of Property.

        Args:
            mock_object: Mock object to replicate Property instance from COM.

        Returns:
            Property: An instance of Property with mock_object.
        """
        return Property(mock_object)

    @pytest.mark.parametrize("field_id", [1, 2, 3])
    def test_delete_field(self, mock_property: Property, mock_object, field_id):
        """
        Test delete_field method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to delete.

        Results:
            Asserts the DeleteField method of Property is called with the expected field ID.
        """
        mock_object.DeleteField.return_value = True
        result = mock_property.delete_field(field_id)
        assert isinstance(result, bool)
        assert result
        mock_object.DeleteField.assert_called_once_with(field_id)

    @pytest.mark.parametrize("field_id", [1, 2, 3])
    def test_get_first_field(self, mock_property: Property, mock_object, field_id):
        """
        Test get_first_field method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.

        Results:
            Asserts the get_first_field method returns the expected first field ID.
            Asserts the GetFirstField method of Property is called.
        """
        mock_object.GetFirstField = field_id
        result = mock_property.get_first_field()
        assert isinstance(result, int)
        assert result == field_id

    @pytest.mark.parametrize("field_id", [1, 2, 3])
    def test_get_next_field(self, mock_property: Property, mock_object, field_id):
        """
        Test get_next_field method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to get the next field.

        Results:
            Asserts the get_next_field method returns the expected next field ID.
            Asserts the GetNextField method of Property is called with the expected field ID.
        """
        mock_object.GetNextField.return_value = field_id + 1
        result = mock_property.get_next_field(field_id)
        assert isinstance(result, int)
        assert result == field_id + 1
        mock_object.GetNextField.assert_called_once_with(field_id)

    @pytest.mark.parametrize("field_id, confidential", [(1, False), (2, False), (3, True)])
    def test_is_field_hidden(self, mock_property: Property, mock_object, field_id, confidential):
        """
        Test is_field_hidden method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to check if hidden.
            confidential: Expected confidentiality status.

        Results:
            Asserts the is_field_hidden method returns the expected confidentiality status.
            Asserts the IsFieldHidden method of Property is called with the expected field ID.
        """
        mock_object.IsFieldHidden.return_value = confidential
        result = mock_property.is_field_hidden(field_id)
        assert isinstance(result, bool)
        assert result == confidential
        mock_object.IsFieldHidden.assert_called_once_with(field_id)

    @pytest.mark.parametrize("field_id, writable", [(1, False), (2, False), (3, True)])
    def test_is_field_writable(self, mock_property: Property, mock_object, field_id, writable):
        """
        Test is_field_writable method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to check if writable.
            writable: Expected writable status.

        Results:
            Asserts the is_field_writable method returns the expected writable status.
            Asserts the IsFieldWritable method of Property is called with the expected field ID.
        """
        mock_object.IsFieldWritable.return_value = writable
        result = mock_property.is_field_writable(field_id)
        assert isinstance(result, bool)
        assert result == writable
        mock_object.IsFieldWritable.assert_called_once_with(field_id)

    @pytest.mark.parametrize("field_id, hidden", [(1, False), (2, False), (3, True)])
    def test_hide_field(self, mock_property: Property, mock_object, field_id, hidden):
        """
        Test hide_field method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to hide.
            hidden: Expected hidden status after hiding.

        Results:
            Asserts the HideField method of Property is called with the expected field ID.
        """
        mock_object.HideField.return_value = hidden
        result = mock_property.hide_field(field_id)
        assert isinstance(result, bool)
        assert result == hidden
        mock_object.HideField.assert_called_once_with(field_id)

    @pytest.mark.parametrize("prop_type", [1, 2, 3])
    def test_type(self, mock_property: Property, mock_object, prop_type):
        """
        Test type attribute of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            prop_type: Expected type of the property.

        Results:
            Asserts the Type attribute of Property returns the expected type.
        """
        mock_object.Type = prop_type
        result = mock_property.type
        assert isinstance(result, int)
        assert result == prop_type

    @pytest.mark.parametrize("field_id", [1, 2, 3])
    def test_id(self, mock_property: Property, mock_object, field_id):
        """
        Test id attribute of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Expected ID of the property.

        Results:
            Asserts the ID attribute of Property returns the expected ID.
        """
        mock_object.ID = field_id
        result = mock_property.id
        assert isinstance(result, int)
        assert result == field_id

    @pytest.mark.parametrize("name", ["Name1", "Name2", "Name3"])
    def test_name(self, mock_property: Property, mock_object, name):
        """
        Test name attribute of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            name: Expected name of the property.

        Results:
            Asserts the Name attribute of Property returns the expected name.
        """
        mock_object.Name = name
        result = mock_property.name
        assert isinstance(result, str)
        assert result == name

    @pytest.mark.parametrize("field_id", [1, 2, 3])
    def test_field_units(self, mock_property: Property, mock_object, field_id):
        """
        Test field_units method of Property.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.
            field_id: Field ID to get the units.

        Results:
            Asserts the field_units method returns the expected StringArray.
            Asserts the FieldUnits method of Property is called with the expected field ID.
        """
        mock_string_array = Mock()
        mock_object.FieldUnits.return_value = mock_string_array
        result = mock_property.field_units(field_id)
        assert isinstance(result, StringArray)
        assert result.string_array == mock_string_array
        mock_object.FieldUnits.assert_called_once_with(field_id)

    def test_field_units_none(self, mock_property: Property, mock_object, _):
        """
        Test field_units method of Property with None field_id.

        Args:
            mock_property: Instance of Property.
            mock_object: Mock object of Property.

        Results:
            Asserts the field_units method raises ValueError when field_id is None.
        """
        with pytest.raises(TypeError) as e:
            mock_property.field_units(None)
        assert _("Invalid") in str(e.value)
        mock_object.FieldUnits.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args", [("FieldUnits", "field_units", (POSITIVE_INT[0],))]
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_property: Property, mock_object, pascal_name, property_name, args
    ):
        """
        Test the return value of the function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_property, property_name)(*args)
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("GetFieldDescription", "get_field_description", (x,), (x,), str, y)
            for x, y in pad_and_zip(POSITIVE_INT, VALID_STR)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_get_function(
        self,
        mock_property: Property,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the return value of the get function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_property, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("GetFieldDescription", "get_field_description", (x,)) for x in INVALID_INT],
    )
    # pylint: disable=R0913, R0917
    def test_get_function_invalid_type(
        self, mock_property: Property, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the return value of the get function with invalid type.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_property, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("SetFieldDescription", "set_field_description", (x, y), (x, y))
            for x, y in pad_and_zip(POSITIVE_INT, VALID_STR)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_set_function(
        self, mock_property: Property, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the return value of the set function.
        """
        getattr(mock_property, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [
            ("SetFieldDescription", "set_field_description", (x, y))
            for x, y in pad_and_zip(INVALID_INT, VALID_STR)
        ]
        + [
            ("SetFieldDescription", "set_field_description", (x, y))
            for x, y in pad_and_zip(POSITIVE_INT, INVALID_STR)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_set_function_invalid_type(
        self, mock_property: Property, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the return value of the set function with invalid type.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_property, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        # pylint: disable-next=C0301
        "pascal_name, property_name, args, expected_args, return_type, expected_return, type_instance",
        [
            (
                "GetFieldValues",
                "get_field_values",
                (x,),
                (x,),
                DoubleArray,
                VALID_MOCK.DOUBLE_ARRAY,
                "double_array",
            )
            for x in POSITIVE_INT
        ],
    )
    # pylint: disable=R0913, R0917
    def test_get_function_return_class(
        self,
        mock_property: Property,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        expected_return,
        type_instance,
    ):
        """
        Test the return value of the get function is class.
        """
        return_value = getattr(expected_return, type_instance)
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_property, property_name)(*args)
        assert isinstance(result, return_type)
        assert getattr(result, type_instance) == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("GetFieldValues", "get_field_values", (x,), (x,)) for x in POSITIVE_INT],
    )
    # pylint: disable=R0913, R0917
    def test_get_function_return_none(
        self, mock_property: Property, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the return value of the get function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_property, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("SetFieldValues", "set_field_values", (x, y), (x, y.double_array))
            for x, y in pad_and_zip(POSITIVE_INT, VALID_MOCK.DOUBLE_ARRAY)
        ],
    )
    # pylint: disable=R0913, R0917
    def test_set_function_return_class(
        self, mock_property: Property, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the return value of the set function is class.
        """
        getattr(mock_property, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    # -------------------------------
    # Setter tests for `name` property
    # -------------------------------

    @pytest.mark.parametrize("prop_name", VALID_STR)
    def test_name_setter(self, mock_property: Property, mock_object, prop_name):
        """Test the setter of the `name` attribute."""
        # Act
        mock_property.name = prop_name

        # Assert
        assert mock_object.Name == prop_name
        assert mock_property.name == prop_name

    @pytest.mark.parametrize("prop_name", INVALID_STR)
    def test_name_setter_invalid_type(self, mock_property: Property, mock_object, prop_name, _):
        """Test the setter of the `name` attribute with invalid types."""
        with pytest.raises(TypeError) as e:
            mock_property.name = prop_name
        assert _("Invalid") in str(e.value)
        assert not hasattr(mock_object, "Name") or mock_object.Name != prop_name
