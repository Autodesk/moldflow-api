# SPDX-FileCopyrightText: 2024 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Moldflow API Library

A Python wrapper for the Autodesk Moldflow Synergy API.
"""

from .boundary_conditions import BoundaryConditions
from .boundary_list import BoundaryList
from .cad_manager import CADManager
from .circuit_generator import CircuitGenerator
from .data_transform import DataTransform
from .diagnosis_manager import DiagnosisManager
from .double_array import DoubleArray
from .ent_list import EntList
from .folder_manager import FolderManager
from .import_options import ImportOptions
from .integer_array import IntegerArray
from .layer_manager import LayerManager
from .material_finder import MaterialFinder
from .material_plot import MaterialPlot
from .material_selector import MaterialSelector
from .mesh_editor import MeshEditor
from .mesh_generator import MeshGenerator
from .mesh_summary import MeshSummary
from .model_duplicator import ModelDuplicator
from .modeler import Modeler
from .mold_surface_generator import MoldSurfaceGenerator
from .plot import Plot
from .plot_manager import PlotManager
from .predicate import Predicate
from .predicate_manager import PredicateManager
from .project import Project
from .prop import Property
from .property_editor import PropertyEditor
from .runner_generator import RunnerGenerator
from .server import Server
from .string_array import StringArray
from .study_doc import StudyDoc
from .synergy import Synergy
from .system_message import SystemMessage
from .unit_conversion import UnitConversion
from .user_plot import UserPlot
from .vector import Vector
from .vector_array import VectorArray
from .viewer import Viewer

from .common import AnalysisType
from .common import BirefringenceResultType
from .common import AnimationType
from .common import AnimationSpeed
from .common import CADBodyProperty
from .common import CADContactMesh
from .common import ClampForcePlotDirection
from .common import ColorScaleOptions
from .common import ColorTableIDs
from .common import CommitActions
from .common import ConstraintType
from .common import CoolType
from .common import CrossSectionType
from .common import CurveInitPosition
from .common import DeflectionType
from .common import DeflectionScaleDirections
from .common import DisplayComponent
from .common import DisplayOption
from .common import DuplicateOption
from .common import EdgeDisplayOptions
from .common import EntityType
from .common import GradingFactor
from .common import GeomType
from .common import ImportUnitIndex
from .common import ImportUnits
from .common import ItemType
from .common import LCSType
from .common import MaterialDatabase
from .common import MaterialDatabaseType
from .common import MaterialIndex
from .common import Mesher3DType
from .common import MoldingProcess
from .common import MDLContactMeshType
from .common import MDLKernel
from .common import MeshType
from .common import ModulusPlotDirection
from .common import NurbsAlgorithm
from .common import PlotMethod
from .common import PlotType
from .common import PropertyType
from .common import ScaleOptions
from .common import ScaleTypes
from .common import ShrinkageCompensationOptions
from .common import SliceAtProbeOptions
from .common import StandardViews
from .common import SystemUnits
from .common import TensorAxisRatioOptions
from .common import TraceModes
from .common import TraceStyles
from .common import TransformFunctions
from .common import TransformOperations
from .common import TransformScalarOperations
from .common import TriClassification
from .common import ViewModes
from .common import UserPlotType

from .message_box import (
    MessageBox,
    MessageBoxType,
    MessageBoxResult,
    MessageBoxOptions,
    MessageBoxIcon,
    MessageBoxModality,
    MessageBoxDefaultButton,
    MessageBoxReturn,
)

# Version checking and update functionality
from .version_check import get_version, check_for_updates_on_import

# Check for updates on import unless disabled
check_for_updates_on_import()

# Version of the package
__version__ = get_version()
