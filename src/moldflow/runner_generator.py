# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    RunnerGenerator Class
"""

from .logger import process_log
from .helper import check_type
from .com_proxy import safe_com
from .common import LogMessage

class RunnerGenerator:
    """
    Wrapper for RunnerGenerator class of Moldflow Synergy.
    """

    def __init__(self, _runner_generator):
        """
        Initialize the RunnerGenerator with a Synergy instance.
        Args:
            _runner_generator: Runner Generator instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="RunnerGenerator")
        self.runner_generator = safe_com(_runner_generator)

    def generate(self) -> bool:
        """
        Generate the runner system.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="generate")
        return self.runner_generator.Generate

    @property
    def sprue_x(self) -> float:
        """
        Value of Sprue X

        :getter: Get value of Sprue X
        :setter: Set value of Sprue X
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="sprue_x")
        return self.runner_generator.SprueX

    @sprue_x.setter
    def sprue_x(self, value: float) -> None:
        """
        Set value of Sprue X

        Args:
            value (float): The value of Sprue X
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="sprue_x", value=value)
        check_type(value, (int, float))
        self.runner_generator.SprueX = value

    @property
    def sprue_y(self) -> float:
        """
        Value of Sprue Y

        :getter: Get value of Sprue Y
        :setter: Set value of Sprue Y
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="sprue_y")
        return self.runner_generator.SprueY

    @sprue_y.setter
    def sprue_y(self, value: float) -> None:
        """
        Set value of Sprue Y

        Args:
            value (float): The value of Sprue Y
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="sprue_y", value=value)
        check_type(value, (int, float))
        self.runner_generator.SprueY = value

    @property
    def sprue_length(self) -> float:
        """
        Value of Sprue Length

        :getter: Get value of Sprue Length
        :setter: Set value of Sprue Length
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="sprue_length")
        return self.runner_generator.SprueLength

    @sprue_length.setter
    def sprue_length(self, value: float) -> None:
        """
        Set value of Sprue Length

        Args:
            value (float): The value of Sprue Length
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="sprue_length", value=value)
        check_type(value, (int, float))
        self.runner_generator.SprueLength = value

    @property
    def parting_z(self) -> float:
        """
        Value of Parting Z

        :getter: Get value of Parting Z
        :setter: Set value of Parting Z
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="parting_z")
        return self.runner_generator.PartingZ

    @parting_z.setter
    def parting_z(self, value: float) -> None:
        """
        Set value of Parting Z

        Args:
            value (float): The value of Parting Z
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="parting_z", value=value)
        check_type(value, (int, float))
        self.runner_generator.PartingZ = value

    @property
    def top_runner_z(self) -> float:
        """
        Value of Top Runner Z

        :getter: Get value of Top Runner Z
        :setter: Set value of Top Runner Z
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="top_runner_z")
        return self.runner_generator.TopRunnerZ

    @top_runner_z.setter
    def top_runner_z(self, value: float) -> None:
        """
        Set value of Top Runner Z

        Args:
            value (float): The value of Top Runner Z
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="top_runner_z", value=value)
        check_type(value, (int, float))
        self.runner_generator.TopRunnerZ = value

    @property
    def sprue_diameter(self) -> float:
        """
        Value of Sprue Diameter

        :getter: Get value of Sprue Diameter
        :setter: Set value of Sprue Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="sprue_diameter")
        return self.runner_generator.SprueDiameter

    @sprue_diameter.setter
    def sprue_diameter(self, value: float) -> None:
        """
        Set value of Sprue Diameter

        Args:
            value (float): The value of Sprue Diameter
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="sprue_diameter", value=value)
        check_type(value, (int, float))
        self.runner_generator.SprueDiameter = value

    @property
    def sprue_taper_angle(self) -> float:
        """
        Value of Sprue Taper Angle

        :getter: Get value of Sprue Taper Angle
        :setter: Set value of Sprue Taper Angle
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="sprue_taper_angle")
        return self.runner_generator.SprueTaperAngle

    @sprue_taper_angle.setter
    def sprue_taper_angle(self, value: float) -> None:
        """
        Set value of Sprue Taper Angle

        Args:
            value (float): The value of Sprue Taper Angle
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="sprue_taper_angle", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.SprueTaperAngle = value

    @property
    def runner_diameter(self) -> float:
        """
        Value of Runner Diameter

        :getter: Get value of Runner Diameter
        :setter: Set value of Runner Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="runner_diameter")
        return self.runner_generator.RunnerDiameter

    @runner_diameter.setter
    def runner_diameter(self, value: float) -> None:
        """
        Set value of Runner Diameter

        Args:
            value (float): The value of Runner Diameter
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="runner_diameter", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.RunnerDiameter = value

    @property
    def trapezoidal(self) -> bool:
        """
        Value of Trapezoidal

        :getter: Get value of Trapezoidal
        :setter: Set value of Trapezoidal
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="trapezoidal")
        return self.runner_generator.Trapezoidal

    @trapezoidal.setter
    def trapezoidal(self, value: bool) -> None:
        """
        Set value of Trapezoidal

        Args:
            value (bool): The value of Trapezoidal
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="trapezoidal", value=value)
        check_type(value, bool)
        self.runner_generator.Trapezoidal = value

    @property
    def trapezoid_angle(self) -> float:
        """
        Value of Trapezoid Angle

        :getter: Get value of Trapezoid Angle
        :setter: Set value of Trapezoid Angle
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="trapezoid_angle")
        return self.runner_generator.TrapezoidAngle

    @trapezoid_angle.setter
    def trapezoid_angle(self, value: float) -> None:
        """
        Set value of Trapezoid Angle

        Args:
            value (float): The value of Trapezoid Angle
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="trapezoid_angle", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.TrapezoidAngle = value

    @property
    def drop_diameter(self) -> float:
        """
        Value of Drop Diameter

        :getter: Get value of Drop Diameter
        :setter: Set value of Drop Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="drop_diameter")
        return self.runner_generator.DropDiameter

    @drop_diameter.setter
    def drop_diameter(self, value: float) -> None:
        """
        Set value of Drop Diameter

        Args:
            value (float): The value of Drop Diameter
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="drop_diameter", value=value)
        check_type(value, (int, float))
        self.runner_generator.DropDiameter = value

    @property
    def drop_taper_angle(self) -> float:
        """
        Value of Drop Taper Angle

        :getter: Get value of Drop Taper Angle
        :setter: Set value of Drop Taper Angle
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="drop_taper_angle")
        return self.runner_generator.DropTaperAngle

    @drop_taper_angle.setter
    def drop_taper_angle(self, value: float) -> None:
        """
        Set value of Drop Taper Angle

        Args:
            value (float): The value of Drop Taper Angle
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="drop_taper_angle", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.DropTaperAngle = value

    @property
    def gates_by_length(self) -> bool:
        """
        Value of Gates By Length

        :getter: Get value of Gates By Length
        :setter: Set value of Gates By Length
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gates_by_length")
        return self.runner_generator.GatesByLength

    @gates_by_length.setter
    def gates_by_length(self, value: bool) -> None:
        """
        Set value of Gates By Length

        Args:
            value (bool): The value of Gates By Length
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="gates_by_length", value=value
        )
        check_type(value, bool)
        self.runner_generator.GatesByLength = value

    @property
    def gate_diameter(self) -> float:
        """
        Value of Gate Diameter

        :getter: Get value of Gate Diameter
        :setter: Set value of Gate Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_diameter")
        return self.runner_generator.GateDiameter

    @gate_diameter.setter
    def gate_diameter(self, value: float) -> None:
        """
        Set value of Gate Diameter

        Args:
            value (float): The value of Gate Diameter
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="gate_diameter", value=value)
        check_type(value, (int, float))
        self.runner_generator.GateDiameter = value

    @property
    def gate_taper_angle(self) -> float:
        """
        Value of Gate Taper Angle

        :getter: Get value of Gate Taper Angle
        :setter: Set value of Gate Taper Angle
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_taper_angle")
        return self.runner_generator.GateTaperAngle

    @gate_taper_angle.setter
    def gate_taper_angle(self, value: float) -> None:
        """
        Set value of Gate Taper Angle

        Args:
            value (float): The value of Gate Taper Angle
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="gate_taper_angle", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.GateTaperAngle = value

    @property
    def gate_length(self) -> float:
        """
        Value of Gate Length

        :getter: Get value of Gate Length
        :setter: Set value of Gate Length
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_length")
        return self.runner_generator.GateLength

    @gate_length.setter
    def gate_length(self, value: float) -> None:
        """
        Set value of Gate Length

        Args:
            value (float): The value of Gate Length
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="gate_length", value=value)
        check_type(value, (int, float))
        self.runner_generator.GateLength = value

    @property
    def gate_angle(self) -> float:
        """
        Value of Gate Angle

        :getter: Get value of Gate Angle
        :setter: Set value of Gate Angle
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_angle")
        return self.runner_generator.GateAngle

    @gate_angle.setter
    def gate_angle(self, value: float) -> None:
        """
        Set value of Gate Angle

        Args:
            value (float): The value of Gate Angle
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="gate_angle", value=value)
        check_type(value, (int, float))
        self.runner_generator.GateAngle = value

    @property
    def top_gate_start_diameter(self) -> float:
        """
        Value of Top Gate Start Diameter

        :getter: Get value of Top Gate Start Diameter
        :setter: Set value of Top Gate Start Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="top_gate_start_diameter")
        return self.runner_generator.TopGateStartDiameter

    @top_gate_start_diameter.setter
    def top_gate_start_diameter(self, value: float) -> None:
        """
        Set value of Top Gate Start Diameter

        Args:
            value (float): The value of Top Gate Start Diameter
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="top_gate_start_diameter", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.TopGateStartDiameter = value

    @property
    def top_gate_end_diameter(self) -> float:
        """
        Value of Top Gate End Diameter

        :getter: Get value of Top Gate End Diameter
        :setter: Set value of Top Gate End Diameter
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="top_gate_end_diameter")
        return self.runner_generator.TopGateEndDiameter

    @top_gate_end_diameter.setter
    def top_gate_end_diameter(self, value: float) -> None:
        """
        Set value of Top Gate End Diameter

        Args:
            value (float): The value of Top Gate End Diameter
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="top_gate_end_diameter", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.TopGateEndDiameter = value

    @property
    def top_gate_length(self) -> float:
        """
        Value of Top Gate Length

        :getter: Get value of Top Gate Length
        :setter: Set value of Top Gate Length
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="top_gate_length")
        return self.runner_generator.TopGateLength

    @top_gate_length.setter
    def top_gate_length(self, value: float) -> None:
        """
        Set value of Top Gate Length

        Args:
            value (float): The value of Top Gate Length
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="top_gate_length", value=value
        )
        check_type(value, (int, float))
        self.runner_generator.TopGateLength = value

    @property
    def delete_old(self) -> bool:
        """
        Value of Delete Old

        :getter: Get value of Delete Old
        :setter: Set value of Delete Old
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="delete_old")
        return self.runner_generator.DeleteOld

    @delete_old.setter
    def delete_old(self, value: bool) -> None:
        """
        Set value of Delete Old

        Args:
            value (bool): The value of Delete Old
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="delete_old", value=value)
        check_type(value, bool)
        self.runner_generator.DeleteOld = value

    @property
    def hot_runners(self) -> bool:
        """
        Value of Hot Runners

        :getter: Get value of Hot Runners
        :setter: Set value of Hot Runners
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="hot_runners")
        return self.runner_generator.HotRunners

    @hot_runners.setter
    def hot_runners(self, value: bool) -> None:
        """
        Set value of Hot Runners

        Args:
            value (bool): The value of Hot Runners
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="hot_runners", value=value)
        check_type(value, bool)
        self.runner_generator.HotRunners = value

    @property
    def part_center_x(self) -> float:
        """
        Value of Part Center X

        :getter: Get value of Part Center X
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="part_center_x")
        return self.runner_generator.PartCenterX

    @property
    def part_center_y(self) -> float:
        """
        Value of Part Center Y

        :getter: Get value of Part Center Y
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="part_center_y")
        return self.runner_generator.PartCenterY

    @property
    def gates_center_x(self) -> float:
        """
        Value of Gates Center X

        :getter: Get value of Gates Center X
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gates_center_x")
        return self.runner_generator.GatesCenterX

    @property
    def gates_center_y(self) -> float:
        """
        Value of Gates Center Y

        :getter: Get value of Gates Center Y
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gates_center_y")
        return self.runner_generator.GatesCenterY

    @property
    def top(self) -> float:
        """
        Value of Top

        :getter: Get value of Top
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="top")
        return self.runner_generator.Top

    @property
    def bottom(self) -> float:
        """
        Value of Bottom

        :getter: Get value of Bottom
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="bottom")
        return self.runner_generator.Bottom

    @property
    def gate_plane_z(self) -> float:
        """
        Value of Gate Plane Z

        :getter: Get value of Gate Plane Z
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="gate_plane_z")
        return self.runner_generator.GatePlaneZ
