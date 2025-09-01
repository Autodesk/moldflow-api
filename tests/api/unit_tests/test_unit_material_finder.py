# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for MaterialFinder Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock, patch
from win32com.client import VARIANT
import pythoncom
import pytest
from moldflow import MaterialFinder, MaterialDatabase, MaterialDatabaseType, Property
from tests.api.unit_tests.conftest import VALID_MOCK


@pytest.mark.unit
class TestUnitMaterialFinder:
    """
    Unit Test suite for the MaterialFinder class.
    """

    @pytest.fixture
    def mock_material_finder(self, mock_object) -> MaterialFinder:
        """
        Fixture to create a mock instance of MaterialFinder.

        Args:
            mock_object: Mock object to replicate MaterialFinder instance from COM.

        Returns:
            MaterialFinder: An instance of MaterialFinder with mock_object.
        """
        return MaterialFinder(mock_object)

    @pytest.mark.parametrize(
        "material_database, "
        "material_database_type, "
        "material_database_value, "
        "material_database_type_value",
        [
            (
                material_database,
                material_database_type,
                material_database.value,
                material_database_type.value,
            )
            for material_database in MaterialDatabase
            for material_database_type in MaterialDatabaseType
        ]
        + [
            (
                material_database.value,
                material_database_type.value,
                material_database.value,
                material_database_type.value,
            )
            for material_database in MaterialDatabase
            for material_database_type in MaterialDatabaseType
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_data_domain_valid_values(
        self,
        mock_material_finder: MaterialFinder,
        material_database,
        material_database_type,
        material_database_value,
        material_database_type_value,
    ):
        """
        Test set_data_domain method of MaterialFinder with valid values.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database: Material database to set.
            material_database_type: Type of Material Database to set.
            material_database_value: Expected material database value.
            material_database_type_value: Expected material database type value.

        Results:
            Asserts the SetDataDomain method of MaterialFinder is called with the expected values.
        """
        mock_material_finder.set_data_domain(material_database, material_database_type)
        mock_material_finder.material_finder.SetDataDomain.assert_called_once_with(
            material_database_value, material_database_type_value
        )

    @pytest.mark.parametrize(
        "material_database, material_database_type",
        [
            ("20010", "System"),
            ("20010", MaterialDatabaseType.USER),
            (MaterialDatabaseType.SYSTEM, MaterialDatabaseType.SYSTEM),
        ],
    )
    def test_set_data_domain_invalid_material_database(
        self,
        mock_material_finder: MaterialFinder,
        mock_object,
        material_database,
        material_database_type,
        _,
    ):
        """
        Test set_data_domain method of MaterialFinder with invalid material_database values.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database: Material database to set.
            material_database_type: Type of Material Database to set.

        Results:
            Asserts the SetDataDomain method of MaterialFinder is not called for the invalid values.
            Asserts a TypeError.
        """
        with pytest.raises(TypeError) as e:
            mock_material_finder.set_data_domain(material_database, material_database_type)
        assert _("Invalid") in str(e.value)
        mock_object.SetDataDomain.assert_not_called()

    @pytest.mark.parametrize(
        "material_database, material_database_type",
        [
            (20010, 123),
            (MaterialDatabase.COOLANT, 123),
            (MaterialDatabase.COOLANT, MaterialDatabase.COOLANT),
        ],
    )
    def test_set_data_domain_invalid_material_database_type(
        self,
        mock_material_finder: MaterialFinder,
        mock_object,
        material_database,
        material_database_type,
        _,
    ):
        """
        Test set_data_domain method of MaterialFinder with invalid material_database_type values.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database: Material database to set.
            material_database_type: Type of Material Database to set.

        Results:
            Asserts the SetDataDomain method of MaterialFinder is not called for the invalid values.
            Asserts a TypeError.
        """
        with pytest.raises(TypeError) as e:
            mock_material_finder.set_data_domain(material_database, material_database_type)
        assert _("Invalid") in str(e.value)
        mock_object.SetDataDomain.assert_not_called()

    @pytest.mark.parametrize(
        "material_database, material_database_type, expected_type",
        [
            (20010, "asd", "asd"),
            (-1, MaterialDatabaseType.SYSTEM, MaterialDatabaseType.SYSTEM.value),
            (99999, MaterialDatabaseType.USER, MaterialDatabaseType.USER.value),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_data_domain_invalid_enum(
        self,
        mock_material_finder: MaterialFinder,
        mock_object,
        material_database,
        material_database_type,
        expected_type,
        _,
        caplog,
    ):
        """
        Test set_data_domain method of MaterialFinder with edge cases.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database: Material database to set.
            material_database_type: Type of Material Database to set.

        Results:
            Asserts the SetDataDomain method of MaterialFinder is not called for the edge cases.
            Asserts a ValueError.
        """
        mock_material_finder.set_data_domain(material_database, material_database_type)
        assert _("this may cause function call to fail") in caplog.text
        mock_object.SetDataDomain.assert_called_once_with(material_database, expected_type)

    @pytest.mark.parametrize(
        "material_database, material_database_type",
        [
            (None, "System"),
            (None, MaterialDatabaseType.USER),
            (MaterialDatabase.COOLANT, None),
            (20010, None),
        ],
    )
    def test_set_data_domain_edge_case_none(
        self,
        mock_material_finder: MaterialFinder,
        mock_object,
        material_database,
        material_database_type,
        _,
    ):
        """
        Test set_data_domain method of MaterialFinder with None type values.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database: Material database to set.
            material_database_type: Type of Material Database to set.

        Results:
            Asserts the SetDataDomain method of MaterialFinder is not called for the edge case None.
            Asserts a TypeError.
        """
        with pytest.raises(TypeError) as e:
            mock_material_finder.set_data_domain(material_database, material_database_type)
        assert _("Invalid") in str(e.value)
        mock_object.SetDataDomain.assert_not_called()

    def test_get_first_material(self, mock_material_finder):
        """
        Test get_first_material method of MaterialFinder.

        Args:
            mock_material_finder: Instance of MaterialFinder.

        Results:
            Asserts the Property object is returned.
        """
        mock_material_finder.material_finder.GetFirstMaterial = Mock()
        result = mock_material_finder.get_first_material()
        assert isinstance(result, Property)
        assert result.prop == mock_material_finder.material_finder.GetFirstMaterial

    def test_get_next_material(self, mock_material_finder):
        """
        Test get_next_material method of MaterialFinder.

        Args:
            mock_material_finder: Instance of MaterialFinder.

        Results:
            Asserts the next Property object is returned.
        """
        mock_current_material = Mock(spec=Property)
        mock_current_material.prop = Mock()
        mock_next_material = Mock()
        mock_material_finder.material_finder.GetNextMaterial.return_value = mock_next_material
        result = mock_material_finder.get_next_material(mock_current_material)
        assert isinstance(result, Property)
        assert result.prop == mock_next_material
        mock_material_finder.material_finder.GetNextMaterial.assert_called_once_with(
            mock_current_material.prop
        )

    def test_get_next_material_none(self, mock_material_finder: MaterialFinder, _):
        """
        Test get_next_material method of MaterialFinder with None material.

        Args:
            mock_material_finder: Instance of MaterialFinder.

        Results:
            Asserts GetNextMaterial method of MaterialFinder is not called for None material value.
            Asserts a ValueError.
        """
        with patch(
            "moldflow.helper.variant_null_idispatch",
            return_value=VARIANT(pythoncom.VT_DISPATCH, None),
        ) as mock_func:
            mock_current_material = None
            mock_next_material = Mock()
            mock_material_finder.material_finder.GetNextMaterial.return_value = mock_next_material
            result = mock_material_finder.get_next_material(mock_current_material)
            assert isinstance(result, Property)
            assert result.prop == mock_next_material
            mock_material_finder.material_finder.GetNextMaterial.assert_called_once_with(
                mock_func()
            )

    @pytest.mark.parametrize("material_database_type", ["System", "User"])
    def test_file_type(self, mock_material_finder: MaterialFinder, material_database_type):
        """
        Test file_type attribute of MaterialFinder.

        Args:
            mock_material_finder: Instance of MaterialFinder.
            material_database_type: Material Database Type.

        Results:
            Asserts the file_type attribute correctly returns.
        """
        mock_material_finder.material_finder.FileType = material_database_type
        result = mock_material_finder.file_type
        assert isinstance(result, str)
        assert result == material_database_type

    @pytest.mark.parametrize(
        "pascal_name, property_name", [("GetFirstMaterial", "get_first_material")]
    )
    def test_function_no_arg_return_none(
        self, mock_material_finder: MaterialFinder, mock_object, pascal_name, property_name
    ):
        """
        Test the return value of the function is None.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_material_finder, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("GetNextMaterial", "get_next_material", (VALID_MOCK.PROP,))],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_material_finder: MaterialFinder, mock_object, pascal_name, property_name, args
    ):
        """
        Test the return value of the function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_material_finder, property_name)(*args)
        assert result is None
