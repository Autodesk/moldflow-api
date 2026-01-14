# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Synergy Class API Wrapper
"""

import os
import win32com.client
from .boundary_conditions import BoundaryConditions
from .cad_manager import CADManager
from .circuit_generator import CircuitGenerator
from .data_transform import DataTransform
from .diagnosis_manager import DiagnosisManager
from .double_array import DoubleArray
from .folder_manager import FolderManager
from .import_options import ImportOptions
from .integer_array import IntegerArray
from .layer_manager import LayerManager
from .material_finder import MaterialFinder
from .material_selector import MaterialSelector
from .mesh_editor import MeshEditor
from .mesh_generator import MeshGenerator
from .model_duplicator import ModelDuplicator
from .modeler import Modeler
from .mold_surface_generator import MoldSurfaceGenerator
from .plot_manager import PlotManager
from .predicate_manager import PredicateManager
from .project import Project
from .property_editor import PropertyEditor
from .runner_generator import RunnerGenerator
from .string_array import StringArray
from .study_doc import StudyDoc
from .system_message import SystemMessage
from .unit_conversion import UnitConversion
from .vector import Vector
from .vector_array import VectorArray
from .viewer import Viewer
from .localization import set_language
from .logger import process_log, configure_file_logging
from .common import LogMessage, SystemUnits
from .constants import DEFAULT_LOG_FILE
from .helper import (
    check_type,
    check_range,
    get_enum_value,
    check_is_positive,
    check_is_non_negative,
)
from .com_proxy import safe_com
from .errors import raise_synergy_error


class Synergy:
    """
    Wrapper for Synergy class of Moldflow Synergy.
    """

    def __init__(self, units=None, logging=True, log_file=False, log_file_name=DEFAULT_LOG_FILE):
        """
        Initialize the Synergy with a Synergy instance.
        Args:
            units: The system units to set. If None, uses the default units.
            logging: If True, enables logging to standard output.
            log_file: If True, enables file logging.
            log_file_name: The name of the log file. Defaults to moldflow.log
        """
        configure_file_logging(logging, log_file, log_file_name)
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Synergy")

        self.synergy = None
        synergy_env = os.environ.get("SAInstance")
        if synergy_env:
            try:
                synergy_getter = win32com.client.GetObject(synergy_env)
                self.synergy = safe_com(synergy_getter.GetSASynergy)
            except Exception:
                process_log(__name__, LogMessage.FAIL_INIT_WITH_ENV, value=synergy_env)

        if not self.synergy:
            try:
                self.synergy = safe_com(win32com.client.Dispatch("synergy.Synergy"))
            except Exception:
                raise_synergy_error()

        # Set Units
        if units is None:
            process_log(__name__, LogMessage.SYSTEM_USE, name="Units", value=self.units)
        else:
            self.units = units

        set_language(version=self.version)

    def silence(self, silence: bool) -> bool:
        """
        .. internal::
        Suppresses message boxes. Off by default.
        WARNING THIS IS INTENDED FOR INTERNAL USE ONLY. May be incomplete

        Args:
            silence (bool): True turns on suppression, False turns off suppression

        Returns:
            True if the operation is successful.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="silence")
        check_type(silence, bool)
        return self.synergy.Silence(silence)

    def new_project(self, name: str, path: str) -> bool:
        """
        Create a new project.

        Args:
            name (str): The name of the project.
            path (str): The location of the project.

        Returns:
            True if the project is created successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="new_project")
        check_type(name, str)
        check_type(path, str)
        return self.synergy.NewProject(name, path)

    def open_project(self, path: str) -> bool:
        """
        Open a project.

        Args:
            path (str): The location of the project.

        Returns:
            True if the project is opened successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="open_project")
        check_type(path, str)
        return self.synergy.OpenProject(path)

    def export_lmv_shared_views(self, collaboration_view_name: str) -> str:
        """
        Publishes active result plot to viewer.autodesk.com

        Args:
            collaboration_view_name (str): The shared view name.

        Returns:
            The TinyURL if successful, otherwise an empty string.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export_lmv_shared_views")
        check_type(collaboration_view_name, str)
        return self.synergy.ExportLMVSharedViews(collaboration_view_name)

    def open_archive(self, path: str, target: str) -> bool:
        """
        Open an archive file.

        Args:
            path (str): The location of the archive file.
            target (str): The target project to open where the archive will be extracted.

        Returns:
            True if successful.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="open_archive")
        check_type(path, str)
        check_type(target, str)
        return self.synergy.OpenArchive(path, target)

    def open_recent_project(self, index: int) -> bool:
        """
        Open a recent project.

        Args:
            index (int): The index of the recent project. [0 to 3]

        Returns:
            True if the project is opened successfully.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="open_recent_project")
        check_type(index, int)
        check_range(index, 0, 3, True, True)
        return self.synergy.OpenRecentProject(index)

    def import_file(
        self,
        file: str,
        import_options: ImportOptions = None,
        show_logs: bool = True,
        show_prompts: bool = False,
    ) -> bool:
        """
        Import a file.

        Args:
            file (str): The file to import.
            import_options (ImportOptions): The import options.
            show_logs (bool): Whether to show logs.
            show_prompts (bool): Whether to show prompts.

        Returns:
            True if the file is imported successfully.
        """

        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="import_file")
        check_type(file, str)
        if show_prompts and import_options is not None:
            process_log(__name__, LogMessage.IMPORT_FILE_PROMPTS, locals())
        if import_options is None:
            import_options = self.import_options
        check_type(import_options, ImportOptions)

        return self.synergy.ImportFile2(
            file, import_options.import_options, show_logs, show_prompts
        )

    def create_vector(self) -> Vector:
        """
        Create a Vector object.

        Returns:
            Vector: The Vector object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_vector")
        result = self.synergy.CreateVector
        if result is None:
            return None
        return Vector(result)

    def create_vector_array(self) -> VectorArray:
        """
        Create a VectorArray object.

        Returns:
            VectorArray: The VectorArray object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_vector_array")
        result = self.synergy.CreateVectorArray
        if result is None:
            return None
        return VectorArray(result)

    def create_double_array(self) -> DoubleArray:
        """
        Create a DoubleArray object.

        Returns:
            DoubleArray: The DoubleArray object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_double_array")
        result = self.synergy.CreateDoubleArray
        if result is None:
            return None
        return DoubleArray(result)

    def create_integer_array(self) -> IntegerArray:
        """
        Create a IntegerArray object.

        Returns:
            IntegerArray: The IntegerArray object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_integer_array")
        result = self.synergy.CreateIntegerArray
        if result is None:
            return None
        return IntegerArray(result)

    def create_string_array(self) -> StringArray:
        """
        Create a StringArray instance.

        Returns:
            StringArray: The StringArray object.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_string_array")
        result = self.synergy.CreateStringArray
        if result is None:
            return None
        return StringArray(result)

    @property
    def units(self) -> str:
        """
        Get the system units.

        :getter: Get the system units.
        :setter: Set the system units.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="units")
        return self.synergy.GetUnits

    @units.setter
    def units(self, value: SystemUnits | str) -> None:
        """
        Set the system units.

        Args:
            value: The system units to set. Can be a SystemUnits enum or a string.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="units", value=value)
        value = get_enum_value(value, SystemUnits)
        self.synergy.SetUnits(value)

    def set_application_window_pos(self, x: int, y: int, size_x: int, size_y: int) -> bool:
        """
        Set the position and size of the application window.

        Args:
            x (int): The x-coordinate of the top-left corner of the window.
            y (int): The y-coordinate of the top-left corner of the window.
            size_x (int): The width of the window.
            size_y (int): The height of the window.

        Returns:
            True if successful, otherwise False.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_application_window_pos")
        check_type(x, int)
        check_is_non_negative(x)
        check_type(y, int)
        check_is_non_negative(y)
        check_type(size_x, int)
        check_is_positive(size_x)
        check_type(size_y, int)
        check_is_positive(size_y)
        return self.synergy.SetApplicationWindowPos(x, y, size_x, size_y)

    def quit(self, prompt_save: bool) -> None:
        """
        Quit the Synergy application.

        Args:
            prompt_save (bool): To prompt to save the changes or not.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="quit")
        check_type(prompt_save, bool)
        self.synergy.Quit(prompt_save)
        self.synergy = None

    def get_material_selector_with_index(self, index: int) -> MaterialSelector:
        """
        Get the MaterialSelector object with the given index.

        Args:
            index (int): The index of the material selector.

        Returns:
            The MaterialSelector object.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_material_selector_with_index"
        )
        check_type(index, int)
        result = self.synergy.GetMaterialSelectorWithIndex(index)
        if result is None:
            return None
        return MaterialSelector(result)

    @property
    def boundary_conditions(self) -> BoundaryConditions:
        """
        Get the BoundaryConditions object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="boundary_conditions")
        result = self.synergy.BoundaryConditions
        if result is None:
            return None
        return BoundaryConditions(result)

    @property
    def cad_manager(self) -> CADManager:
        """
        Get the CADManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="cad_manager")
        result = self.synergy.CADManager
        if result is None:
            return None
        return CADManager(result)

    @property
    def circuit_generator(self) -> CircuitGenerator:
        """
        Get the CircuitGenerator object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="circuit_generator")
        result = self.synergy.CircuitGenerator
        if result is None:
            return None
        return CircuitGenerator(result)

    @property
    def data_transform(self) -> DataTransform:
        """
        Get the DataTransform object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="data_transform")
        result = self.synergy.DataTransform
        if result is None:
            return None
        return DataTransform(result)

    @property
    def diagnosis_manager(self) -> DiagnosisManager:
        """
        Get the DiagnosisManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="diagnosis_manager")
        result = self.synergy.DiagnosisManager
        if result is None:
            return None
        return DiagnosisManager(result)

    @property
    def folder_manager(self) -> FolderManager:
        """
        Get the FolderManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="folder_manager")
        result = self.synergy.FolderManager
        if result is None:
            return None
        return FolderManager(result)

    @property
    def import_options(self) -> ImportOptions:
        """
        Get the ImportOptions object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="import_options")
        result = self.synergy.ImportOptions
        if result is None:
            return None
        return ImportOptions(result)

    @property
    def layer_manager(self) -> LayerManager:
        """
        Get the LayerManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="layer_manager")
        result = self.synergy.LayerManager
        if result is None:
            return None
        return LayerManager(result)

    @property
    def material_finder(self) -> MaterialFinder:
        """
        Get the MaterialFinder object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="material_finder")
        result = self.synergy.MaterialFinder
        if result is None:
            return None
        return MaterialFinder(result)

    @property
    def material_selector(self) -> MaterialSelector:
        """
        Get the MaterialSelector object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="material_selector")
        result = self.synergy.MaterialSelector
        if result is None:
            return None
        return MaterialSelector(result)

    @property
    def mesh_editor(self) -> MeshEditor:
        """
        Get the MeshEditor object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_editor")
        result = self.synergy.MeshEditor
        if result is None:
            return None
        return MeshEditor(result)

    @property
    def mesh_generator(self) -> MeshGenerator:
        """
        Get the MeshGenerator object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_generator")
        result = self.synergy.MeshGenerator
        if result is None:
            return None
        return MeshGenerator(result)

    @property
    def model_duplicator(self) -> ModelDuplicator:
        """
        Get the ModelDuplicator object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="model_duplicator")
        result = self.synergy.ModelDuplicator
        if result is None:
            return None
        return ModelDuplicator(result)

    @property
    def modeler(self) -> Modeler:
        """
        Get the Modeler object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="modeler")
        result = self.synergy.Modeler
        if result is None:
            return None
        return Modeler(result)

    @property
    def mold_surface_generator(self) -> MoldSurfaceGenerator:
        """
        Get the MoldSurfaceGenerator object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mold_surface_generator")
        result = self.synergy.MoldSurfaceGenerator
        if result is None:
            return None
        return MoldSurfaceGenerator(result)

    @property
    def plot_manager(self) -> PlotManager:
        """
        Get the PlotManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="plot_manager")
        result = self.synergy.PlotManager
        if result is None:
            return None
        return PlotManager(result)

    @property
    def predicate_manager(self) -> PredicateManager:
        """
        Get the PredicateManager object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="predicate_manager")
        result = self.synergy.PredicateManager
        if result is None:
            return None
        return PredicateManager(result)

    @property
    def property_editor(self) -> PropertyEditor:
        """
        Get the PropertyEditor object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="property_editor")
        result = self.synergy.PropertyEditor
        if result is None:
            return None
        return PropertyEditor(result)

    @property
    def project(self) -> Project:
        """
        Get the Project object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="project")
        result = self.synergy.Project
        if result is None:
            return None
        return Project(result)

    @property
    def runner_generator(self) -> RunnerGenerator:
        """
        Get the RunnerGenerator object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="runner_generator")
        result = self.synergy.RunnerGenerator
        if result is None:
            return None
        return RunnerGenerator(result)

    @property
    def study_doc(self) -> StudyDoc:
        """
        Get the StudyDoc object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="study_doc")
        result = self.synergy.StudyDoc
        if result is None:
            return None
        return StudyDoc(result)

    @property
    def system_message(self) -> SystemMessage:
        """
        Get the SystemMessage object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="system_message")
        result = self.synergy.SystemMessage
        if result is None:
            return None
        return SystemMessage(result)

    @property
    def unit_conversion(self) -> UnitConversion:
        """
        Get the UnitConversion object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="unit_conversion")
        result = self.synergy.UnitConversion
        if result is None:
            return None
        return UnitConversion(result)

    @property
    def viewer(self) -> Viewer:
        """
        Get the Viewer object.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="viewer")
        result = self.synergy.Viewer
        if result is None:
            return None
        return Viewer(result)

    @property
    def build(self) -> str:
        """
        Get the build version of the Synergy application.

        :getter: Get the build version.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="build")
        return self.synergy.Build

    @property
    def build_number(self) -> str:
        """
        Get the build number of the Synergy application.

        :getter: Get the build number.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="build_number")
        return self.synergy.BuildNumber

    @property
    def edition(self) -> str:
        """
        Get the edition of the Synergy application.

        :getter: Get the edition.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="edition")
        return self.synergy.Edition

    @property
    def version(self) -> str:
        """
        Get the version of the Synergy application.

        :getter: Get the version.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="version")
        return self.synergy.Version
