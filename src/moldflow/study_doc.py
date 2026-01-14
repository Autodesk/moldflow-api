# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    StudyDoc Class API Wrapper
"""

from .ent_list import EntList
from .import_options import ImportOptions
from .logger import process_log
from .helper import (
    check_type,
    check_optional_type,
    coerce_optional_dispatch,
    check_and_coerce_optional,
    check_file_extension,
    check_range,
    get_enum_value,
    check_is_non_negative,
)
from .com_proxy import safe_com
from .common import LogMessage, MoldingProcess, MeshType
from .constants import UDM_FILE_EXT
from .vector import Vector
from .string_array import StringArray


class StudyDoc:
    """
    Wrapper for StudyDoc class of Moldflow Synergy.
    """

    def __init__(self, _study_doc):
        """
        Initialize the StudyDoc with a StudyDoc instance from COM.

        Args:
            _study_doc: The StudyDoc instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="StudyDoc")
        self.study_doc = safe_com(_study_doc)

    def create_entity_list(self) -> EntList:
        """
        Creates a new entity list.

        Returns:
            EntList: A new entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.study_doc.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    @property
    def molding_process(self) -> str:
        """
        Value of Molding Process.

        :getter: Get value of Molding Process
        :setter: Set value of Molding Process
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="molding_process")
        return self.study_doc.MoldingProcess

    @molding_process.setter
    def molding_process(self, value: str | MoldingProcess) -> None:
        """
        Set molding process
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="molding_process", value=value
        )
        value = get_enum_value(value, MoldingProcess)
        self.study_doc.MoldingProcess = value

    @property
    def analysis_sequence(self) -> str:
        """
        Value of Analysis Sequence.

        :getter: Get value of Analysis Sequence
        :setter: Set value of Analysis Sequence
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="analysis_sequence")
        return self.study_doc.AnalysisSequence

    @analysis_sequence.setter
    def analysis_sequence(self, value: str):
        """
        Set analysis sequence
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="analysis_sequence", value=value
        )
        check_type(value, str)
        self.study_doc.AnalysisSequence = value

    @property
    def analysis_sequence_description(self) -> str:
        """
        Value of Analysis Sequence Description.

        :getter: Get value of Analysis Sequence Description
        :setter: Set value of Analysis Sequence Description
        :type: str
        """
        process_log(
            __name__, LogMessage.PROPERTY_GET, locals(), name="analysis_sequence_description"
        )
        return self.study_doc.AnalysisSequenceDescription

    @property
    def mesh_type(self) -> str:
        """
        Value of Mesh Type.

        :getter: Get value of Mesh Type
        :setter: Set value of Mesh Type
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_type")
        return self.study_doc.MeshType

    @mesh_type.setter
    def mesh_type(self, value: MeshType | str) -> None:
        """
        Set mesh type
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="mesh_type", value=value)
        value = get_enum_value(value, MeshType)
        self.study_doc.MeshType = value

    @property
    def selection(self) -> EntList:
        """
        Value of Selection.

        :getter: Get value of Selection
        :setter: Set value of Selection
        :type: EntList
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="selection")
        result = self.study_doc.Selection
        if result is None:
            return None
        return EntList(result)

    @selection.setter
    def selection(self, value: EntList | None) -> None:
        """
        Set selection
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="selection", value=value)

        self.study_doc.Selection = check_and_coerce_optional(value, EntList)

    @property
    def number_of_analyses(self) -> int:
        """
        Value of Number of Analyses.

        :getter: Get value of Number of Analyses
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="number_of_analysis")
        return self.study_doc.NumberOfAnalyses

    @property
    def study_name(self) -> str:
        """
        Value of Study Name.

        :getter: Get value of Study Name
        :setter: Set value of Study Name
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="study_name")
        return self.study_doc.StudyName

    def save(self) -> bool:
        """
        Saves the study

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save")
        return self.study_doc.Save

    def save_as(self, name: str) -> bool:
        """
        Saves the study under a new name

        Args:
            name (str): New study name

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_as")
        check_type(name, str)
        return self.study_doc.SaveAs(name)

    def close(self, show_prompt: bool = True) -> bool:
        """
        Closes the study

        Args:
            show_prompt (bool): Prompt to save changes or not (default: None)

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="close")
        check_type(show_prompt, bool)
        result = self.study_doc.Close2(show_prompt)
        if result:
            self.study_doc = None
        return result

    def undo(self, num: int) -> bool:
        """
        Undoes a number of model edit

        Args:
            num (int): Number of undo steps

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="undo")
        check_type(num, int)
        return self.study_doc.Undo(num)

    def redo(self, num: int) -> bool:
        """
        Redoes a number of model editing

        Args:
            num (int): Number of redo steps

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="redo")
        check_type(num, int)
        return self.study_doc.Redo(num)

    def add_file(self, name: str, opts: ImportOptions | None, show_logs: bool) -> bool:
        """
        Adds a CAD model file to the current study

        Args:
            name (str): Name of the file to add
            opts (ImportOptions | None): Import options for the file
            show_logs (bool): True if display logs

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_file")
        check_type(name, str)
        check_optional_type(opts, ImportOptions)
        check_type(show_logs, bool)
        return self.study_doc.AddFile(
            name, coerce_optional_dispatch(opts, "import_options"), show_logs
        )

    def analyze_now(self, check: bool, solve: bool, prompts: bool = False) -> bool:
        """
        Runs analysis immediately

        Args:
            check (bool): True if check only
            solve (bool): True if solve only
            prompts (bool): True if display prompts

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="analyze_now")
        check_type(check, bool)
        check_type(solve, bool)
        check_type(prompts, bool)
        return self.study_doc.AnalyzeNow2(check, solve, prompts)

    def get_first_node(self) -> EntList:
        """
        Gets the first node in the study

        Returns:
            EntList: The first node in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_node")
        result = self.study_doc.GetFirstNode
        if result is None:
            return None
        return EntList(result)

    def get_next_node(self, node: EntList | None) -> EntList:
        """
        Gets the next node in the study

        Args:
            node (EntList | None): The current node

        Returns:
            EntList: The next node in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_node")

        result = self.study_doc.GetNextNode(check_and_coerce_optional(node, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_node_coord(self, node: EntList | None) -> Vector:
        """
        Gets node coordinates

        Args:
            node (EntList | None): The current node

        Returns:
            Vector: The coordinates of the node
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_node_coord")

        result = self.study_doc.GetNodeCoord(check_and_coerce_optional(node, EntList))
        if result is None:
            return None
        return Vector(result)

    def get_first_tri(self) -> EntList:
        """
        Gets the first triangle in the study

        Returns:
            EntList: The first triangle in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_tri")
        result = self.study_doc.GetFirstTri
        if result is None:
            return None
        return EntList(result)

    def get_next_tri(self, tri: EntList | None) -> EntList:
        """
        Gets the next triangle in the study

        Args:
            tri (EntList | None): The current triangle

        Returns:
            EntList: The next triangle in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_tri")

        result = self.study_doc.GetNextTri(check_and_coerce_optional(tri, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_first_beam(self) -> EntList:
        """
        Gets the first beam in the study

        Returns:
            EntList: The first beam in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_beam")
        result = self.study_doc.GetFirstBeam
        if result is None:
            return None
        return EntList(result)

    def get_next_beam(self, beam: EntList | None) -> EntList:
        """
        Gets the next beam in the study

        Args:
            beam (EntList | None): The current beam

        Returns:
            EntList: The next beam in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_beam")

        result = self.study_doc.GetNextBeam(check_and_coerce_optional(beam, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_first_tet(self) -> EntList:
        """
        Gets the first tetrahedral element in the study

        Returns:
            EntList: The first tetrahedral element in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_tet")
        result = self.study_doc.GetFirstTet
        if result is None:
            return None
        return EntList(result)

    def get_next_tet(self, tet: EntList | None) -> EntList:
        """
        Gets the next tetrahedral element in the study

        Args:
            tet (EntList | None): The current tetrahedral element

        Returns:
            EntList: The next tetrahedral element in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_tet")

        result = self.study_doc.GetNextTet(check_and_coerce_optional(tet, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_elem_nodes(self, elem: EntList | None) -> EntList:
        """
        Gets the nodes of an element

        Args:
            elem (EntList | None): The element to get nodes from

        Returns:
            EntList: The nodes of the element
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_elem_nodes")

        result = self.study_doc.GetElemNodes(check_and_coerce_optional(elem, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_entity_layer(self, ent: EntList | None) -> EntList:
        """
        Gets the layer that the entity is assigned to

        Args:
            ent (EntList | None): The entity to get layer

        Returns:
            EntList: The layer of the entity
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_entity_layer")

        result = self.study_doc.GetEntityLayer(check_and_coerce_optional(ent, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_entity_id(self, ent: EntList | None) -> int:
        """
        Gets entity ID

        Args:
            ent (EntList | None): The entity

        Returns:
            int: The ID of the entity
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_entity_id")

        return self.study_doc.GetEntityID(check_and_coerce_optional(ent, EntList))

    def get_first_curve(self) -> EntList:
        """
        Gets the first curve in the study

        Returns:
            EntList: The first curve in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_curve")
        result = self.study_doc.GetFirstCurve
        if result is None:
            return None
        return EntList(result)

    def get_next_curve(self, curve: EntList | None) -> EntList:
        """
        Gets the next curve in the study

        Args:
            curve (EntList | None): The current curve

        Returns:
            EntList: The next curve in the study
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_curve")

        result = self.study_doc.GetNextCurve(check_and_coerce_optional(curve, EntList))
        if result is None:
            return None
        return EntList(result)

    def get_curve_point(self, curve: EntList | None, pos_curve: float) -> Vector:
        """
        Gets a specified point on the curve

        Args:
            curve (EntList | None): The curve to get point from
            pos_curve (float): The position on the curve

        Returns:
            Vector: The point on the curve
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_curve_point")

        check_type(pos_curve, (int, float))
        check_range(pos_curve, 0, 1, True, True)
        result = self.study_doc.GetCurvePoint(check_and_coerce_optional(curve, EntList), pos_curve)
        if result is None:
            return None
        return Vector(result)

    def delete_results(self, index: int) -> bool:
        """
        Deletes results starting from the given index

        Args:
            index (int): Start index of results to be deleted

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_results")
        check_type(index, int)
        return self.study_doc.DeleteResults(index)

    def mesh_now(self, show_prompts: bool) -> bool:
        """
        Runs mesh immediately

        Args:
            show_prompts (bool): True if display prompts

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="mesh_now")
        check_type(show_prompts, bool)
        return self.study_doc.MeshNow(show_prompts)

    def get_result_prefix(self, name: str) -> str:
        """
        Gets result prefix string of a given process

        Args:
            name (str): The name of the process

        Returns:
            str: The result prefix of the process
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_result_prefix")
        check_type(name, str)
        return self.study_doc.GetResultPrefix(name)

    def import_process_variation(self, file: str, doe: bool, show_prompt: bool) -> bool:
        """
        Import process variation from MPX/Shotscope

        Args:
            file (str): udm file from MPX/Shotscope
            doe (bool): True if set up DOE analysis
            show_prompt (bool): True if display prompt

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="import_process_variation")
        check_type(file, str)
        check_type(doe, bool)
        check_type(show_prompt, bool)
        file = check_file_extension(file, UDM_FILE_EXT)
        return self.study_doc.ImportProcessVariation(file, doe, show_prompt)

    def import_process_condition(self, file: str, show_prompt: bool) -> bool:
        """
        Import process condition from MPX

        Args:
            file (str): udm file from MPX
            show_prompt (bool): True if display prompt

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="import_process_condition")
        check_type(file, str)
        check_type(show_prompt, bool)
        file = check_file_extension(file, UDM_FILE_EXT)
        return self.study_doc.ImportProcessCondition(file, show_prompt)

    def export_analysis_log(self, file: str) -> bool:
        """
        Export analysis log to text file

        Args:
            file (str): File name to export analysis log

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export_analysis_log")
        check_type(file, str)
        # file = file if file.endswith(".log") else f"{file}.log"
        return self.study_doc.ExportAnalysisLog(file)

    def export_mesh_log(self, file: str) -> bool:
        """
        Export mesh log to text file

        Args:
            file (str): File name to export mesh log

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="export_mesh_log")
        check_type(file, str)
        return self.study_doc.ExportMeshLog(file)

    def mark_analysis_summary_for_export(self, marking: bool) -> None:
        """
        Marks the summary for export

        Args:
            marking (bool): True if mark for export

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="mark_analysis_summary_for_export"
        )
        check_type(marking, bool)
        self.study_doc.MarkAnalysisSummaryForExport(marking)

    def get_part_cad_names(self) -> StringArray:
        """
        Return the names of all cad models as a string array

        Returns:
            StringArray: The names of all cad models
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_part_cad_names")
        result = self.study_doc.GetPartCadNames
        if result is None:
            return None
        return StringArray(result)

    @property
    def notes(self) -> str:
        """
        Gets study notes
        :getter: Get study notes
        :setter: Set study notes
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="notes")
        return self.study_doc.GetNotes

    @notes.setter
    def notes(self, note: str) -> None:
        """
        Sets study notes

        Args:
            note: Notes to be set

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="notes", value=note)
        check_type(note, str)
        self.study_doc.SetNotes(note)

    def analysis_status(self, index: int) -> str:
        """
        Gets the status of the analysis at the given index

        Args:
            index (int): Index of the analysis

        Returns:
            str: The status of the analysis
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="analysis_status")
        check_type(index, int)
        check_is_non_negative(index)
        return self.study_doc.AnalysisStatus(index)

    def analysis_name(self, index: int) -> str:
        """
        Gets the name of the analysis at the given index

        Args:
            index (int): Index of the analysis

        Returns:
            str: The name of the analysis
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="analysis_name")
        check_type(index, int)
        check_is_non_negative(index)
        return self.study_doc.AnalysisName(index)

    def mesh_status(self) -> str:
        """
        Gets the status of the mesh at the given index

        Args:
            index: Index of the mesh

        Returns:
            str: The status of the mesh
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="mesh_status")
        return self.study_doc.MeshStatus

    def is_analysis_running(self) -> bool:
        """
        Checks if the analysis is currently running

        Returns:
            bool: True if the analysis is running, False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="is_analysis_running")
        return self.study_doc.IsAnalysisRunning
