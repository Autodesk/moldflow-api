"""
Test for AnimationExportOptions Wrapper Class of moldflow-api module.
Test Details:

Classes:
    TestUnitAnimationExportOptions: Test suite for the AnimationExportOptions class.
Fixtures:
    mock_animation_export_options: Fixture to create a mock instance of AnimationExportOptions.
Test Methods:

"""

import pytest
from moldflow import AnimationExportOptions, CaptureModes, AnimationSpeed
from moldflow.constants import ANIMATION_SPEED_CONVERTER
from moldflow.logger import set_is_logging
from tests.conftest import (
    NON_NEGATIVE_INT,
    VALID_STR,
    VALID_BOOL,
    INVALID_INT,
    INVALID_BOOL,
    INVALID_STR,
    NEGATIVE_INT,
)


@pytest.mark.unit
class TestUnitAnimationExportOptions:
    """
    Test suite for the AnimationExportOptions class.
    """

    set_is_logging(False)

    @pytest.fixture
    def mock_animation_export_options(self, mock_object) -> AnimationExportOptions:
        """
        Fixture to create a mock instance of AnimationExportOptions.
        Args:
            mock_object: Mock object for the AnimationExportOptions dependency.
        Returns:
            AnimationExportOptions: An instance of AnimationExportOptions with the mock object.
        """
        return AnimationExportOptions(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value,",
        [("FileName", "file_name", x) for x in VALID_STR]
        + [("AnimationSpeed", "animation_speed", x) for x in range(2)]
        + [("ShowPrompts", "show_prompts", x) for x in VALID_BOOL]
        + [("SizeX", "size_x", x) for x in NON_NEGATIVE_INT]
        + [("SizeY", "size_y", x) for x in NON_NEGATIVE_INT]
        + [("CaptureMode", "capture_mode", x.value) for x in CaptureModes],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self,
        mock_animation_export_options: AnimationExportOptions,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test Get properties of AnimationExportOptions.

        Args:
            mock_animation_export_options: Instance of AnimationExportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_animation_export_options, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [
            ("FileName", "file_name", x, y)
            for (x, y) in [("Test", "Test.mp4"), ("Test.mp4", "Test.mp4"), ("Test.gif", "Test.gif")]
        ]
        + [
            ("AnimationSpeed", "animation_speed", x, ANIMATION_SPEED_CONVERTER[x.value])
            for x in AnimationSpeed
        ]
        + [("AnimationSpeed", "animation_speed", x, x) for x in range(2)]
        + [("ShowPrompts", "show_prompts", x, x) for x in VALID_BOOL]
        + [("SizeX", "size_x", x, x) for x in NON_NEGATIVE_INT]
        + [("SizeY", "size_y", x, x) for x in NON_NEGATIVE_INT]
        + [("CaptureMode", "capture_mode", x, x.value) for x in CaptureModes],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self,
        mock_animation_export_options: AnimationExportOptions,
        mock_object,
        pascal_name,
        property_name,
        value,
        expected,
    ):
        """
        Test properties of AnimationExportOptions.

        Args:
            mock_animation_export_options: Instance of AnimationExportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_animation_export_options, property_name, value)
        result = getattr(mock_object, pascal_name)
        assert isinstance(result, type(expected))
        assert result == expected

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("FileName", "file_name", x) for x in INVALID_STR]
        + [("AnimationSpeed", "animation_speed", x) for x in INVALID_INT]
        + [("ShowPrompts", "show_prompts", x) for x in INVALID_BOOL]
        + [("SizeX", "size_x", x) for x in INVALID_INT]
        + [("SizeY", "size_y", x) for x in INVALID_INT]
        + [("CaptureMode", "capture_mode", x) for x in INVALID_INT],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_properties(
        self,
        mock_object,
        mock_animation_export_options: AnimationExportOptions,
        pascal_name,
        property_name,
        value,
        _,
    ):
        """
        Test invalid properties of AnimationExportOptions.
        Args:
            mock_animation_export_options: Instance of AnimationExportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_animation_export_options, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("SizeX", "size_x", x) for x in NEGATIVE_INT]
        + [("SizeY", "size_y", x) for x in NEGATIVE_INT]
        + [("AnimationSpeed", "animation_speed", x) for x in NEGATIVE_INT + [3, 4]]
        + [("CaptureMode", "capture_mode", x) for x in NEGATIVE_INT + [3, 4]],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_value_properties(
        self,
        mock_object,
        mock_animation_export_options: AnimationExportOptions,
        pascal_name,
        property_name,
        value,
        _,
    ):
        """
        Test invalid properties of AnimationExportOptions.
        Args:
            mock_animation_export_options: Instance of AnimationExportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(ValueError) as e:
            setattr(mock_animation_export_options, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
