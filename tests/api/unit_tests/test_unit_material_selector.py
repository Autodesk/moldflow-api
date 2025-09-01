# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for MaterialSelector Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import MaterialSelector
from moldflow.common import MaterialDatabaseType, MaterialIndex


@pytest.mark.unit
class TestUnitMaterialSelector:
    """
    Test suite for the MaterialSelector class.
    """

    @pytest.fixture
    def mock_material_selector(self, mock_object) -> MaterialSelector:
        """
        Fixture to create a mock instance of MaterialSelector.
        """
        return MaterialSelector(mock_object)

    @pytest.mark.parametrize(
        "expected, filetype, expect_enum",
        [
            (True, "System", "System"),
            (True, MaterialDatabaseType.SYSTEM, "System"),
            (True, "System", "System"),
            (False, "", ""),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_select(self, mock_material_selector, mock_object, expected, filetype, expect_enum):
        """
        Test the select method of MaterialSelector.
        """
        filename = "test_file.mdb"
        index = 1
        material = 0

        mock_object.Select.return_value = expected
        result = mock_material_selector.select(filename, filetype, index, material)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.Select.assert_called_once_with(filename, expect_enum, index, material)

    @pytest.mark.parametrize(
        "filename, filetype, index, material",
        [
            (None, "System", 1, 0),
            ("test_file.mdb", None, 1, 0),
            ("test_file.mdb", "System", None, 0),
            ("test_file.mdb", "System", 1, None),
            (True, "System", 1, 0),
            ("test_file.mdb", True, 1, 0),
            ("test_file.mdb", "System", True, 0),
            ("test_file.mdb", "System", 1, True),
            (1, "System", 1, 0),
            ("test_file.mdb", 1, 1, 0),
            (1.0, "System", 1, 0),
            ("test_file.mdb", 1.0, 1, 0),
            ("test_file.mdb", "System", 1.0, 0),
            ("test_file.mdb", "System", 1, 1.0),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_select_invalid(
        self, mock_material_selector, mock_object, filename, filetype, index, material, _
    ):
        """
        Test the select method of MaterialSelector with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_material_selector.select(filename, filetype, index, material)
        assert _("Invalid") in str(e.value)
        mock_object.Select.assert_not_called()

    @pytest.mark.parametrize("index, material", [(-1, 0), (0, -1), (0, 2)])
    def test_select_invalid_num(self, mock_material_selector, mock_object, index, material, _):
        """
        Test the select method of MaterialSelector with negative index and material.
        """
        filename = "test_file.mdb"
        filetype = "System"
        with pytest.raises(ValueError) as e:
            mock_material_selector.select(filename, filetype, index, material)
        assert _("Invalid") in str(e.value)
        mock_object.Select.assert_not_called()

    @pytest.mark.parametrize(
        "expected, enum, expected_call",
        [(True, MaterialIndex.FIRST, 0), (False, MaterialIndex.SECOND, 1)],
    )
    # pylint: disable-next=R0913, R0917
    def test_select_via_dialog(
        self, mock_material_selector, mock_object, expected, enum, expected_call
    ):
        """
        Test the select_via_dialog method of MaterialSelector.
        """
        client_process_id = 1234

        mock_object.SelectViaDialog.return_value = expected
        result = mock_material_selector.select_via_dialog(enum, client_process_id)
        assert isinstance(result, bool)
        assert result is expected
        mock_object.SelectViaDialog.assert_called_once_with(expected_call, client_process_id)

    @pytest.mark.parametrize(
        "material, client_id",
        [
            (None, 1234),
            (0, None),
            (True, 1234),
            (0, True),
            (1.0, 1234),
            (0, 1.0),
            ("test", 1234),
            (0, "test"),
        ],
    )
    def test_select_via_dialog_invalid(
        self, mock_material_selector, mock_object, material, client_id, _
    ):
        """
        Test the select_via_dialog method of MaterialSelector with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_material_selector.select_via_dialog(material, client_id)
        assert _("Invalid") in str(e.value)
        mock_object.SelectViaDialog.assert_not_called()

    @pytest.mark.parametrize("material", [2, -1, 3])
    def test_select_via_dialog_invalid_range(
        self, mock_material_selector, mock_object, material, _
    ):
        """
        Test the select_via_dialog method of MaterialSelector with invalid range.
        """
        client_process_id = 1234

        with pytest.raises(ValueError) as e:
            mock_material_selector.select_via_dialog(material, client_process_id)
        assert _("Invalid") in str(e.value)
        mock_object.SelectViaDialog.assert_not_called()

    @pytest.mark.parametrize(
        "expected, enum, expected_call",
        [(True, MaterialIndex.FIRST, 0), (False, MaterialIndex.SECOND, 1)],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_material_file(
        self, mock_material_selector, mock_object, expected, enum, expected_call
    ):
        """
        Test the get_material_file method of MaterialSelector.
        """
        mock_object.GetMaterialFile.return_value = expected
        result = mock_material_selector.get_material_file(enum)
        assert isinstance(result, bool)
        assert result == expected
        mock_object.GetMaterialFile.assert_called_once_with(expected_call)

    @pytest.mark.parametrize("material", [None, True, 1.0, "test"])
    def test_get_material_file_invalid(self, mock_material_selector, mock_object, material, _):
        """
        Test the get_material_file method of MaterialSelector with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_material_selector.get_material_file(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialFile.assert_not_called()

    @pytest.mark.parametrize("material", [-1, 2])
    def test_get_material_file_invalid_range(
        self, mock_material_selector, mock_object, material, _
    ):
        """
        Test the get_material_file method of MaterialSelector with invalid range.
        """
        with pytest.raises(ValueError) as e:
            mock_material_selector.get_material_file(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialFile.assert_not_called()

    @pytest.mark.parametrize(
        "expected, enum, expected_call",
        [("Return", MaterialIndex.FIRST, 0), ("Return", MaterialIndex.SECOND, 1)],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_material_file_type(
        self, mock_material_selector, mock_object, expected, enum, expected_call
    ):
        """
        Test the get_material_file_type method of MaterialSelector.
        """

        mock_object.GetMaterialFileType.return_value = expected
        result = mock_material_selector.get_material_file_type(enum)
        assert isinstance(result, str)
        assert result == expected
        mock_object.GetMaterialFileType.assert_called_once_with(expected_call)

    @pytest.mark.parametrize("material", [None, True, 1.0, "test"])
    def test_get_material_file_type_invalid(self, mock_material_selector, mock_object, material, _):
        """
        Test the get_material_file_type method of MaterialSelector with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_material_selector.get_material_file_type(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialFileType.assert_not_called()

    @pytest.mark.parametrize("material", [-1, 2])
    def test_get_material_file_type_invalid_range(
        self, mock_material_selector, mock_object, material, _
    ):
        """
        Test the get_material_file_type method of MaterialSelector with invalid range.
        """
        with pytest.raises(ValueError) as e:
            mock_material_selector.get_material_file_type(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialFileType.assert_not_called()

    @pytest.mark.parametrize(
        "expected, enum, expected_call", [(1, 0, 0), (2, MaterialIndex.SECOND, 1)]
    )
    # pylint: disable-next=R0913, R0917
    def test_get_material_index(
        self, mock_material_selector, mock_object, expected, enum, expected_call
    ):
        """
        Test the get_material_index method of MaterialSelector.
        """

        mock_object.GetMaterialIndex.return_value = expected
        result = mock_material_selector.get_material_index(enum)
        assert isinstance(result, int)
        assert result == expected
        mock_object.GetMaterialIndex.assert_called_once_with(expected_call)

    @pytest.mark.parametrize("material", [None, True, 1.0, "test"])
    def test_get_material_index_invalid(self, mock_material_selector, mock_object, material, _):
        """
        Test the get_material_index method of MaterialSelector with invalid parameters.
        """
        with pytest.raises(TypeError) as e:
            mock_material_selector.get_material_index(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialIndex.assert_not_called()

    @pytest.mark.parametrize("material", [-1, 2])
    def test_get_material_index_invalid_range(
        self, mock_material_selector, mock_object, material, _
    ):
        """
        Test the get_material_index method of MaterialSelector with invalid range.
        """
        with pytest.raises(ValueError) as e:
            mock_material_selector.get_material_index(material)
        assert _("Invalid") in str(e.value)
        mock_object.GetMaterialIndex.assert_not_called()
