# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for Project Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import Project, ItemType, ImportUnitIndex


@pytest.mark.unit
class TestUnitProject:
    """
    Test suite for the Project class.
    """

    @pytest.fixture
    def mock_project(self, mock_object) -> Project:
        """
        Fixture to create a mock instance of Project.
        Args:
            mock_object: Mock object for the Project dependency.
        Returns:
            Project: An instance of Project with the mock object.
        """
        return Project(mock_object)

    @pytest.mark.parametrize("close", [True, False])
    def test_close(self, mock_project: Project, mock_object, close):
        """
        Test the close method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Close2.return_value = close
        result = mock_project.close()
        assert isinstance(result, bool)
        assert result == close
        mock_object.Close2.assert_called_once_with(True)
        if close:
            assert mock_project.project is None
        else:
            assert mock_project.project is not None

    @pytest.mark.parametrize("prompts", [True, False])
    def test_close_optional(self, mock_project: Project, mock_object, prompts):
        """
        Test the close method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Close2.return_value = True
        result = mock_project.close(prompts)
        assert isinstance(result, bool)
        assert result
        mock_object.Close2.assert_called_once_with(prompts)

    @pytest.mark.parametrize("prompts", [10, "True"])
    def test_close_invalid_type(self, mock_project: Project, mock_object, prompts, _):
        """
        Test the close method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.close(prompts)
        assert _("Invalid") in str(e.value)
        mock_object.Close2.assert_not_called()

    @pytest.mark.parametrize("save_all", [True, False])
    def test_save_all(self, mock_project: Project, mock_object, save_all):
        """
        Test the save_all method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.SaveAll = save_all
        result = mock_project.save_all()
        assert isinstance(result, bool)
        assert mock_project.save_all() == save_all

    @pytest.mark.parametrize("study_name", ["Study1", "Study2"])
    def test_new_study(self, mock_project: Project, mock_object, study_name):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.NewStudy.return_value = True
        result = mock_project.new_study(study_name)
        assert result
        mock_object.NewStudy.assert_called_once_with(study_name)

    @pytest.mark.parametrize("study_name", [True, 10])
    def test_new_study_invalid_type(self, mock_project: Project, mock_object, study_name, _):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.new_study(study_name)
        assert _("Invalid") in str(e.value)
        mock_object.NewStudy.assert_not_called()

    @pytest.mark.parametrize("folder_name", ["Folder1", "Folder2"])
    def test_new_folder(self, mock_project: Project, mock_object, folder_name):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.NewFolder.return_value = True
        result = mock_project.new_folder(folder_name)
        assert result
        mock_object.NewFolder.assert_called_once_with(folder_name)

    @pytest.mark.parametrize("folder_name", [True, 10])
    def test_new_folder_invalid_type(self, mock_project: Project, mock_object, folder_name, _):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.new_folder(folder_name)
        assert _("Invalid") in str(e.value)
        mock_object.NewFolder.assert_not_called()

    @pytest.mark.parametrize("folder_name", ["Folder1", "Folder2"])
    def test_select_folder(self, mock_project: Project, mock_object, folder_name):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.SelectFolder.return_value = True
        result = mock_project.select_folder(folder_name)
        assert result
        mock_object.SelectFolder.assert_called_once_with(folder_name)

    @pytest.mark.parametrize("folder_name", [True, 10])
    def test_select_folder_invalid_type(self, mock_project: Project, mock_object, folder_name, _):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.select_folder(folder_name)
        assert _("Invalid") in str(e.value)
        mock_object.SelectFolder.assert_not_called()

    @pytest.mark.parametrize("item_name", ["Item1", "Item2"])
    def test_attach(self, mock_project: Project, mock_object, item_name):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Attach.return_value = True
        result = mock_project.attach(item_name)
        assert result
        mock_object.Attach.assert_called_once_with(item_name)

    @pytest.mark.parametrize("item_name", [True, 10])
    def test_attach_invalid_type(self, mock_project: Project, mock_object, item_name, _):
        """
        Test the new_study method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.attach(item_name)
        assert _("Invalid") in str(e.value)
        mock_object.Attach.assert_not_called()

    @pytest.mark.parametrize("compact", [True, False])
    def test_compact(self, mock_project: Project, mock_object, compact):
        """
        Test the compact method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Compact = compact
        result = mock_project.compact()
        assert isinstance(result, bool)
        assert mock_project.compact() == compact

    @pytest.mark.parametrize(
        "file_name, selected, results", [("file1", True, True), ("file2", False, False)]
    )
    # pylint: disable-next=R0913, R0917
    def test_export(self, mock_project: Project, mock_object, file_name, selected, results):
        """
        Test the export method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Export3.return_value = True
        result = mock_project.export(file_name, selected, results)
        assert result
        mock_object.Export3.assert_called_once_with(file_name, selected, results, "", False, False)

    @pytest.mark.parametrize(
        "file_name, selected, results, criteria_file, restrict, skip_cad",
        [
            ("file1", True, True, True, True, True),
            ("file2", False, False, True, True, True),
            ("file1", True, True, False, True, True),
            ("file2", False, False, False, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_export_optional(
        self,
        mock_project: Project,
        mock_object,
        file_name,
        selected,
        results,
        criteria_file,
        restrict,
        skip_cad,
    ):
        """
        Test the export method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Export3.return_value = True
        result = mock_project.export(
            file_name, selected, results, criteria_file, restrict, skip_cad
        )
        assert result
        mock_object.Export3.assert_called_once_with(
            file_name, selected, results, "", False, skip_cad
        )

    @pytest.mark.parametrize(
        "file_name, selected, results, criteria_file, restrict, skip_cad",
        [
            (True, True, True, True, True, True),
            (10, False, False, True, True, False),
            ("file1", "True", True, True, True, True),
            ("file1", True, True, True, True, 1),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_export_invalid_type(
        self,
        mock_project: Project,
        mock_object,
        file_name,
        selected,
        results,
        criteria_file,
        restrict,
        skip_cad,
        _,
    ):
        """
        Test the export method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.export(file_name, selected, results, criteria_file, restrict, skip_cad)
        assert _("Invalid") in str(e.value)
        mock_object.Export3.assert_not_called()

    @pytest.mark.parametrize("file_name", ["file1", "file2"])
    def test_export_model(self, mock_project: Project, mock_object, file_name):
        """
        Test the export_model method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.ExportModel.return_value = True
        result = mock_project.export_model(file_name)
        assert result
        mock_object.ExportModel.assert_called_once_with(file_name)

    @pytest.mark.parametrize(
        "file_name, units, expected", [("file1", ImportUnitIndex.CM, 1), ("file2", 2, 2)]
    )
    # pylint: disable-next=R0913, R0917
    def test_export_model_with_units(
        self, mock_project: Project, mock_object, file_name, units, expected
    ):
        """
        Test the export_model method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.ExportModel2.return_value = True
        result = mock_project.export_model(file_name, units)
        assert result
        mock_object.ExportModel2.assert_called_once_with(file_name, expected)

    @pytest.mark.parametrize("file_name", [True, 10])
    def test_export_model_invalid_type(self, mock_project: Project, mock_object, file_name, _):
        """
        Test the export_model method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.export_model(file_name)
        assert _("Invalid") in str(e.value)
        mock_object.ExportModel.assert_not_called()
        mock_object.ExportModel2.assert_not_called()

    @pytest.mark.parametrize("study_name", ["Study1", "Study2"])
    def test_duplicate_study_by_name(self, mock_project: Project, mock_object, study_name):
        """
        Test the duplicate_study_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.DuplicateStudyByName3.return_value = True
        result = mock_project.duplicate_study_by_name(study_name)
        assert result
        mock_object.DuplicateStudyByName3.assert_called_once_with(study_name, False, 2)

    @pytest.mark.parametrize("study_name", [True, 10])
    def test_duplicate_study_by_name_invalid_type(
        self, mock_project: Project, mock_object, study_name, _
    ):
        """
        Test the duplicate_study_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.duplicate_study_by_name(study_name)
        assert _("Invalid") in str(e.value)
        mock_object.DuplicateStudyByName3.assert_not_called()

    @pytest.mark.parametrize(
        "item_name, item_type, expected",
        [
            ("Study1", ItemType.STUDY, "Study"),
            ("Report1", ItemType.REPORT, "Report"),
            ("Study1", "Study", "Study"),
            ("Report1", "Report", "Report"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_delete_item_by_name(
        self, mock_project: Project, mock_object, item_name, item_type, expected
    ):
        """
        Test the delete_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.DeleteItemByName.return_value = True
        result = mock_project.delete_item_by_name(item_name, item_type)
        assert result
        mock_object.DeleteItemByName.assert_called_once_with(item_name, expected)

    @pytest.mark.parametrize("item_name, item_type", [(True, ItemType.STUDY), (10, "Study")])
    def test_delete_item_by_name_invalid_type(
        self, mock_project: Project, mock_object, item_name, item_type, _
    ):
        """
        Test the delete_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.delete_item_by_name(item_name, item_type)
        assert _("Invalid") in str(e.value)
        mock_object.DeleteItemByName.assert_not_called()

    @pytest.mark.parametrize("item_name, item_type", [("Study1", "Type"), ("Report1", "repo")])
    # pylint: disable-next=R0913, R0917
    def test_delete_item_by_name_invalid_value(
        self, mock_project: Project, mock_object, item_name, item_type, _, caplog
    ):
        """
        Test the delete_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_project.delete_item_by_name(item_name, item_type)
        mock_object.DeleteItemByName.assert_called_once_with(item_name, item_type)
        assert _("this may cause function call to fail") in caplog.text

    @pytest.mark.parametrize(
        "old_name, item_type, new_name, expected",
        [
            ("OldName", ItemType.STUDY, "NewName", "Study"),
            ("OldName", "Study", "NewName", "Study"),
            ("OldName", ItemType.REPORT, "NewName", "Report"),
            ("OldName", "Report", "NewName", "Report"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_rename_item_by_name(
        self, mock_project: Project, mock_object, old_name, item_type, new_name, expected
    ):
        """
        Test the rename_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.RenameItemByName.return_value = True
        result = mock_project.rename_item_by_name(old_name, item_type, new_name)
        assert result
        mock_object.RenameItemByName.assert_called_once_with(old_name, expected, new_name)

    @pytest.mark.parametrize(
        "old_name, item_type, new_name",
        [(True, ItemType.STUDY, "NewName"), (10, "Study", "NewName")],
    )
    # pylint: disable-next=R0913, R0917
    def test_rename_item_by_name_invalid_type(
        self, mock_project: Project, mock_object, old_name, item_type, new_name, _
    ):
        """
        Test the rename_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.rename_item_by_name(old_name, item_type, new_name)
        assert _("Invalid") in str(e.value)
        mock_object.RenameItemByName.assert_not_called()

    @pytest.mark.parametrize(
        "old_name, item_type, new_name",
        [("OldName", "Type", "NewName"), ("OldName", "repo", "NewName")],
    )
    # pylint: disable-next=R0913, R0917
    def test_rename_item_by_name_invalid_value(
        self, mock_project: Project, mock_object, old_name, item_type, new_name, _, caplog
    ):
        """
        Test the rename_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_project.rename_item_by_name(old_name, item_type, new_name)
        assert _("this may cause function call to fail") in caplog.text
        mock_object.RenameItemByName.assert_called_once_with(old_name, item_type, new_name)

    @pytest.mark.parametrize(
        "item_name, item_type, expected",
        [
            ("Item1", ItemType.STUDY, "Study"),
            ("Item2", ItemType.REPORT, "Report"),
            ("Item1", "Study", "Study"),
            ("Item2", "Report", "Report"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_open_item_by_name(
        self, mock_project: Project, mock_object, item_name, item_type, expected
    ):
        """
        Test the open_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.OpenItemByName.return_value = True
        result = mock_project.open_item_by_name(item_name, item_type)
        assert result
        mock_object.OpenItemByName.assert_called_once_with(item_name, expected)

    @pytest.mark.parametrize("item_name, item_type", [(True, ItemType.STUDY), (10, "Study")])
    def test_open_item_by_name_invalid_type(
        self, mock_project: Project, mock_object, item_name, item_type, _
    ):
        """
        Test the open_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.open_item_by_name(item_name, item_type)
        assert _("Invalid") in str(e.value)
        mock_object.OpenItemByName.assert_not_called()

    @pytest.mark.parametrize("item_name, item_type", [("Item1", "Type"), ("Item2", "repo")])

    # pylint: disable-next=R0913, R0917
    def test_open_item_by_name_invalid_value(
        self, mock_project: Project, mock_object, item_name, item_type, _, caplog
    ):
        """
        Test the open_item_by_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_project.open_item_by_name(item_name, item_type)
        assert _("this may cause function call to fail") in caplog.text
        mock_object.OpenItemByName.assert_called_once_with(item_name, item_type)

    @pytest.mark.parametrize("item_index", [1, 10])
    # pylint: disable-next=R0913, R0917
    def test_open_item_by_index(self, mock_project: Project, mock_object, item_index):
        """
        Test the open_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.OpenItemByIndex.return_value = True
        result = mock_project.open_item_by_index(item_index)
        assert result
        mock_object.OpenItemByIndex.assert_called_once_with(item_index)

    @pytest.mark.parametrize("item_index", [(True), ("10")])
    def test_open_item_by_index_invalid_type(
        self, mock_project: Project, mock_object, item_index, _
    ):
        """
        Test the open_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.open_item_by_index(item_index)
        assert _("Invalid") in str(e.value)
        mock_object.OpenItemByIndex.assert_not_called()

    @pytest.mark.parametrize("item_index", [1, 2])
    # pylint: disable-next=R0913, R0917
    def test_open_item_by_index_invalid_value(
        self, mock_project: Project, mock_object, item_index, _
    ):
        """
        Test the open_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_project.open_item_by_index(item_index)
        mock_object.OpenItemByIndex.assert_called_once_with(item_index)

    @pytest.mark.parametrize("index, new_name", [(1, "NewName1"), (2, "NewName2")])
    def test_rename_item_by_index(self, mock_project: Project, mock_object, index, new_name):
        """
        Test the rename_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.RenameItemByIndex.return_value = True
        result = mock_project.rename_item_by_index(index, new_name)
        assert result
        mock_object.RenameItemByIndex.assert_called_once_with(index, new_name)

    @pytest.mark.parametrize("index, new_name", [(True, "NewName"), ("10", "NewName")])
    def test_rename_item_by_index_invalid_type(
        self, mock_project: Project, mock_object, index, new_name, _
    ):
        """
        Test the rename_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.rename_item_by_index(index, new_name)
        assert _("Invalid") in str(e.value)
        mock_object.RenameItemByIndex.assert_not_called()

    @pytest.mark.parametrize("index", [1, 2])
    def test_delete_item_by_index(self, mock_project: Project, mock_object, index):
        """
        Test the delete_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.DeleteItemByIndex.return_value = True
        result = mock_project.delete_item_by_index(index)
        assert result
        mock_object.DeleteItemByIndex.assert_called_once_with(index)

    @pytest.mark.parametrize("index", [True, "10"])
    def test_delete_item_by_index_invalid_type(self, mock_project: Project, mock_object, index, _):
        """
        Test the delete_item_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.delete_item_by_index(index)
        assert _("Invalid") in str(e.value)
        mock_object.DeleteItemByIndex.assert_not_called()

    @pytest.mark.parametrize(
        "item_name, item_type, expected, folder_name",
        [
            ("Item1", ItemType.STUDY, "Study", "Folder1"),
            ("Item2", ItemType.REPORT, "Report", "Folder2"),
            ("Item1", "Study", "Study", "Folder1"),
            ("Item2", "Report", "Report", "Folder2"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_move_item_to_folder(
        self, mock_project: Project, mock_object, item_name, item_type, expected, folder_name
    ):
        """
        Test the move_item_to_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.MoveItemToFolder.return_value = True
        result = mock_project.move_item_to_folder(item_name, item_type, folder_name)
        assert result
        mock_object.MoveItemToFolder.assert_called_once_with(item_name, expected, folder_name)

    @pytest.mark.parametrize(
        "item_name, item_type, folder_name",
        [(True, ItemType.STUDY, "Folder1"), (10, "Study", "Folder2")],
    )
    # pylint: disable-next=R0913, R0917
    def test_move_item_to_folder_invalid_type(
        self, mock_project: Project, mock_object, item_name, item_type, folder_name, _
    ):
        """
        Test the move_item_to_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.move_item_to_folder(item_name, item_type, folder_name)
        assert _("Invalid") in str(e.value)
        mock_object.MoveItemToFolder.assert_not_called()

    @pytest.mark.parametrize(
        "item_name, item_type, folder_name",
        [("Item1", "Type", "Folder1"), ("Item2", "repo", "Folder2")],
    )
    # pylint: disable-next=R0913, R0917
    def test_move_item_to_folder_invalid_value(
        self, mock_project: Project, mock_object, item_name, item_type, folder_name, _, caplog
    ):
        """
        Test the move_item_to_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_project.move_item_to_folder(item_name, item_type, folder_name)
        assert _("this may cause function call to fail") in caplog.text
        mock_object.MoveItemToFolder.assert_called_once_with(item_name, item_type, folder_name)

    @pytest.mark.parametrize("index", [1, 2])
    def test_duplicate_study_by_index(self, mock_project: Project, mock_object, index):
        """
        Test the duplicate_study_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.DuplicateStudyByIndex3.return_value = True
        result = mock_project.duplicate_study_by_index(index)
        assert result
        mock_object.DuplicateStudyByIndex3.assert_called_once_with(index, False, 2)

    @pytest.mark.parametrize("index", [True, "10"])
    def test_duplicate_study_by_index_invalid_type(
        self, mock_project: Project, mock_object, index, _
    ):
        """
        Test the duplicate_study_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.duplicate_study_by_index(index)
        assert _("Invalid") in str(e.value)
        mock_object.DuplicateStudyByIndex3.assert_not_called()

    def test_get_first_study_name(self, mock_project: Project, mock_object):
        """
        Test the get_first_study_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetFirstStudyName = "Test"
        result = mock_project.get_first_study_name()
        assert isinstance(result, str)
        assert result == "Test"

    def test_get_next_study_name(self, mock_project: Project, mock_object):
        """
        Test the get_next_study_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNextStudyName.return_value = "Test"
        result = mock_project.get_next_study_name("Test")
        assert isinstance(result, str)
        mock_object.GetNextStudyName.assert_called_once_with("Test")

    def test_get_next_study_name_invalid_type(self, mock_project: Project, mock_object, _):
        """
        Test the get_next_study_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.get_next_study_name(10)
        assert _("Invalid") in str(e.value)
        mock_object.GetNextStudyName.assert_not_called()

    def test_get_first_report_name(self, mock_project: Project, mock_object):
        """
        Test the get_first_report_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetFirstReportName = "Test"
        result = mock_project.get_first_report_name()
        assert isinstance(result, str)
        assert result == "Test"

    def test_get_next_report_name(self, mock_project: Project, mock_object):
        """
        Test the get_next_report_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNextReportName.return_value = "Test"
        result = mock_project.get_next_report_name("Test")
        assert isinstance(result, str)
        assert result == "Test"
        mock_object.GetNextReportName.assert_called_once_with("Test")

    def test_get_next_report_name_invalid_type(self, mock_project: Project, mock_object, _):
        """
        Test the get_next_report_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.get_next_report_name(10)
        assert _("Invalid") in str(e.value)
        mock_object.GetNextReportName.assert_not_called()

    def test_get_first_folder_name(self, mock_project: Project, mock_object):
        """
        Test the get_first_folder_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetFirstFolderName = "Test"
        result = mock_project.get_first_folder_name()
        assert isinstance(result, str)
        assert result == "Test"

    def test_get_next_folder_name(self, mock_project: Project, mock_object):
        """
        Test the get_next_folder_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNextFolderName.return_value = "Test"
        result = mock_project.get_next_folder_name("Test")
        assert isinstance(result, str)
        assert result == "Test"
        mock_object.GetNextFolderName.assert_called_once_with("Test")

    def test_get_next_folder_name_invalid_type(self, mock_project: Project, mock_object, _):
        """
        Test the get_next_folder_name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.get_next_folder_name(10)
        assert _("Invalid") in str(e.value)
        mock_object.GetNextFolderName.assert_not_called()

    @pytest.mark.parametrize(
        "from_name, to_name", [("FromName1", "ToName1"), ("FromName2", "ToName2")]
    )
    def test_copy_study_settings(self, mock_project: Project, mock_object, from_name, to_name):
        """
        Test the copy_study_settings method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.CopyStudySettings.return_value = True
        result = mock_project.copy_study_settings(from_name, to_name)
        assert result
        mock_object.CopyStudySettings.assert_called_once_with(from_name, to_name)

    @pytest.mark.parametrize("from_name, to_name", [(True, "ToName"), ("FromName", 10)])
    def test_copy_study_settings_invalid_type(
        self, mock_project: Project, mock_object, from_name, to_name, _
    ):
        """
        Test the copy_study_settings method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.copy_study_settings(from_name, to_name)
        assert _("Invalid") in str(e.value)
        mock_object.CopyStudySettings.assert_not_called()

    @pytest.mark.parametrize("items", [10, 20])
    def test_get_number_of_items(self, mock_project: Project, mock_object, items):
        """
        Test the get_number_of_items method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNumberOfItems = items
        result = mock_project.get_number_of_items()
        assert isinstance(result, int)
        assert result == items

    @pytest.mark.parametrize("index, number_of_items", [(1, 2), (2, 2)])
    def test_get_item_name_by_index(
        self, mock_project: Project, mock_object, index, number_of_items
    ):
        """
        Test the get_item_name_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNumberOfItems = number_of_items
        mock_object.GetItemNameByIndex.return_value = "Test"
        result = mock_project.get_item_name_by_index(index)
        assert isinstance(result, str)
        assert result == "Test"
        mock_object.GetItemNameByIndex.assert_called_once_with(index)

    @pytest.mark.parametrize("index", [True, "10"])
    def test_get_item_name_by_index_invalid_type(
        self, mock_project: Project, mock_object, index, _
    ):
        """
        Test the get_item_name_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.get_item_name_by_index(index)
        assert _("Invalid") in str(e.value)
        mock_object.GetItemNameByIndex.assert_not_called()

    @pytest.mark.parametrize("index, number_of_items", [(1, 0), (2, 1)])
    def test_get_item_name_by_index_out_of_range(
        self, mock_project: Project, mock_object, index, number_of_items, _
    ):
        """
        Test the get_item_name_by_index method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.GetNumberOfItems = number_of_items
        with pytest.raises(IndexError) as e:
            mock_project.get_item_name_by_index(index)
        assert _("Index") in str(e.value)
        mock_object.GetItemNameByIndex.assert_not_called()

    @pytest.mark.parametrize("study_name", ["Study1", "Study2"])
    def test_is_open(self, mock_project: Project, mock_object, study_name):
        """
        Test the is_open method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.IsOpen.return_value = True
        result = mock_project.is_open(study_name)
        assert result
        mock_object.IsOpen.assert_called_once_with(study_name)

    @pytest.mark.parametrize("study_name", [True, 10])
    def test_is_open_invalid_type(self, mock_project: Project, mock_object, study_name, _):
        """
        Test the is_open method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.is_open(study_name)
        assert _("Invalid") in str(e.value)
        mock_object.IsOpen.assert_not_called()

    @pytest.mark.parametrize("folder_name", ["Folder1", "Folder2"])
    def test_expand_folder(self, mock_project: Project, mock_object, folder_name):
        """
        Test the expand_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.ExpandFolder.return_value = True
        result = mock_project.expand_folder(folder_name)
        assert result
        mock_object.ExpandFolder.assert_called_once_with(folder_name)

    @pytest.mark.parametrize("folder_name", [True, 10])
    def test_expand_folder_invalid_type(self, mock_project: Project, mock_object, folder_name, _):
        """
        Test the expand_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.expand_folder(folder_name)
        assert _("Invalid") in str(e.value)
        mock_object.ExpandFolder.assert_not_called()

    @pytest.mark.parametrize("folder_name", ["Folder1", "Folder2"])
    def test_close_folder(self, mock_project: Project, mock_object, folder_name):
        """
        Test the close_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.CloseFolder.return_value = True
        result = mock_project.close_folder(folder_name)
        assert result
        mock_object.CloseFolder.assert_called_once_with(folder_name)

    @pytest.mark.parametrize("folder_name", [True, 10])
    def test_close_folder_invalid_type(self, mock_project: Project, mock_object, folder_name, _):
        """
        Test the close_folder method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        with pytest.raises(TypeError) as e:
            mock_project.close_folder(folder_name)
        assert _("Invalid") in str(e.value)
        mock_object.CloseFolder.assert_not_called()

    @pytest.mark.parametrize("path", ["Path1", "Path2"])
    def test_path(self, mock_project: Project, mock_object, path):
        """
        Test the path method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Path = path
        result = mock_project.path
        assert isinstance(result, str)
        assert result == path

    @pytest.mark.parametrize("name", ["Name1", "Name2"])
    def test_name(self, mock_project: Project, mock_object, name):
        """
        Test the name method of Project class.
        Args:
            mock_project: Instance of Project with mock object.
            mock_object: Mock object for the Project dependency.
        """
        mock_object.Name = name
        result = mock_project.name
        assert isinstance(result, str)
        assert result == name
