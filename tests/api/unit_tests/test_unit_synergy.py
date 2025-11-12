# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for Synergy Wrapper Class of moldflow-api module.
Test Details:

Classes:
    TestUnitSynergy: Test suite for the Synergy class.
Fixtures:
    mock_synergy: Fixture to create a mock instance of Synergy.
Test Methods:

"""

from unittest.mock import Mock, PropertyMock, patch
import pytest
from moldflow import (
    BoundaryConditions,
    CADManager,
    CircuitGenerator,
    DataTransform,
    DiagnosisManager,
    DoubleArray,
    FolderManager,
    ImportOptions,
    IntegerArray,
    LayerManager,
    MaterialFinder,
    MaterialSelector,
    MeshEditor,
    MeshGenerator,
    ModelDuplicator,
    Modeler,
    MoldSurfaceGenerator,
    PlotManager,
    PredicateManager,
    PropertyEditor,
    Project,
    RunnerGenerator,
    StringArray,
    StudyDoc,
    SystemMessage,
    UnitConversion,
    Vector,
    VectorArray,
    Viewer,
    Synergy,
    SystemUnits,
)
from moldflow.exceptions import SynergyError
from moldflow.logger import set_is_logging
from tests.api.unit_tests.conftest import VALID_MOCK
from tests.conftest import (
    VALID_BOOL,
    VALID_STR,
    INVALID_BOOL,
    INVALID_INT,
    INVALID_STR,
    NEGATIVE_INT,
    POSITIVE_INT,
    pad_and_zip,
)


@pytest.mark.unit
@pytest.mark.synergy
class TestUnitSynergy:
    """
    Test suite for the Synergy class.
    """

    set_is_logging(True)

    @pytest.fixture
    def mock_synergy(self, mock_object) -> Synergy:
        """
        Fixture to create a mock instance of Synergy.
        Args:
            mock_object: Mock object for the Synergy dependency.
        Returns:
            Synergy: An instance of Synergy with the mock object.
        """
        synergy = Synergy.__new__(Synergy)
        synergy.synergy = mock_object
        return synergy

    @patch("moldflow.synergy.safe_com")
    @patch("moldflow.synergy.win32com.client.GetObject")
    def test_synergy_initialization_normal_path(self, mock_get_object, mock_safe_com):
        """
        Test Synergy initialization if SAInstance is set in os.environ (if block).
        """
        mock_synergy_instance = Mock()
        mock_getter = Mock()
        mock_getter.GetSASynergy = mock_synergy_instance
        mock_get_object.return_value = mock_getter
        mock_safe_proxy = Mock()
        mock_safe_com.return_value = mock_safe_proxy
        with patch("moldflow.synergy.os.environ", {"SAInstance": "mock_env_path"}):
            syn = Synergy()
            mock_get_object.assert_called_once_with("mock_env_path")
            mock_safe_com.assert_called_once_with(mock_synergy_instance)
            assert syn.synergy is mock_safe_proxy

    @pytest.mark.parametrize("units", [None] + list(SystemUnits))
    @patch("moldflow.synergy.win32com.client.Dispatch", side_effect=Exception("COM failed"))
    def test_synergy_initialization_fallback_path(self, mock_dispatch, units):
        """
        Test the fallback initialization path of the Synergy class when GetObject fails.
        Args:
            mock_dispatch: Mock for the Dispatch method.
            mock_get_object: Mock for the GetObject method that raises an exception.
        """
        mock_shell = Mock()
        mock_shell.ExpandEnvironmentStrings.return_value = "mock_env_path"
        mock_fallback_synergy = Mock()
        mock_dispatch.side_effect = [mock_shell, mock_fallback_synergy]
        Synergy(units=units, logging=False)
        mock_dispatch.assert_called_with("synergy.Synergy")

    @patch("moldflow.synergy.safe_com")
    @patch("moldflow.synergy.win32com.client.Dispatch")
    def test_synergy_initialization_synergy_not_found(self, mock_dispatch, mock_safe_com):
        """
        Test the initialization path of the Synergy class when Synergy is not found.
        """
        # Simulate GetObject fails and Dispatch fails
        mock_dispatch.side_effect = Exception("synergy.Synergy failed")
        with patch("moldflow.synergy.os.environ", {}):
            with pytest.raises(SynergyError):
                Synergy()
        mock_dispatch.assert_called_with("synergy.Synergy")
        mock_safe_com.assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args, return_type, return_value",
        [
            ("Silence", "silence", (x,), (x,), bool, y)
            for x, y in pad_and_zip(VALID_BOOL, VALID_BOOL)
        ]
        + [
            ("NewProject", "new_project", (x, y), (x, y), bool, z)
            for x, y, z in pad_and_zip(VALID_STR, VALID_STR, VALID_BOOL)
        ]
        + [
            ("OpenProject", "open_project", (x,), (x,), bool, y)
            for x, y in pad_and_zip(VALID_STR, VALID_BOOL)
        ]
        + [
            ("ExportLMVSharedViews", "export_lmv_shared_views", (x,), (x,), str, y)
            for x, y in pad_and_zip(VALID_STR, VALID_STR)
        ]
        + [
            ("OpenArchive", "open_archive", (x, y), (x, y), bool, z)
            for x, y, z in pad_and_zip(VALID_STR, VALID_STR, VALID_BOOL)
        ]
        + [
            ("OpenRecentProject", "open_recent_project", (x,), (x,), bool, y)
            for x, y in pad_and_zip(range(4), VALID_BOOL)
        ]
        + [
            ("ImportFile2", "import_file", (v, w, x), (v, w.import_options, x, False), bool, z)
            for v, w, x, z in pad_and_zip(
                VALID_STR, VALID_MOCK.IMPORT_OPTIONS, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            ("ImportFile2", "import_file", (v, w, x, True), (v, w.import_options, x, True), bool, z)
            for v, w, x, z in pad_and_zip(
                VALID_STR, VALID_MOCK.IMPORT_OPTIONS, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            (
                "SetApplicationWindowPos",
                "set_application_window_pos",
                (x, y, z, w),
                (x, y, z, w),
                bool,
                v,
            )
            for x, y, z, w, v in pad_and_zip(
                POSITIVE_INT, POSITIVE_INT, POSITIVE_INT, POSITIVE_INT, VALID_BOOL
            )
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions(
        self,
        mock_synergy: Synergy,
        mock_object,
        pascal_name,
        property_name,
        args,
        expected_args,
        return_type,
        return_value,
    ):
        """
        Test the functions of the Synergy class.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments after processing.
            return_type: Expected return type of the function.
            return_value: Expected return value of the function.
        """
        getattr(mock_object, pascal_name).return_value = return_value
        result = getattr(mock_synergy, property_name)(*args)
        assert isinstance(result, return_type)
        assert result == return_value
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    def test_import_file_no_import_options(self, mock_synergy: Synergy, mock_object):
        """
        Test the import_file function without import options.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
        """
        import_options_instance = Mock(spec=ImportOptions)
        import_options_instance.import_options = Mock()
        with patch.object(Synergy, "import_options", new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = import_options_instance
            v = VALID_STR[0]
            getattr(mock_object, "ImportFile2").return_value = True
            result = mock_synergy.import_file(v)
            assert result is True
            # The assertion must be inside the patch context!
            getattr(mock_object, "ImportFile2").assert_called_once_with(
                v, import_options_instance.import_options, True, False
            )

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("Silence", "silence", (x,)) for x in pad_and_zip(INVALID_BOOL)]
        + [("NewProject", "new_project", (x, y)) for x, y in pad_and_zip(INVALID_STR, VALID_STR)]
        + [("NewProject", "new_project", (x, y)) for x, y in pad_and_zip(VALID_STR, INVALID_STR)]
        + [("OpenProject", "open_project", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [
            ("ExportLMVSharedViews", "export_lmv_shared_views", (x,))
            for x in pad_and_zip(INVALID_STR)
        ]
        + [("OpenArchive", "open_archive", (x, y)) for x, y in pad_and_zip(INVALID_STR, VALID_STR)]
        + [("OpenArchive", "open_archive", (x, y)) for x, y in pad_and_zip(VALID_STR, INVALID_STR)]
        + [("OpenRecentProject", "open_recent_project", (x,)) for x in pad_and_zip(INVALID_INT)]
        + [("ImportFile2", "import_file", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [("ImportFile3", "import_file", (x,)) for x in pad_and_zip(INVALID_STR)]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(INVALID_INT, POSITIVE_INT, POSITIVE_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, INVALID_INT, POSITIVE_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, POSITIVE_INT, INVALID_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, POSITIVE_INT, POSITIVE_INT, INVALID_INT)
        ]
        + [
            ("GetMaterialSelectorWithIndex", "get_material_selector_with_index", (x,))
            for x in pad_and_zip(INVALID_INT)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_type(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions of the Synergy class with invalid types.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(TypeError) as e:
            getattr(mock_synergy, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    def test_quit(self, mock_synergy: Synergy, mock_object):
        """
        Test the quit method of the Synergy class.
        """
        mock_synergy.quit(True)
        mock_object.Quit.assert_called_once()
        assert mock_synergy.synergy is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [("Quit", "quit", (x,), (x,)) for x in pad_and_zip(VALID_BOOL)],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_no_return(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the functions of the Synergy class that do not return a value.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
            expected_args: Expected arguments after processing.
        """
        getattr(mock_synergy, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [("OpenRecentProject", "open_recent_project", (x,)) for x in [-1, 4]]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(NEGATIVE_INT, POSITIVE_INT, POSITIVE_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, NEGATIVE_INT, POSITIVE_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, POSITIVE_INT, NEGATIVE_INT, POSITIVE_INT)
        ]
        + [
            ("SetApplicationWindowPos", "set_application_window_pos", (x, y, z, w))
            for x, y, z, w in pad_and_zip(POSITIVE_INT, POSITIVE_INT, POSITIVE_INT, NEGATIVE_INT)
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_invalid_value(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, args, _
    ):
        """
        Test the functions of the Synergy class with invalid types.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: Arguments to be passed to the function.
        """
        with pytest.raises(ValueError) as e:
            getattr(mock_synergy, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, expected_return, type_instance",
        [
            ("CreateVector", "create_vector", Vector, VALID_MOCK.VECTOR, "vector"),
            (
                "CreateVectorArray",
                "create_vector_array",
                VectorArray,
                VALID_MOCK.VECTOR_ARRAY,
                "vector_array",
            ),
            (
                "CreateDoubleArray",
                "create_double_array",
                DoubleArray,
                VALID_MOCK.DOUBLE_ARRAY,
                "double_array",
            ),
            (
                "CreateIntegerArray",
                "create_integer_array",
                IntegerArray,
                VALID_MOCK.INTEGER_ARRAY,
                "integer_array",
            ),
            (
                "CreateStringArray",
                "create_string_array",
                StringArray,
                VALID_MOCK.STRING_ARRAY,
                "string_array",
            ),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_function_return_classes(
        self,
        mock_synergy: Synergy,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        expected_return,
        type_instance,
    ):
        """
        Test the method of the Synergy class.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
        """
        expected_return_instance = getattr(expected_return, type_instance)
        setattr(mock_object, pascal_name, expected_return_instance)
        result = getattr(mock_synergy, property_name)()
        assert isinstance(result, return_type)
        assert getattr(result, type_instance) == expected_return_instance

    @pytest.mark.parametrize(
        # pylint: disable=C0301
        "pascal_name, property_name, args, expected_args, return_type, expected_return, type_instance",
        [
            (
                "GetMaterialSelectorWithIndex",
                "get_material_selector_with_index",
                (x,),
                (x,),
                MaterialSelector,
                VALID_MOCK.MATERIAL_SELECTOR,
                "material_selector",
            )
            for x in pad_and_zip(range(4))
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_function_args_return_classes(
        self,
        mock_synergy: Synergy,
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
        Test the method of the Synergy class.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
        """
        expected_return_instance = getattr(expected_return, type_instance)
        getattr(mock_object, pascal_name).return_value = expected_return_instance
        result = getattr(mock_synergy, property_name)(*args)
        assert isinstance(result, return_type)
        assert getattr(result, type_instance) == expected_return_instance
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [("SetUnits", "units", x, x.value) for x in SystemUnits],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, value, expected
    ):
        """
        Test properties of Synergy.

        Args:
            mock_synergy: Instance of Synergy.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_synergy, property_name, value)
        getattr(mock_object, pascal_name).assert_called_once_with(expected)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("GetUnits", "units", x) for x in SystemUnits]
        + [("Build", "build", x) for x in VALID_STR]
        + [("BuildNumber", "build_number", x) for x in VALID_STR]
        + [("Edition", "edition", x) for x in VALID_STR]
        + [("Version", "version", x) for x in VALID_STR],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of Synergy.

        Args:
            mock_synergy: Instance of Synergy.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_synergy, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize("property_name, value", [("units", x) for x in INVALID_STR])
    def test_properties_invalid_type(self, mock_synergy: Synergy, property_name, value, _):
        """
        Test invalid properties of Synergy.
        Args:
            mock_synergy: Instance of Synergy.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_synergy, property_name, value)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "pascal_name, property_name, return_type, expected_return, type_instance",
        [
            (
                "BoundaryConditions",
                "boundary_conditions",
                BoundaryConditions,
                VALID_MOCK.BOUNDARY_CONDITIONS,
                "boundary_conditions",
            ),
            ("CADManager", "cad_manager", CADManager, VALID_MOCK.CAD_MANAGER, "cad_manager"),
            (
                "CircuitGenerator",
                "circuit_generator",
                CircuitGenerator,
                VALID_MOCK.CIRCUIT_GENERATOR,
                "circuit_generator",
            ),
            (
                "DataTransform",
                "data_transform",
                DataTransform,
                VALID_MOCK.DATA_TRANSFORM,
                "data_transform",
            ),
            (
                "DiagnosisManager",
                "diagnosis_manager",
                DiagnosisManager,
                VALID_MOCK.DIAGNOSIS_MANAGER,
                "diagnosis_manager",
            ),
            (
                "FolderManager",
                "folder_manager",
                FolderManager,
                VALID_MOCK.FOLDER_MANAGER,
                "folder_manager",
            ),
            (
                "ImportOptions",
                "import_options",
                ImportOptions,
                VALID_MOCK.IMPORT_OPTIONS,
                "import_options",
            ),
            (
                "LayerManager",
                "layer_manager",
                LayerManager,
                VALID_MOCK.LAYER_MANAGER,
                "layer_manager",
            ),
            (
                "MaterialFinder",
                "material_finder",
                MaterialFinder,
                VALID_MOCK.MATERIAL_FINDER,
                "material_finder",
            ),
            (
                "MaterialSelector",
                "material_selector",
                MaterialSelector,
                VALID_MOCK.MATERIAL_SELECTOR,
                "material_selector",
            ),
            ("MeshEditor", "mesh_editor", MeshEditor, VALID_MOCK.MESH_EDITOR, "mesh_editor"),
            (
                "MeshGenerator",
                "mesh_generator",
                MeshGenerator,
                VALID_MOCK.MESH_GENERATOR,
                "mesh_generator",
            ),
            (
                "ModelDuplicator",
                "model_duplicator",
                ModelDuplicator,
                VALID_MOCK.MODEL_DUPLICATOR,
                "model_duplicator",
            ),
            ("Modeler", "modeler", Modeler, VALID_MOCK.MODELER, "modeler"),
            (
                "MoldSurfaceGenerator",
                "mold_surface_generator",
                MoldSurfaceGenerator,
                VALID_MOCK.MOLD_SURFACE_GENERATOR,
                "mold_surface_generator",
            ),
            ("PlotManager", "plot_manager", PlotManager, VALID_MOCK.PLOT_MANAGER, "plot_manager"),
            (
                "PredicateManager",
                "predicate_manager",
                PredicateManager,
                VALID_MOCK.PREDICATE_MANAGER,
                "predicate_manager",
            ),
            (
                "PropertyEditor",
                "property_editor",
                PropertyEditor,
                VALID_MOCK.PROPERTY_EDITOR,
                "property_editor",
            ),
            ("Project", "project", Project, VALID_MOCK.PROJECT, "project"),
            (
                "RunnerGenerator",
                "runner_generator",
                RunnerGenerator,
                VALID_MOCK.RUNNER_GENERATOR,
                "runner_generator",
            ),
            ("StudyDoc", "study_doc", StudyDoc, VALID_MOCK.STUDY_DOC, "study_doc"),
            (
                "SystemMessage",
                "system_message",
                SystemMessage,
                VALID_MOCK.SYSTEM_MESSAGE,
                "system_message",
            ),
            (
                "UnitConversion",
                "unit_conversion",
                UnitConversion,
                VALID_MOCK.UNIT_CONVERSION,
                "unit_conversion",
            ),
            ("Viewer", "viewer", Viewer, VALID_MOCK.VIEWER, "viewer"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_properties_return_classes(
        self,
        mock_synergy: Synergy,
        mock_object,
        pascal_name,
        property_name,
        return_type,
        expected_return,
        type_instance,
    ):
        """
        Test the property of the Synergy class that returns a class instance.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the property.
            property_name: The property name to be tested.
            return_type: The expected return type.
            expected_return: The expected mock return value.
            type_instance: The attribute name to check on the returned object.
        """
        mock_instance = getattr(expected_return, type_instance)
        setattr(mock_object, pascal_name, mock_instance)
        result = getattr(mock_synergy, property_name)
        assert isinstance(result, return_type)
        assert getattr(result, type_instance) == mock_instance

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("BoundaryConditions", "boundary_conditions"),
            ("CADManager", "cad_manager"),
            ("CircuitGenerator", "circuit_generator"),
            ("DataTransform", "data_transform"),
            ("DiagnosisManager", "diagnosis_manager"),
            ("FolderManager", "folder_manager"),
            ("ImportOptions", "import_options"),
            ("LayerManager", "layer_manager"),
            ("MaterialFinder", "material_finder"),
            ("MaterialSelector", "material_selector"),
            ("MeshEditor", "mesh_editor"),
            ("MeshGenerator", "mesh_generator"),
            ("ModelDuplicator", "model_duplicator"),
            ("Modeler", "modeler"),
            ("MoldSurfaceGenerator", "mold_surface_generator"),
            ("PlotManager", "plot_manager"),
            ("PredicateManager", "predicate_manager"),
            ("PropertyEditor", "property_editor"),
            ("Project", "project"),
            ("RunnerGenerator", "runner_generator"),
            ("StudyDoc", "study_doc"),
            ("SystemMessage", "system_message"),
            ("UnitConversion", "unit_conversion"),
            ("Viewer", "viewer"),
        ],
    )
    def test_properties_return_none(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name
    ):
        """
        Test the functions of the Synergy class that return None.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_synergy, property_name)
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name",
        [
            ("CreateVector", "create_vector"),
            ("CreateVectorArray", "create_vector_array"),
            ("CreateDoubleArray", "create_double_array"),
            ("CreateIntegerArray", "create_integer_array"),
            ("CreateStringArray", "create_string_array"),
        ],
    )
    def test_functions_return_none(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name
    ):
        """
        Test the functions of the Synergy class that return None.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
        """
        setattr(mock_object, pascal_name, None)
        result = getattr(mock_synergy, property_name)()
        assert result is None

    @pytest.mark.parametrize(
        "pascal_name, property_name, args, expected_args",
        [
            ("GetMaterialSelectorWithIndex", "get_material_selector_with_index", (x,), (x,))
            for x in pad_and_zip(range(4))
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_functions_args_return_none(
        self, mock_synergy: Synergy, mock_object, pascal_name, property_name, args, expected_args
    ):
        """
        Test the functions of the Synergy class that return None.

        Args:
            mock_synergy: The mock instance of Synergy.
            mock_object: The mock object for the Synergy dependency.
            pascal_name: The Pascal case name of the function.
            property_name: The property name to be tested.
            args: The arguments to be passed to the function.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_synergy, property_name)(*args)
        assert result is None
        getattr(mock_object, pascal_name).assert_called_once_with(*expected_args)
