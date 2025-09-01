# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for UnitConversion Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import UnitConversion
from moldflow.common import SystemUnits


@pytest.mark.unit
class TestUnitUnitConversion:
    """
    Test suite for the UnitConversion class.
    """

    @pytest.fixture
    def mock_unit_conversion(self, mock_object) -> UnitConversion:
        """
        Fixture to create a mock instance of UnitConversion.
        Args:
            mock_object: Mock object for the UnitConversion dependency.
        Returns:
            UnitConversion: An instance of UnitConversion with the mock object.
        """
        return UnitConversion(mock_object)

    @pytest.mark.parametrize("unit, value, expected", [('psi', 10, 0.68)])
    # pylint: disable-next=R0913, R0917
    def test_convert_to_si(self, mock_unit_conversion, mock_object, unit, value, expected):
        """Test the convert_to_si method of the UnitConversion class."""
        mock_object.ConvertToSI.return_value = expected
        result = mock_unit_conversion.convert_to_si(unit, value)
        assert isinstance(result, float)
        mock_object.ConvertToSI.assert_called_once_with(unit, value)

    @pytest.mark.parametrize("unit, value", [(5, "String"), (True, False)])
    def test_convert_to_si_invalid(self, mock_unit_conversion, mock_object, unit, value, _):
        """Test the convert_to_si method of the UnitConversion class with invalid methods"""
        with pytest.raises(TypeError) as e:
            mock_unit_conversion.convert_to_si(unit, value)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertToSI.assert_not_called()

    @pytest.mark.parametrize(
        "unit, unit_system, value, expected, expected_enum",
        [
            ("deg/s", "English", 50, 2864.78898, "English"),
            ("cm^3", SystemUnits.METRIC, 50, 0.00005, "Metric"),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_convert_to_unit(
        self, mock_unit_conversion, mock_object, unit, unit_system, value, expected, expected_enum
    ):
        """Test the convert_to_unit method of the UnitConversion class"""
        mock_object.ConvertToUnit.return_value = expected
        result = mock_unit_conversion.convert_to_unit(unit, unit_system, value)
        assert isinstance(result, float)
        assert result == expected
        mock_object.ConvertToUnit.assert_called_once_with(unit, expected_enum, value)

    @pytest.mark.parametrize(
        "unit, unit_system, value",
        [
            (5, "Metric", 5),
            (True, "Metric", 5),
            ("psi", "Metric", " "),
            ("psi", SystemUnits.METRIC, SystemUnits.ENGLISH),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_convert_to_unit_invalid(
        self, mock_unit_conversion, mock_object, unit, unit_system, value, _
    ):
        """Test the convert_to_unit method of the UnitConversion class with invalid methods"""
        with pytest.raises(Exception) as e:
            mock_unit_conversion.convert_to_unit(unit, unit_system, value)
        assert _("Invalid") in str(e.value)
        mock_object.ConvertToUnit.assert_not_called()

    @pytest.mark.parametrize("unit, unit_system, value", [("psi", "Mejtric", 5), ("psi", "Sl", 5)])

    # pylint: disable-next=R0913, R0917
    def test_convert_to_unit_invalid_enum(
        self, mock_unit_conversion, mock_object, unit, unit_system, value, _, caplog
    ):
        """Test the convert_to_unit method of the UnitConversion class with invalid enum value"""
        mock_unit_conversion.convert_to_unit(unit, unit_system, value)
        assert _("this may cause function call to fail") in caplog.text
        mock_object.ConvertToUnit.assert_called_once_with(unit, unit_system, value)

    @pytest.mark.parametrize(
        "unit, unit_system, expected",
        [("psi", SystemUnits.METRIC, "Metric"), ("oz", SystemUnits.ENGLISH, "English")],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_unit_description(
        self, mock_unit_conversion, mock_object, unit, unit_system, expected
    ):
        """Test the get_unit_description method of the UnitConversion class"""
        mock_object.GetUnitDescription.return_value = "Test_String"
        result = mock_unit_conversion.get_unit_description(unit, unit_system)
        assert isinstance(result, str)
        mock_object.GetUnitDescription.assert_called_once_with(unit, expected)

    @pytest.mark.parametrize("unit, unit_system", [(5, "Metric"), ("psi", 50)])
    def test_get_unit_description_invalid(
        self, mock_unit_conversion, mock_object, unit, unit_system, _
    ):
        """Test the get_unit_description method with invalid methods"""
        with pytest.raises(TypeError) as e:
            mock_unit_conversion.get_unit_description(unit, unit_system)
        assert _("Invalid") in str(e.value)
        mock_object.GetUnitDescription.assert_not_called()
