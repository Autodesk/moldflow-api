# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for Synergy Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the Synergy class with real Moldflow Synergy COM objects.
"""

import os
import logging
from pathlib import Path
import pygetwindow as gw
import pytest
from moldflow import (
    Synergy,
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
    Project,
    PropertyEditor,
    RunnerGenerator,
    StringArray,
    StudyDoc,
    SystemMessage,
    UnitConversion,
    Vector,
    VectorArray,
    Viewer,
    SystemUnits,
)
from tests.conftest import VALID_BOOL
from tests.api.integration_tests.constants import (
    FileSet,
    TEST_PROJECT_NAME,
    STUDY_FILES_DIR,
    MID_DOE_MODEL_NAME,
    MID_DOE_MODEL_FILE,
    SYNERGY_WINDOW_TITLE,
    DEFAULT_WINDOW_POSITION_X,
    DEFAULT_WINDOW_POSITION_Y,
    DEFAULT_WINDOW_SIZE_X,
    DEFAULT_WINDOW_SIZE_Y,
)

SYNERGY_CLASSES_LIST = [
    ("boundary_conditions", BoundaryConditions),
    ("cad_manager", CADManager),
    ("circuit_generator", CircuitGenerator),
    ("data_transform", DataTransform),
    ("diagnosis_manager", DiagnosisManager),
    ("folder_manager", FolderManager),
    ("import_options", ImportOptions),
    ("layer_manager", LayerManager),
    ("material_finder", MaterialFinder),
    ("material_selector", MaterialSelector),
    ("mesh_editor", MeshEditor),
    ("mesh_generator", MeshGenerator),
    ("model_duplicator", ModelDuplicator),
    ("modeler", Modeler),
    ("mold_surface_generator", MoldSurfaceGenerator),
    ("plot_manager", PlotManager),
    ("predicate_manager", PredicateManager),
    ("property_editor", PropertyEditor),
    ("project", Project),
    ("runner_generator", RunnerGenerator),
    ("study_doc", StudyDoc),
    ("system_message", SystemMessage),
    ("unit_conversion", UnitConversion),
    ("viewer", Viewer),
]

CREATE_OBJECT_METHODS_LIST = [
    ("create_vector", Vector),
    ("create_vector_array", VectorArray),
    ("create_double_array", DoubleArray),
    ("create_integer_array", IntegerArray),
    ("create_string_array", StringArray),
]


@pytest.mark.integration
@pytest.mark.synergy
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationSynergy:
    """
    Integration test suite for the Synergy class.
    Tests are run against meshed models to ensure all functionality is available.
    """

    def test_synergy_initialization(self, synergy: Synergy):
        """
        Test that Synergy instance is properly initialized.
        """
        assert synergy is not None
        assert synergy.synergy is not None

    def test_synergy_properties(self, synergy: Synergy, expected_values_general: dict):
        """
        Test Synergy properties return correct types.
        """

        units_val = synergy.units
        build_val = synergy.build
        build_number_val = synergy.build_number
        edition_val = synergy.edition
        version_val = synergy.version

        assert isinstance(units_val, str)
        assert isinstance(build_val, str)
        assert isinstance(build_number_val, str)
        assert isinstance(edition_val, str)
        assert isinstance(version_val, str)

        assert units_val in [units.value for units in SystemUnits]
        assert len(build_val) > 0
        assert len(build_number_val) > 0
        # assert len(edition_val) > 0
        assert len(version_val) > 0

        assert version_val == expected_values_general["version"]
        assert expected_values_general["build_number"] in build_number_val

    def test_new_project_open_project_open_recent_project(self, synergy: Synergy, temp_dir):
        """
        Test new project functionality.
        """
        project_name = TEST_PROJECT_NAME
        project_path = Path(temp_dir, project_name)

        result = synergy.new_project(project_name, str(project_path))
        assert result
        proj = synergy.project
        assert proj is not None
        assert os.path.exists(project_path)

        proj.close(False)
        assert proj.project is None

        result = synergy.open_project(str(project_path))
        assert result
        proj = synergy.project
        assert proj is not None

        proj.close(False)
        assert proj.project is None

        result = synergy.open_recent_project(0)
        # TODO: Need to update to assert True as soon as API is fixed
        assert result is False
        proj = synergy.project
        assert proj is not None

    def test_import_file(self, synergy: Synergy, temp_dir):
        """
        Test import file functionality.
        """
        project_name = TEST_PROJECT_NAME
        project_path = Path(temp_dir, project_name)
        file_path = Path(STUDY_FILES_DIR, FileSet.SINGLE.value, MID_DOE_MODEL_FILE)
        result = synergy.open_project(str(project_path))
        result = synergy.import_file(str(file_path))
        assert result

        proj = synergy.project
        std = proj.get_first_study_name()
        assert std == MID_DOE_MODEL_NAME

    def test_synergy_units_property(self, synergy: Synergy):
        """
        Test units property getter and setter.
        """
        current_units = synergy.units
        assert isinstance(current_units, str)
        assert current_units in [units.value for units in SystemUnits]

        original_units = current_units
        test_units = (
            SystemUnits.METRIC if current_units != SystemUnits.METRIC.value else SystemUnits.ENGLISH
        )
        synergy.units = test_units
        assert synergy.units == test_units.value

        synergy.units = test_units.value
        assert synergy.units == test_units.value

        synergy.units = original_units

    @pytest.mark.parametrize("silence_value", VALID_BOOL)
    def test_synergy_silence_method(self, synergy: Synergy, silence_value: bool):
        """
        Test silence method for suppressing message boxes.
        """
        result = synergy.silence(silence_value)
        assert isinstance(result, bool)

    def test_synergy_set_application_window_pos(self, synergy: Synergy):
        """
        Test setting application window position and size.
        """
        result = synergy.set_application_window_pos(100, 100, 800, 600)
        assert isinstance(result, bool)

        window = next((w for w in gw.getWindowsWithTitle(SYNERGY_WINDOW_TITLE) if w), None)
        assert window is not None

        left, top, right, bottom = window.left, window.top, window.right, window.bottom
        width, height = right - left, bottom - top

        assert (left, top, width, height) == (100, 100, 800, 600)

        synergy.set_application_window_pos(
            DEFAULT_WINDOW_POSITION_X,
            DEFAULT_WINDOW_POSITION_Y,
            DEFAULT_WINDOW_SIZE_X,
            DEFAULT_WINDOW_SIZE_Y,
        )

    @pytest.mark.parametrize(
        "synergy_class_name, synergy_class",
        SYNERGY_CLASSES_LIST,
        ids=[x[0] for x in SYNERGY_CLASSES_LIST],
    )
    def test_synergy_class_properties(
        self, synergy: Synergy, study_with_project, synergy_class_name, synergy_class
    ):
        """
        Test synergy class properties return correct types.
        """

        syn_class = getattr(synergy, synergy_class_name)
        if syn_class is not None:
            assert isinstance(syn_class, synergy_class)
            assert getattr(syn_class, synergy_class_name) is not None

    @pytest.mark.parametrize(
        "create_array_method_name, create_array_method_return",
        CREATE_OBJECT_METHODS_LIST,
        ids=[x[0] for x in CREATE_OBJECT_METHODS_LIST],
    )
    def test_synergy_create_array_methods(
        self, synergy: Synergy, create_array_method_name, create_array_method_return
    ):
        """
        Test create array methods create correct types.
        """
        create_array_method = getattr(synergy, create_array_method_name)()
        if create_array_method is not None:
            assert isinstance(create_array_method, create_array_method_return)

    def test_get_material_selector_with_index(self, synergy: Synergy, study_with_project):
        """
        Test get material selector with index method.
        """
        result = synergy.get_material_selector_with_index(0)
        assert isinstance(result, MaterialSelector)
        assert result.material_selector is not None

    # TODO: open_archive


@pytest.mark.integration
@pytest.mark.synergy
@pytest.mark.file_set(FileSet.SINGLE)
class TestIntegrationSynergyExportLMVSharedViews:
    """
    Integration test suite for the Synergy class export_lmv_shared_views method.
    """

    def test_export_lmv_shared_views(self, synergy: Synergy, study_with_project):
        """
        Test exporting LMV shared views.
        """
        plot_mgr = synergy.plot_manager
        plot = plot_mgr.find_plot_by_name("Fill Time", "Fill Time")
        assert plot is not None
        viewer = synergy.viewer
        viewer.show_plot(plot)
        result = synergy.export_lmv_shared_views("test_view")
        assert isinstance(result, str)
        assert len(result) > 0
        logging.info(f"LMV shared views exported to: {result}")


@pytest.mark.integration
@pytest.mark.synergy
class TestIntegrationSynergyQuit:
    """
    Integration test suite for the Synergy class quit method.
    """

    def test_quit(self, synergy: Synergy):
        """
        Test quit functionality.
        """
        synergy.quit(False)
        assert synergy.synergy is None
