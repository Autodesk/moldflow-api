# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Enums for Moldflow API
"""

import logging
from enum import Enum


class MaterialDatabase(Enum):
    """
    Enum for different material database with IDs.
    """

    COOLANT = 20010
    MOLD_MATERIAL = 20020
    THERMOSET_MATERIAL = 20030
    UNDERFILL_ENCAPSULANT = 20034
    PREFORM = 20040
    WIRE_MATERIAL = 20060
    LEADFRAME_MATERIAL = 20070
    THERMOPLASTIC = 21000
    FILLER_PROPERTIES = 21200
    MUCELL_MATERIAL_PROPERTIES = 21300
    INJECTION_MOLDING_MACHINE = 30007


class MaterialDatabaseType(Enum):
    """
    Enum for different material database types.
    """

    SYSTEM = "System"
    USER = "User"


class CrossSectionType(Enum):
    """
    Enum for different cross-section type
    """

    CIRCULAR = "Circular"
    RECTANGULAR = "Rectangular"
    ANNULAR = "Annular"
    HALF_CIRCULAR = "Half-Circular"
    U_SHAPE = "U-shape"
    TRAPEZOIDAL = "Trapezoidal"


class MeshType(Enum):
    """
    Enum for different mesh types.
    """

    MESH_MIDPLANE = "Midplane"
    MESH_FUSION = "Fusion"
    MESH_3D = "3D"


class ImportUnits(Enum):
    """
    Enum for ImportUnits
    """

    MM = "mm"
    CM = "cm"
    M = "m"
    IN = "in"


class ImportUnitIndex(Enum):
    """
    Enum for ImportUnits
    """

    MM = 0
    CM = 1
    M = 2
    IN = 3


class MDLKernel(Enum):
    """
    Enum for MDLKernel
    """

    PARAMETRIC = "Parametric"
    PARASOLID = "Parasolid"


class MDLContactMeshType(Enum):
    """
    Enum for MDLContactMeshType
    """

    PRECISE_MATCH = "Precise match"
    FAULT_TOLERANCE = "Fault tolerant"
    IGNORE_CONTACT = "Ignore contact"


class CADBodyProperty(Enum):
    """
    Enum for CADBodyProperty
    """

    PROPERTY_CAD_COMPONENT = 0
    PROPERTY_3D_CHANNEL = 40915
    PROPERTY_MOLD_COMPONENT = 40912


class ItemType(Enum):
    """
    Enum for ItemType
    """

    STUDY = "Study"
    REPORT = "Report"
    FOLDER = "Folder"


class DuplicateOption(Enum):
    """
    Enum for DuplicateOption
    """

    COMPLETE_COPY_OF_RESULTS_FILES = 0
    NO_RESULTS_FILES_INCLUDED = 1
    INCLUDE_RESULT_FILES_LINKED_TO_ORIGINAL = 2


class SystemUnits(Enum):
    """
    System of units
    """

    METRIC = "Metric"
    ENGLISH = "English"
    STANDARD = "SI"


class ErrorMessage(Enum):
    """
    Enum for error messages.
    """

    TYPE_ERROR = "Invalid Type: must be {expected_types}, not {variable_type}"
    VALUE_ERROR = "Invalid Value: {reason}"
    INDEX_ERROR = "Invalid Index: out of range"
    SAVE_ERROR = "Save Error: Failed to save {saving} to {file_name}"
    ATTRIBUTE_ERROR = "Invalid Attribute: {attribute} is not supported"
    SYNERGY_ERROR = "Failed to initialize Synergy: Synergy not found"


class LogMessage(Enum):
    """
    Enum for translated messages.
    """

    # Debug Logs
    CLASS_INIT = ("Initializing {name}", logging.DEBUG)
    HELPER_CHECK = ("Checking {value} is {name}", logging.DEBUG)
    LANG_METHOD = ("Using {method} {product_key} for locale", logging.DEBUG)
    PROPERTY_GET = ("Getting {name}", logging.DEBUG)
    PROPERTY_PARAM_GET = ("Getting {name} at index {value}", logging.DEBUG)
    VALID_TYPE = ("Valid Input Type", logging.DEBUG)
    VALID_INPUT = ("Valid Input", logging.DEBUG)
    CHECK_RANGE = ("Checking {value} is in range {min_value} to {max_value}", logging.DEBUG)
    CHECK_MIN = ("Checking {value} is greater than {min_value}", logging.DEBUG)
    CHECK_MAX = ("Checking {value} is less than {max_value}", logging.DEBUG)
    CHECK_NON_NEGATIVE = ("Checking {value} is non-negative", logging.DEBUG)
    CHECK_POSITIVE = ("Checking {value} is positive", logging.DEBUG)
    CHECK_NON_ZERO = ("Checking {value} is non-zero", logging.DEBUG)
    CHECK_NEGATIVE = ("Checking {value} is negative", logging.DEBUG)
    CHECK_INDEX_IN_RANGE = ("Checking index {index} is in range", logging.DEBUG)
    CHECK_FILE_EXTENSION = ("Checking file extension {file_name}", logging.DEBUG)
    CHECK_EXPECTED_VALUES = ("Checking {value} is in expected values", logging.DEBUG)
    FAIL_INIT_WITH_ENV = (
        "Could not initialize with Instance ID: {value}",
        logging.DEBUG,
    )  # Fail initialization with environment variable (SAInstance)
    # Info Logs
    FUNCTION_CALL = ("Executing {name}", logging.INFO)
    PROPERTY_SET = ("Setting {name} to {value}", logging.INFO)
    SYSTEM_SET = ("Setting {name} to {value}", logging.INFO)
    SYSTEM_USE = ("{name} is {value}", logging.INFO)
    # Warning
    NOT_APPLICABLE = ("{name} parameter will be ignored", logging.WARNING)
    VALUE_NOT_IN_ENUM = (
        "{value} cannot be found documented in {enum_name}, this may cause function call to fail",
        logging.WARNING,
    )
    INVALID_FILE_EXTENSION = (
        "{file_name} does not have a valid file extension, will use {default}",
        logging.WARNING,
    )
    IMPORT_FILE_PROMPTS = (
        "Using prompts will use pop-up import options instead of the ones provided.",
        logging.WARNING,
    )
    NONE_LOGGER = ("Logger was not setup", logging.WARNING)
    # Critical logs


class ValueErrorReason(Enum):
    """Reasons for raising a ValueError."""

    EMPTY = "cannot be empty"
    INVALID_ENUM_VALUE = "{value} is not a valid {enum_name}"
    POSITIVE = "found {value}, must be positive"
    NON_NEGATIVE = "found {value}, must be non-negative"
    NON_ZERO = "found {value}, must be non-zero"
    NEGATIVE = "found {value}, must be positive"
    GREATER_THAN = "found {value}, must be greater than {min_value}"
    GREATER_THAN_OR_EQUAL = "found {value}, must be greater than or equal to {min_value}"
    LESS_THAN = "found {value}, must be less than {max_value}"
    LESS_THAN_OR_EQUAL = "found {value}, must be less than or equal to {max_value}"
    NOT_IN_RANGE = "found {value}, must be between {min_value} and {max_value}"
    MIN_MORE_THAN_MAX = "found {min_value} must be less than {max_value}"
    INVALID_FILE_EXTENSION = "{value} does not have a valid file extension, must be {extensions}"
    INVALID_VALUE = "found {value}, must be one of {expected_values}"
    BOTH_PARAMETERS_REQUIRED = "both {first} and {second} must be provided together"


class MoldingProcess(Enum):
    """Type of molding process"""

    THERMOPLASTIC_INJECTION_MOLDING = "Thermoplastic Injection Molding"
    MULTIPLE_BARREL_THERMOPLASTICS_INJECTION_MOLDING = (
        "Multiple-Barrel Thermoplastics Injection Molding"
    )
    THERMOPLASTICS_OVERMOLDING = "Thermoplastics Overmolding"
    THERMOPLASTICS_BI_INJECTION_MOLDING = "Thermoplastics Bi-injection Molding"
    GAS_ASSISTED_INJECTION_MOLDING = "Gas-Assisted Injection Molding"
    CO_INJECTION_MOLDING = "Co-injection Molding"
    THERMOPLASTICS_INJECTION_COMPRESSION_MOLDING = "Thermoplastics Injection-Compression Molding"
    REACTIVE_INJECTION_COMPRESSION_MOLDING = "Reactive Injection-Compression Molding"
    REACTIVE_MOLDING = "Reactive Molding"
    MICROCHIP_ENCAPSULATION = "Microchip Encapsulation"
    THERMOPLASTICS_MICROCELLULAR_INJECTION_MOLDING = (
        "Thermoplastics Microcellular Injection Molding"
    )
    RTM_OR_SRIM = "RTM or SRIM"
    UNDERFILL_ENCAPSULATION = "Underfill Encapsulation"
    MULTIPLE_BARREL_REACTIVE_MOLDING = "Multiple-Barrel Reactive Molding"
    COOLANT_FLOW = "Coolant Flow"


class MaterialIndex(Enum):
    """
    Enum for different material index.
    """

    FIRST = 0
    SECOND = 1


class EntityType(Enum):
    """
    Enum for EntityType
    """

    NODE = "N"
    BEAM = "B"
    TRIANGLE = "T"
    CURVE = "C"
    FACE = "F"
    SURFACE = "S"
    REGION = "R"
    NDBC = "NBC"
    SUBC = "SBC"
    LCS = "LCS"
    TET4 = "TE"
    STL = "STL"


class DisplayOption(Enum):
    """
    Enum for DisplayOption
    """

    SOLID = "Solid"
    SOLID_PLUS_ELEMENT_EDGES = "Solid+Element Edges"
    TRANSPARENT = "Transparent"
    TRANSPARENT_PLUS_ELEMENT_EDGES = "Transparent + Element Edges"
    SHRUNKEN = "Shrunken"
    AXIS_LINE_ONLY = "Axis Line Only"
    POINT = "Point"
    TRIAD = "Triad"
    NET = "Net"
    SOLID_PLUS_NET = "Solid + Net"
    TRANSPARENT_PLUS_NET = "Transparent + Net"


class AnalysisType(Enum):
    """
    Enum for AnalysisType
    """

    STRESS = 1
    WARP = 2
    STRESS_WARP = 3
    CORE_SHIFT = 4


class ConstraintType(Enum):
    """
    Enum for ConstraintType
    """

    FIXED = 1
    FREE = 2
    SPECIFIC = 3


class TransformFunctions(Enum):
    """
    Enum for TransformFunctions
    """

    SINE = "sin"
    COSINE = "cos"
    TANGENT = "tan"
    ABSOLUTE = "abs"
    EXPONENT = "exp"
    NEAREST_INT = "nint"
    SIGN = "sign"
    LOGARITHM = "log"
    SQUARE_ROOT = "sqrt"


class TransformOperations(Enum):
    """
    Enum for TransformOperations
    """

    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


class TransformScalarOperations(Enum):
    """
    Enum for TransformScalarOperations
    """

    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POST_DIVIDE = "/="
    POST_MINUS = "-="


class CommitActions(Enum):
    """
    Enum for CommitActions
    """

    ASSIGN = "Assign"
    EDIT = "Edit"
    PROCESS_CONDITIONS = "Process Conditions"
    REMOVE_UNUSED = "Remove Unused"


class NurbsAlgorithm(Enum):
    """
    Enum for NurbsMesher
    """

    DEFAULT = 0
    ADVANCING_FRONT = 1


class CoolType(Enum):
    """
    Enum for CoolType
    """

    BEM = 1
    FEM = 2


class TriClassification(Enum):
    """
    Enum for TriClassification
    """

    IGNORE = 0
    PRESERVE_NOT_SLIVER = 1
    PRESERVE_ALL = 2


class GeomType(Enum):
    """
    Enum for GeomType
    """

    AUTO_DETECT = "Auto-Detect"
    FUSION = "Fusion"
    MIDPLANE = "Midplane"


class Mesher3DType(Enum):
    """
    Enum for Mesher3DType
    """

    ADVANCING_FRONT = "AdvancingFront"
    LEGACY = "Legacy"
    ADVANCING_LAYERS = "AdvancingLayers"


class CADContactMesh(Enum):
    """
    Enum for CADContactMesh
    """

    PRECISE_MATCH = "Precise match"
    FAULT_TOLERANCE = "Fault tolerant"
    IGNORE_CONTACT = "Ignore contact"


class UserPlotType(Enum):
    """
    Enum for UserPlotType
    """

    ELEMENT_DATA = "ELDT"
    NODE_DATA = "NDDT"
    NON_MESH_DATA = "NMDT"


class BirefringenceResultType(Enum):
    """
    Enum for BirefringenceResultType
    """

    PHASE_SHIFT = 0
    RETARDATION = 1
    RETARDANCE_TENSOR = 2
    FRINGE_PATTERN = 3


class DeflectionType(Enum):
    """
    Enum for DeflectionType
    """

    DEFL = "DEFL"
    DEFL_C = "DEFL_C"
    DEFL_W = "DEFL_W"
    DEFL_W2 = "DEFL_W2"


class DisplayComponent(Enum):
    """
    Enum for DisplayComponent
    """

    VECTOR_X = 0
    VECTOR_Y = 1
    VECTOR_Z = 2
    MAGNITUDE = 3
    XX_COMPONENT = 0
    YY_COMPONENT = 1
    ZZ_COMPONENT = 2
    XY_COMPONENT = 3
    XZ_COMPONENT = 4
    YZ_COMPONENT = 5
    FIRST_TENSOR_PRINCIPAL_VALUE = 6
    SECOND_TENSOR_PRINCIPAL_VALUE = 7
    THIRD_TENSOR_PRINCIPAL_VALUE = 8


class ScaleOptions(Enum):
    """
    Enum for ScaleOption
    """

    AUTOMATIC_SCALING_ALL_FRAMES = 0
    AUTOMATIC_SCALING_WITH_COLORS_SCALED_PER_FRAME = 1
    SPECIFIED_MANUAL_SCALING = 2


class PlotMethod(Enum):
    """
    Enum for PlotMethod
    """

    DEFLECTION_PLOT = 1
    SHADED_PLOT = 2
    CONTOUR_PLOT = 4
    DISPLAY_VECTOR_AS_DARTS = 8
    DISPLAY_VECTOR_AS_SEGMENTS = 16
    DISPLAY_TENSOR_AS_AXES = 32
    DISPLAY_TENSOR_AS_ELLIPSES = 64
    DISPLAY_TENSOR_PRINCIPAL_VECTOR_AS_DARTS = 128
    DISPLAY_TENSOR_PRINCIPAL_VECTOR_AS_SEGMENTS = 256


class AnimationType(Enum):
    """
    Enum for AnimationType
    """

    FRAME_ANIMATION = 0
    MIN_MAX_ANIMATION = 1


class ColorTableIDs(Enum):
    """
    Enum for ColorTableIDs
    """

    RAINBOW = 100
    GRAY_SCALE = 110
    COOL_TO_WARM = 120
    BLACK_BODY = 130
    SINGLE_COLOR = 1000
    TRAFFIC_LIGHT = 1100


class EdgeDisplayOptions(Enum):
    """
    Enum for EdgeDisplayOptions
    """

    OFF = 0
    FEATURE_EDGE = 1
    MESH_EDGE = 2


class DeflectionScaleDirections(Enum):
    """
    Enum for DeflectionScaleDirections
    """

    X = 0
    Y = 1
    Z = 2
    ALL = 3


class SliceAtProbeOptions(Enum):
    """
    Enum for SliceAtProbeOptions
    """

    NONE = "None"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"


class TensorAxisRatioOptions(Enum):
    """
    Enum for TensorAxisRatioOptions
    """

    CONSTANT_MAXIMUM_LENGTH = 0
    THREE_TWO_ONE = 1
    PROPORTIONAL_TO_PRINCIPAL_VALUES = 2


class ShrinkageCompensationOptions(Enum):
    """
    Enum for ShrinkageCompensationOptions
    """

    AUTOMATIC = "Automatic"
    ISOTROPIC = "Isotropic"
    ANISOTROPIC = "Anisotropic"
    NONE = "None"


class TraceModes(Enum):
    """
    Enum for TraceModes
    """

    ALL_PATHLINES = 0
    TERMINATING_IN_SELECTED_AREA = 1


class TraceStyles(Enum):
    """
    Enum for TraceStyles
    """

    LINES = 0
    MARKERS = 1
    TUBES = 2


class ScaleTypes(Enum):
    """
    Enum for ScaleTypes
    """

    DEFAULT = 0
    SPECIFIED = 1


class ColorScaleOptions(Enum):
    """
    Enum for ColorScaleOptions
    """

    BLUE_TO_RED = True
    RED_TO_BLUE = False


class ViewModes(Enum):
    """
    Enum for ViewModes projections
    """

    PARALLEL_PROJECTION = 0
    PERSPECTIVE_PROJECTION = 1


class StandardViews(Enum):
    """
    Enum for StandardViews
    """

    FRONT = "Front"
    BACK = "Back"
    RIGHT = "Right"
    LEFT = "Left"
    TOP = "Top"
    BOTTOM = "Bottom"
    FRONT_LEFT = "FrontLeft"
    FRONT_RIGHT = "FrontRight"
    FRONT_TOP = "FrontTop"
    FRONT_BOTTOM = "FrontBottom"
    BACK_LEFT = "BackLeft"
    BACK_RIGHT = "BackRight"
    BACK_TOP = "BackTop"
    BACK_BOTTOM = "BackBottom"
    FRONT_TOP_LEFT = "FrontTopLeft"
    FRONT_TOP_RIGHT = "FrontTopRight"
    FRONT_BOTTOM_LEFT = "FrontBottomLeft"
    FRONT_BOTTOM_RIGHT = "FrontBottomRight"
    BACK_TOP_LEFT = "BackTopLeft"
    BACK_TOP_RIGHT = "BackTopRight"
    BACK_BOTTOM_LEFT = "BackBottomLeft"
    BACK_BOTTOM_RIGHT = "BackBottomRight"
    ISOMETRIC = "Isometric"


class AnimationSpeed(Enum):
    """
    Enum for AnimationSpeed
    """

    SLOW = "Slow"
    MEDIUM = "Medium"
    FAST = "Fast"


class ClampForcePlotDirection(Enum):
    """
    Enum for ClampForcePlotDirection
    """

    X = 0
    Y = 1
    Z = 2


class ModulusPlotDirection(Enum):
    """
    Enum for ModulusPlotDirection
    """

    EXX = 0
    EYY = 1
    EZZ = 2


class PlotType(Enum):
    """
    Enum for PlotType
    """

    PLOT_DEFAULT_PLOT_FOR_DATA_ID = 0
    PLOT_NONE_MESH_PLOT = 1
    PLOT_HIGHLIGHT_PLOT = 4
    PLOT_REGULAR_XY_PLOT = 5
    PLOT_VECTOR_PLOT = 6
    PLOT_TENSOR_PLOT = 7
    PLOT_MIN_MAX_ANIMATION_PLOT = 9
    PLOT_FRAME_ANIMATION_PLOT = 11
    PLOT_XYZ_PLOT = 12
    PLOT_DOE_XY_PLOT = 13
    PLOT_DOE_SHADED_PLOT = 14
    PLOT_XYZ_XY_PLOT = 15
    PLOT_SHRINK_CHECK_PLOT = 16
    PLOT_SINK_MARK_PLOT = 17
    PLOT_USER_DISPLACEMENT_PLOT = 18
    PLOT_GEO_XY_PLOT = 19
    PLOT_XYZ_CUT_XY_PLOT = 20
    PLOT_3D_PROBE_XY_PLOT = 21
    PLOT_MOLD_INTERNAL_TEMPERATURE_PLOT = 22
    PLOT_3D_PLANE_PROBE_PLOT = 23
    PLOT_FUSION_SINK_MARK_PLOT = 24
    PLOT_DOE_RESPONSE_SURFACE_PLOT = 25


class LCSType(Enum):
    """
    Enum for LCS_Type
    """

    COORDINATE_SYSTEM = "LCS"
    MODELLING_PLANE = "Plane"


class CurveInitPosition(Enum):
    """
    Enum for Curve_Init_Position
    """

    START = 0
    END = 1


class PropertyType(Enum):
    """
    Enum for PropertyType
    """

    PART_MIDPLANE = 40800
    GATE_MIDPLANE = 40808
    MOLD_EXTERNAL_SURFACE = 40904
    IN_MOLD_LABEL = 40906
    PART_INSERT = 40907
    MOLD_INSERT_SURFACE = 40908
    PARTING_SURFACE = 40910
