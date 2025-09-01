# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for StudyDoc Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import StudyDoc, ImportOptions, EntList, StringArray, Vector
from tests.api.unit_tests.conftest import VALID_MOCK
from tests.conftest import NON_NEGATIVE_INT, VALID_STR, VALID_BOOL


@pytest.mark.unit
class TestUnitStudyDoc:
    """
    Test suite for the StudyDoc class.
    """

    @pytest.fixture
    def mock_study_doc(self, mock_object) -> StudyDoc:
        """
        Fixture to create a mock instance of StudyDoc.
        Args:
            mock_object: Mock object for the StudyDoc dependency.
        Returns:
            StudyDoc: An instance of StudyDoc with the mock object.
        """
        return StudyDoc(mock_object)

    @pytest.fixture
    def mock_ent_list(self) -> EntList:
        """
        Fixture to create a mock instance of EntList.
        Args:
            mock_object: Mock object for the EntList dependency.
        Returns:
            EntList: An instance of EntList with the mock object.
        """
        ent_list = Mock(spec=EntList)
        ent_list.ent_list = Mock()
        return ent_list

    @pytest.mark.parametrize(
        "property_name, pascal_case, value",
        [
            ("molding_process", "MoldingProcess", " Thermoplastic Injection Molding"),
            ("analysis_sequence", "AnalysisSequence", "Fill+Pack"),
            ("analysis_sequence_description", "AnalysisSequenceDescription", "Filling and Packing"),
            ("mesh_type", "MeshType", "3D"),
            ("number_of_analyses", "NumberOfAnalyses", "TestStudy"),
            ("study_name", "StudyName", "3D"),
            ("notes", "GetNotes", "This is a test note."),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_study_doc: StudyDoc, mock_object, property_name, pascal_case, value
    ):
        """
        Test setting properties of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
            property_name: Name of the property to test.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_case, value)
        new_val = getattr(mock_study_doc, property_name)
        assert isinstance(new_val, type(value))
        assert new_val == value

    @pytest.mark.parametrize(
        "property_name, pascal_case, value",
        [
            ("molding_process", "MoldingProcess", "Thermoplastic Injection Molding"),
            ("analysis_sequence", "AnalysisSequence", "Fill+Pack"),
            ("mesh_type", "MeshType", "3D"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_study_doc: StudyDoc, mock_object, property_name, pascal_case, value
    ):
        """
        Test getting properties of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
            property_name: Name of the property to test.
            value: Value to set and check.
        """
        setattr(mock_study_doc, property_name, value)
        result = getattr(mock_object, pascal_case)
        assert result == value

    def test_selection_get(self, mock_study_doc: StudyDoc, mock_object, mock_ent_list):
        """
        Test getting selection of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_object.Selection = mock_ent_list.ent_list
        result = mock_study_doc.selection
        assert isinstance(result, EntList)
        assert result.ent_list == mock_ent_list.ent_list

    def test_selection_set(self, mock_study_doc: StudyDoc, mock_ent_list):
        """
        Test setting selection of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_study_doc.selection = mock_ent_list
        result = mock_study_doc.selection
        assert result.ent_list == mock_ent_list.ent_list

    @pytest.mark.parametrize("text", ["This is a test note.", "Another test note."])
    def test_set_notes(self, mock_study_doc: StudyDoc, mock_object, text):
        """
        Test setting notes of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_study_doc.notes = text
        mock_object.SetNotes.assert_called_once_with(text)

    @pytest.mark.parametrize("name, prefix", [("Test", "Prefix"), ("Study", "TestPrefix")])
    def test_get_result_prefix(self, mock_study_doc: StudyDoc, mock_object, name, prefix):
        """
        Test getting result prefix of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_object.GetResultPrefix.return_value = prefix
        result = mock_study_doc.get_result_prefix(name)
        assert isinstance(result, str)
        assert result == prefix

    @pytest.mark.parametrize(
        "filename, doe, prompt, expected",
        [
            ("test_file.udm", True, True, True),
            ("test.udm", True, False, False),
            ("import.udm", False, False, False),
            ("test_file.udm", False, True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_import_process_variation(
        self, mock_study_doc: StudyDoc, mock_object, filename, doe, prompt, expected
    ):
        """
        Test the import_process_variation method of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_object.ImportProcessVariation.return_value = expected
        result = mock_study_doc.import_process_variation(filename, doe, prompt)
        assert result is expected
        mock_object.ImportProcessVariation.assert_called_once_with(filename, doe, prompt)

    @pytest.mark.parametrize(
        "filename, prompt, expected",
        [
            ("test_file.udm", True, True),
            ("test_file.udm", True, False),
            ("test_file.udm", False, False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_import_process_conditions(
        self, mock_study_doc: StudyDoc, mock_object, filename, prompt, expected
    ):
        """
        Test the import_process_conditions method of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        mock_object.ImportProcessCondition.return_value = expected
        result = mock_study_doc.import_process_condition(filename, prompt)
        assert result is expected
        mock_object.ImportProcessCondition.assert_called_once_with(filename, prompt)

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("molding_process", 123),
            ("analysis_sequence", True),
            ("mesh_type", False),
            ("notes", None),
        ],
    )
    def test_invalid_properties(self, mock_study_doc: StudyDoc, property_name, value, _):
        """
        Test invalid properties of StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_study_doc, property_name, value)
        assert _("Invalid") in str(e.value)

    def test_save(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the save method of StudyDoc.
        """
        mock_object.Save = True
        result = mock_study_doc.save()
        assert result

    def test_save_as(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the save_as method of StudyDoc.
        """
        mock_object.SaveAs.return_value = True
        result = mock_study_doc.save_as("NewStudyName")
        assert result
        mock_object.SaveAs.assert_called_once_with("NewStudyName")

    @pytest.mark.parametrize(
        "show_prompt, expected_return", list(zip([True, False], [True, False]))
    )
    def test_close(self, mock_study_doc: StudyDoc, mock_object, show_prompt, expected_return):
        """
        Test the close method of StudyDoc.
        """
        mock_object.Close2.return_value = expected_return
        result = mock_study_doc.close(show_prompt)
        mock_object.Close2.assert_called_once_with(show_prompt)
        assert isinstance(result, bool)
        assert result == expected_return
        if expected_return:
            assert mock_study_doc.study_doc is None
        else:
            assert mock_study_doc.study_doc is not None

    @pytest.mark.parametrize("expected_return", [True, False])
    def test_close_no_prompt(self, mock_study_doc: StudyDoc, mock_object, expected_return):
        """
        Test the close method of StudyDoc with no prompt.
        """
        mock_object.Close2.return_value = expected_return
        result = mock_study_doc.close()
        assert isinstance(result, bool)
        assert result == expected_return
        mock_object.Close2.assert_called_once_with(True)
        if expected_return:
            assert mock_study_doc.study_doc is None
        else:
            assert mock_study_doc.study_doc is not None

    @pytest.mark.parametrize("num", [1, 5, 10])
    def test_undo(self, mock_study_doc: StudyDoc, mock_object, num):
        """
        Test the undo method of StudyDoc.
        """
        mock_object.Undo.return_value = True
        result = mock_study_doc.undo(num)
        assert result
        mock_object.Undo.assert_called_once_with(num)

    @pytest.mark.parametrize("num", [1, 5, 10])
    def test_redo(self, mock_study_doc: StudyDoc, mock_object, num):
        """
        Test the redo method of StudyDoc.
        """
        mock_object.Redo.return_value = True
        result = mock_study_doc.redo(num)
        assert result
        mock_object.Redo.assert_called_once_with(num)

    def test_analyze_now(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the analyze_now method of StudyDoc.
        """
        mock_object.AnalyzeNow2.return_value = True
        opts = (True, True, True)
        result = mock_study_doc.analyze_now(opts[0], opts[1], opts[2])
        assert result
        mock_object.AnalyzeNow2.assert_called_once_with(opts[0], opts[1], opts[2])

    def test_add_file(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the add_file method of StudyDoc.
        """
        mock_object.AddFile.return_value = True
        opts = Mock(spec=ImportOptions)
        opts.import_options = Mock()
        result = mock_study_doc.add_file("test_file.cad", opts, True)
        assert result
        mock_object.AddFile.assert_called_once_with("test_file.cad", opts.import_options, True)

    @pytest.mark.parametrize(
        "snake_case, pascal_case, has_arg",
        [
            ("get_first_node", "GetFirstNode", False),
            ("get_next_node", "GetNextNode", True),
            ("get_first_tri", "GetFirstTri", False),
            ("get_next_tri", "GetNextTri", True),
            ("get_first_beam", "GetFirstBeam", False),
            ("get_next_beam", "GetNextBeam", True),
            ("get_first_tet", "GetFirstTet", False),
            ("get_next_tet", "GetNextTet", True),
            ("get_elem_nodes", "GetElemNodes", True),
            ("get_entity_layer", "GetEntityLayer", True),
            ("get_entity_id", "GetEntityID", True),
            ("get_first_curve", "GetFirstCurve", False),
            ("get_next_curve", "GetNextCurve", True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_entlist(
        self, mock_study_doc: StudyDoc, mock_object, mock_ent_list, snake_case, pascal_case, has_arg
    ):
        """
        Test the get_first_node method of StudyDoc.
        """
        if has_arg:  # Need to provide input
            func = getattr(mock_study_doc, snake_case)
            getattr(mock_object, pascal_case).return_value = mock_ent_list
            node = mock_ent_list
            result = func(node)
            getattr(mock_object, pascal_case).assert_called_once_with(node.ent_list)
            assert isinstance(result, EntList)
        else:  # No input needed
            setattr(mock_object, pascal_case, mock_ent_list)
            result = getattr(mock_study_doc, snake_case)()
            assert result is not None

    def test_get_node_coord(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the get_node_coord method of StudyDoc.
        """
        mock_object.GetNodeCoord.return_value = Mock(spec=Vector)
        node = Mock(spec=EntList)
        node.ent_list = Mock()
        result = mock_study_doc.get_node_coord(node)
        assert isinstance(result, Vector)
        assert result is not None
        mock_object.GetNodeCoord.assert_called_once_with(node.ent_list)

    @pytest.mark.parametrize("pos", [0, 1, 0.5, 0.25])
    def test_get_curve_point(self, mock_study_doc: StudyDoc, mock_object, pos):
        """
        Test the get_curve_point method of StudyDoc.
        """
        node = Mock(spec=EntList)
        node.ent_list = Mock()
        mock_object.GetCurvePoint.return_value = Mock(spec=Vector)
        result = mock_study_doc.get_curve_point(node, pos)
        assert isinstance(result, Vector)
        assert result is not None
        mock_object.GetCurvePoint.assert_called_once_with(node.ent_list, pos)

    @pytest.mark.parametrize("index, expected", [(1, True), (5, False), (10, False)])
    def test_delete_results(self, mock_study_doc: StudyDoc, mock_object, index, expected):
        """
        Test the delete_results method of StudyDoc.
        """
        mock_object.DeleteResults.return_value = expected
        result = mock_study_doc.delete_results(index)
        assert result is expected
        mock_object.DeleteResults.assert_called_once_with(index)

    @pytest.mark.parametrize(
        "expected, prompts", [(True, True), (True, True), (False, False), (False, False)]
    )
    def test_mesh_now(self, mock_study_doc: StudyDoc, mock_object, expected, prompts):
        """
        Test the mesh_now method of StudyDoc.
        """
        mock_object.MeshNow.return_value = expected
        mock_object.MeshNow3.return_value = expected
        result = mock_study_doc.mesh_now(prompts)
        assert result is expected
        mock_object.MeshNow.assert_called_once_with(prompts)

    @pytest.mark.parametrize("expected, filename", [(True, "analyze.txt"), (False, "test.txt")])
    def test_export_analysis_log(self, mock_study_doc: StudyDoc, mock_object, expected, filename):
        """
        Test the export_analysis_log method of StudyDoc.
        """
        mock_object.ExportAnalysisLog.return_value = expected
        result = mock_study_doc.export_analysis_log(filename)
        assert result is expected
        mock_object.ExportAnalysisLog.assert_called_once_with(filename)

    @pytest.mark.parametrize("expected, filename", [(True, "test.txt"), (False, "mesh.txt")])
    def test_export_mesh_log(self, mock_study_doc: StudyDoc, mock_object, expected, filename):
        """
        Test the export_mesh_log method of StudyDoc.
        """
        mock_object.ExportMeshLog.return_value = expected
        result = mock_study_doc.export_mesh_log(filename)
        assert result is expected
        mock_object.ExportMeshLog.assert_called_once_with(filename)

    @pytest.mark.parametrize("marking", [False, True])
    def test_mark_analysis_summary_for_export(self, mock_study_doc: StudyDoc, mock_object, marking):
        """
        Test the mark_analysis_summary_for_export method of StudyDoc.
        """
        mock_study_doc.mark_analysis_summary_for_export(marking)
        mock_object.MarkAnalysisSummaryForExport.assert_called_once_with(marking)

    def test_get_part_cad_names(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the get_part_cad_names method of StudyDoc.
        """
        mock_object.GetPartCadNames = Mock(spec=StringArray)
        result = mock_study_doc.get_part_cad_names()
        assert isinstance(result, StringArray)

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("molding_process", 50),
            ("molding_process", True),
            ("analysis_sequence", 50),
            ("analysis_sequence", True),
            ("mesh_type", 50),
            ("mesh_type", True),
            ("selection", 50),
            ("selection", True),
        ],
    )
    def test_set_property_invalid(self, mock_study_doc: StudyDoc, property_name, value, _):
        """
        Test setting invalid properties of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_study_doc, property_name, value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "property_name, value", [("molding_process", "1234"), ("mesh_type", "Something")]
    )
    def test_set_property_enum_invalid(
        self, mock_study_doc: StudyDoc, property_name, value, _, caplog
    ):
        """
        Test setting invalid properties of StudyDoc.
        """
        setattr(mock_study_doc, property_name, value)
        assert _("this may cause function call to fail") in caplog.text

    @pytest.mark.parametrize(
        "function_name, value",
        [
            ("save_as", 50),
            ("save_as", True),
            ("close", 50),
            ("close", "True"),
            ("undo", True),
            ("undo", "Test"),
            ("redo", True),
            ("redo", "Test"),
            ("get_next_node", True),
            ("get_next_node", 123),
            ("get_next_node", "test_node"),
            ("get_node_coord", "test_node"),
            ("get_node_coord", 456),
            ("get_node_coord", True),
            ("get_next_tri", True),
            ("get_next_tri", 135),
            ("get_next_tri", "test_tri"),
            ("get_next_beam", "test_beam"),
            ("get_next_beam", 12),
            ("get_next_beam", False),
            ("get_next_tet", False),
            ("get_next_tet", "test_tet"),
            ("get_next_tet", 57),
            ("get_elem_nodes", 57),
            ("get_elem_nodes", True),
            ("get_elem_nodes", "Elem_Node"),
            ("get_entity_layer", "Elem_Node"),
            ("get_entity_layer", True),
            ("get_entity_layer", 90),
            ("get_entity_id", "Elem_Node"),
            ("get_entity_id", True),
            ("get_entity_id", 90),
            ("get_next_curve", False),
            ("get_next_curve", "test_tet"),
            ("get_next_curve", 57),
            ("delete_results", True),
            ("delete_results", "50"),
            ("mesh_now", "50"),
            ("mesh_now", 50),
            ("get_result_prefix", 50),
            ("get_result_prefix", True),
            ("export_analysis_log", True),
            ("export_analysis_log", 1),
            ("export_mesh_log", 1),
            ("export_mesh_log", False),
            ("mark_analysis_summary_for_export", "test"),
            ("mark_analysis_summary_for_export", 0),
        ],
    )
    def test_run_function_invalid(
        self, mock_study_doc: StudyDoc, mock_object, function_name, value, _
    ):
        """
        Test invalid parameters into a function of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_study_doc, function_name)(value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, function_name).assert_not_called()

    @pytest.mark.parametrize(
        "filename, opts, show_log",
        [
            ("test_file.txt", Mock(spec=ImportOptions), "test"),
            ("test_file.txt", Mock(spec=ImportOptions), 50),
            ("test_file.txt", "test", False),
            ("test_file.txt", 50, False),
            ("test_file.txt", False, False),
            (50, Mock(spec=ImportOptions), True),
            (False, Mock(spec=ImportOptions), False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_add_file_invalid(
        self, mock_study_doc: StudyDoc, mock_object, filename, opts, show_log, _
    ):
        """
        Test adding invalid file to StudyDoc.
        Args:
            mock_study_doc: Instance of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            mock_study_doc.add_file(filename, opts, show_log)
        assert _("Invalid") in str(e.value)
        mock_object.AddFile.assert_not_called()

    @pytest.mark.parametrize(
        "check, solve, prompts",
        [
            (True, True, 1),
            (True, 2, True),
            (3, True, True),
            (True, "4", True),
            (True, True, "5"),
            ("6", True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_analyze_now_invalid(
        self, mock_study_doc: StudyDoc, mock_object, check, solve, prompts, _
    ):
        """
        Test invalid parameters into analyze_now method of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            mock_study_doc.analyze_now(check, solve, prompts)
        assert _("Invalid") in str(e.value)
        mock_object.AnalyzeNow2.assert_not_called()

    @pytest.mark.parametrize(
        "import_type, pascal_case, file, prompt",
        [
            ("import_process_condition", "ImportProcessCondition", 2, True),
            ("import_process_condition", "ImportProcessCondition", True, True),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_import_invalid(
        self, mock_study_doc: StudyDoc, mock_object, import_type, pascal_case, file, prompt, _
    ):
        """
        Test invalid parameters into import_process_condition method of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_study_doc, import_type)(file, prompt)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_case).assert_not_called()

    @pytest.mark.parametrize("file, doe, prompts", [(3, True, True), (True, True, True)])
    # pylint: disable-next=R0913, R0917
    def test_import_process_variation_invalid(
        self, mock_study_doc: StudyDoc, mock_object, file, doe, prompts, _
    ):
        """
        Test invalid parameters into analyze_now method of StudyDoc.
        """
        with pytest.raises(TypeError) as e:
            mock_study_doc.import_process_variation(file, doe, prompts)
        assert _("Invalid") in str(e.value)
        mock_object.ImportProcessVariation.assert_not_called()

    def test_create_entity_list(self, mock_study_doc: StudyDoc, mock_object):
        """
        Test the create_entity_list method of StudyDoc.
        """
        mock_object.CreateEntityList = VALID_MOCK.ENT_LIST.ent_list
        result = mock_study_doc.create_entity_list()
        assert isinstance(result, EntList)
        assert result.ent_list == VALID_MOCK.ENT_LIST.ent_list

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("CreateEntityList", "create_entity_list"),
            ("GetFirstNode", "get_first_node"),
            ("GetFirstTri", "get_first_tri"),
            ("GetFirstBeam", "get_first_beam"),
            ("GetFirstTet", "get_first_tet"),
            ("GetFirstCurve", "get_first_curve"),
            ("GetPartCadNames", "get_part_cad_names"),
        ],
    )
    def test_function_no_arg_return_none(
        self, mock_study_doc: StudyDoc, mock_object, pascal_name, property_name
    ):
        """
        Test the return value of the function is None.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_study_doc, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            (
                "GetNextNode",
                "get_next_node",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            (
                "GetNodeCoord",
                "get_node_coord",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            ("GetNextTri", "get_next_tri", (VALID_MOCK.ENT_LIST,), (VALID_MOCK.ENT_LIST.ent_list,)),
            (
                "GetNextBeam",
                "get_next_beam",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            ("GetNextTet", "get_next_tet", (VALID_MOCK.ENT_LIST,), (VALID_MOCK.ENT_LIST.ent_list,)),
            (
                "GetElemNodes",
                "get_elem_nodes",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            (
                "GetEntityLayer",
                "get_entity_layer",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            (
                "GetNextCurve",
                "get_next_curve",
                (VALID_MOCK.ENT_LIST,),
                (VALID_MOCK.ENT_LIST.ent_list,),
            ),
            (
                "GetCurvePoint",
                "get_curve_point",
                (VALID_MOCK.ENT_LIST, 0.5),
                (VALID_MOCK.ENT_LIST.ent_list, 0.5),
            ),
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self, mock_study_doc: StudyDoc, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the return value of the function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_study_doc, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("AnalysisStatus", "analysis_status", (x,), (x,), str, y)
            for x in NON_NEGATIVE_INT
            for y in VALID_STR
        ]
        + [
            ("AnalysisName", "analysis_name", (x,), (x,), str, y)
            for x in NON_NEGATIVE_INT
            for y in VALID_STR
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function(
        self,
        mock_study_doc: StudyDoc,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the return value of the function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_study_doc, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, return_value",
        [("MeshStatus", "mesh_status", str, x) for x in VALID_STR]
        + [("IsAnalysisRunning", "is_analysis_running", bool, x) for x in VALID_BOOL],
    )
    # pylint: disable=R0913, R0917
    def test_function_no_args(
        self,
        mock_study_doc: StudyDoc,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        return_value,
    ):
        """
        Test the return value of the function.
        """
        setattr(mock_object, pascal_name, return_value)
        result = getattr(mock_study_doc, property_name)()
        assert isinstance(result, return_type)
        assert result == return_value

    @pytest.mark.parametrize("pascal_name, property_name", [("Selection", "selection")])
    def test_property_return_none(
        self, mock_study_doc: StudyDoc, mock_object, pascal_name, property_name
    ):
        """
        Test the return value of the property.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_study_doc, property_name)
        assert result is None
