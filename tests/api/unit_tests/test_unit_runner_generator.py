# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Unit Test for RunnerGenerator Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import RunnerGenerator


@pytest.mark.unit
class TestUnitRunnerGenerator:
    """
    Test suite for the RunnerGenerator class.
    """

    @pytest.fixture
    def mock_runner_generator(self, mock_object) -> RunnerGenerator:
        """
        Fixture to create a mock instance of RunnerGenerator.
        Args:
            mock_object: Mock object for the RunnerGenerator dependency.
        Returns:
            RunnerGenerator: An instance of RunnerGenerator with the mock object.
        """
        return RunnerGenerator(mock_object)

    @pytest.mark.parametrize("value", [True, False])
    def test_generate(self, mock_runner_generator: RunnerGenerator, value):
        """
        Test generate method of RunnerGenerator.
        Args:
            mock_runner_generator: Instance of RunnerGenerator.
        """
        mock_runner_generator.runner_generator.Generate = value
        result = mock_runner_generator.generate()
        assert result is value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("SprueX", "sprue_x", 10),
            ("SprueY", "sprue_y", 20),
            ("SprueLength", "sprue_length", 40.5),
            ("PartingZ", "parting_z", 50),
            ("TopRunnerZ", "top_runner_z", 60),
            ("SprueDiameter", "sprue_diameter", 70),
            ("SprueTaperAngle", "sprue_taper_angle", 80),
            ("RunnerDiameter", "runner_diameter", 90),
            ("Trapezoidal", "trapezoidal", True),
            ("TrapezoidAngle", "trapezoid_angle", 100),
            ("DropDiameter", "drop_diameter", 110),
            ("DropTaperAngle", "drop_taper_angle", 120),
            ("GatesByLength", "gates_by_length", False),
            ("GateDiameter", "gate_diameter", 130),
            ("GateTaperAngle", "gate_taper_angle", 140),
            ("GateLength", "gate_length", 150),
            ("GateAngle", "gate_angle", 160),
            ("TopGateStartDiameter", "top_gate_start_diameter", 170),
            ("TopGateEndDiameter", "top_gate_end_diameter", 180),
            ("TopGateLength", "top_gate_length", 190),
            ("DeleteOld", "delete_old", True),
            ("HotRunners", "hot_runners", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_runner_generator: RunnerGenerator, mock_object, pascal_name, property_name, value
    ):
        """
        Test properties of RunnerGenerator.
        Args:
            mock_runner_generator: Instance of RunnerGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_runner_generator, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("SprueX", "sprue_x", 10),
            ("SprueY", "sprue_y", 20),
            ("SprueLength", "sprue_length", 40.5),
            ("PartingZ", "parting_z", 50),
            ("TopRunnerZ", "top_runner_z", 60),
            ("SprueDiameter", "sprue_diameter", 70),
            ("SprueTaperAngle", "sprue_taper_angle", 80),
            ("RunnerDiameter", "runner_diameter", 90),
            ("Trapezoidal", "trapezoidal", True),
            ("TrapezoidAngle", "trapezoid_angle", 100),
            ("DropDiameter", "drop_diameter", 110),
            ("DropTaperAngle", "drop_taper_angle", 120),
            ("GatesByLength", "gates_by_length", False),
            ("GateDiameter", "gate_diameter", 130),
            ("GateTaperAngle", "gate_taper_angle", 140),
            ("GateLength", "gate_length", 150),
            ("GateAngle", "gate_angle", 160),
            ("TopGateStartDiameter", "top_gate_start_diameter", 170),
            ("TopGateEndDiameter", "top_gate_end_diameter", 180),
            ("TopGateLength", "top_gate_length", 190),
            ("DeleteOld", "delete_old", True),
            ("HotRunners", "hot_runners", False),
            ("PartCenterX", "part_center_x", 200),
            ("PartCenterY", "part_center_y", 210),
            ("GatesCenterX", "gates_center_x", 220),
            ("GatesCenterY", "gates_center_y", 230),
            ("Top", "top", 240),
            ("Bottom", "bottom", 250),
            ("GatePlaneZ", "gate_plane_z", 260),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_runner_generator: RunnerGenerator, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of RunnerGenerator.
        Args:
            mock_runner_generator: Instance of RunnerGenerator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_runner_generator, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("sprue_x", "10"),
            ("sprue_x", True),
            ("sprue_y", "20"),
            ("sprue_y", True),
            ("sprue_length", "40.5"),
            ("sprue_length", True),
            ("parting_z", "50"),
            ("parting_z", True),
            ("top_runner_z", "60"),
            ("top_runner_z", True),
            ("sprue_diameter", " 70"),
            ("sprue_diameter", True),
            ("sprue_taper_angle", "80"),
            ("sprue_taper_angle", True),
            ("runner_diameter", " 90"),
            ("runner_diameter", True),
            ("trapezoidal", "True"),
            ("trapezoidal", 0),
            ("trapezoid_angle", " 100"),
            ("trapezoid_angle", True),
            ("drop_diameter", "110"),
            ("drop_diameter", True),
            ("drop_taper_angle", "120"),
            ("drop_taper_angle", True),
            ("gates_by_length", "True"),
            ("gates_by_length", 0),
            ("gate_diameter", "130"),
            ("gate_diameter", True),
            ("gate_taper_angle", "140"),
            ("gate_taper_angle", True),
            ("gate_length", "150"),
            ("gate_length", True),
            ("gate_angle", "160"),
            ("gate_angle", True),
            ("top_gate_start_diameter", "170"),
            ("top_gate_start_diameter", True),
            ("top_gate_end_diameter", "180"),
            ("top_gate_end_diameter", True),
            ("top_gate_length", "190"),
            ("top_gate_length", True),
            ("delete_old", "True"),
            ("delete_old", 0),
            ("hot_runners", "True"),
            ("hot_runners", 0),
        ],
    )
    def test_invalid_properties(
        self, mock_runner_generator: RunnerGenerator, property_name, value, _
    ):
        """
        Test invalid properties of RunnerGenerator.
        Args:
            mock_runner_generator: Instance of RunnerGenerator.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_runner_generator, property_name, value)
        assert _("Invalid") in str(e.value)
