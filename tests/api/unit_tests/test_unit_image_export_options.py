"""
Test for ImageExportOptions Wrapper Class of moldflow-api module.
Test Details:

Classes:
    TestUnitImageExportOptions: Test suite for the ImageExportOptions class.
Fixtures:
    mock_image_export_options: Fixture to create a mock instance of ImageExportOptions.
Test Methods:

"""

import pytest
from moldflow import ImageExportOptions, CaptureModes
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
class TestUnitImageExportOptions:
    """
    Test suite for the ImageExportOptions class.
    """

    set_is_logging(False)

    @pytest.fixture
    def mock_image_export_options(self, mock_object) -> ImageExportOptions:
        """
        Fixture to create a mock instance of ImageExportOptions.
        Args:
            mock_object: Mock object for the ImageExportOptions dependency.
        Returns:
            ImageExportOptions: An instance of ImageExportOptions with the mock object.
        """
        return ImageExportOptions(mock_object)

    @pytest.mark.parametrize(
        "pascal_name, property_name, value,",
        [("FileName", "file_name", x) for x in VALID_STR]
        + [("SizeX", "size_x", x) for x in NON_NEGATIVE_INT]
        + [("SizeY", "size_y", x) for x in NON_NEGATIVE_INT]
        + [("ShowResult", "show_result", x) for x in VALID_BOOL]
        + [("ShowLegend", "show_legend", x) for x in VALID_BOOL]
        + [("ShowRotationAngle", "show_rotation_angle", x) for x in VALID_BOOL]
        + [("ShowRotationAxes", "show_rotation_axes", x) for x in VALID_BOOL]
        + [("ShowScaleBar", "show_scale_bar", x) for x in VALID_BOOL]
        + [("ShowPlotInfo", "show_plot_info", x) for x in VALID_BOOL]
        + [("ShowStudyTitle", "show_study_title", x) for x in VALID_BOOL]
        + [("ShowRuler", "show_ruler", x) for x in VALID_BOOL]
        + [("ShowHistogram", "show_histogram", x) for x in VALID_BOOL]
        + [("ShowMinMax", "show_min_max", x) for x in VALID_BOOL]
        + [("FitToScreen", "fit_to_screen", x) for x in VALID_BOOL]
        + [("CaptureMode", "capture_mode", x.value) for x in CaptureModes],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self,
        mock_image_export_options: ImageExportOptions,
        mock_object,
        pascal_name,
        property_name,
        value,
    ):
        """
        Test Get properties of ImageExportOptions.

        Args:
            mock_image_export_options: Instance of ImageExportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_image_export_options, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value, expected",
        [
            ("FileName", "file_name", x, y)
            for (x, y) in [("Test", "Test.png"), ("Test.jpg", "Test.jpg")]
        ]
        + [("SizeX", "size_x", x, x) for x in NON_NEGATIVE_INT]
        + [("SizeY", "size_y", x, x) for x in NON_NEGATIVE_INT]
        + [("ShowResult", "show_result", x, x) for x in VALID_BOOL]
        + [("ShowLegend", "show_legend", x, x) for x in VALID_BOOL]
        + [("ShowRotationAngle", "show_rotation_angle", x, x) for x in VALID_BOOL]
        + [("ShowRotationAxes", "show_rotation_axes", x, x) for x in VALID_BOOL]
        + [("ShowScaleBar", "show_scale_bar", x, x) for x in VALID_BOOL]
        + [("ShowPlotInfo", "show_plot_info", x, x) for x in VALID_BOOL]
        + [("ShowStudyTitle", "show_study_title", x, x) for x in VALID_BOOL]
        + [("ShowRuler", "show_ruler", x, x) for x in VALID_BOOL]
        + [("ShowHistogram", "show_histogram", x, x) for x in VALID_BOOL]
        + [("ShowMinMax", "show_min_max", x, x) for x in VALID_BOOL]
        + [("FitToScreen", "fit_to_screen", x, x) for x in VALID_BOOL]
        + [("CaptureMode", "capture_mode", x, x.value) for x in CaptureModes],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self,
        mock_image_export_options: ImageExportOptions,
        mock_object,
        pascal_name,
        property_name,
        value,
        expected,
    ):
        """
        Test properties of ImageExportOptions.

        Args:
            mock_image_export_options: Instance of ImageExportOptions.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_image_export_options, property_name, value)
        result = getattr(mock_object, pascal_name)
        assert isinstance(result, type(expected))
        assert result == expected

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("FileName", "file_name", x) for x in INVALID_STR]
        + [("SizeX", "size_x", x) for x in INVALID_INT]
        + [("SizeY", "size_y", x) for x in INVALID_INT]
        + [("ShowResult", "show_result", x) for x in INVALID_BOOL]
        + [("ShowLegend", "show_legend", x) for x in INVALID_BOOL]
        + [("ShowRotationAngle", "show_rotation_angle", x) for x in INVALID_BOOL]
        + [("ShowRotationAxes", "show_rotation_axes", x) for x in INVALID_BOOL]
        + [("ShowScaleBar", "show_scale_bar", x) for x in INVALID_BOOL]
        + [("ShowPlotInfo", "show_plot_info", x) for x in INVALID_BOOL]
        + [("ShowStudyTitle", "show_study_title", x) for x in INVALID_BOOL]
        + [("ShowRuler", "show_ruler", x) for x in INVALID_BOOL]
        + [("ShowHistogram", "show_histogram", x) for x in INVALID_BOOL]
        + [("ShowMinMax", "show_min_max", x) for x in INVALID_BOOL]
        + [("FitToScreen", "fit_to_screen", x) for x in INVALID_BOOL]
        + [("CaptureMode", "capture_mode", x) for x in INVALID_INT],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_properties(
        self,
        mock_object,
        mock_image_export_options: ImageExportOptions,
        pascal_name,
        property_name,
        value,
        _,
    ):
        """
        Test invalid properties of ImageExportOptions.
        Args:
            mock_image_export_options: Instance of ImageExportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_image_export_options, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [("SizeX", "size_x", x) for x in NEGATIVE_INT]
        + [("SizeY", "size_y", x) for x in NEGATIVE_INT]
        + [("CaptureMode", "capture_mode", x) for x in NEGATIVE_INT + [3, 4]],
    )
    # pylint: disable-next=R0913, R0917
    def test_invalid_value_properties(
        self,
        mock_object,
        mock_image_export_options: ImageExportOptions,
        pascal_name,
        property_name,
        value,
        _,
    ):
        """
        Test invalid properties of ImageExportOptions.
        Args:
            mock_image_export_options: Instance of ImageExportOptions.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(ValueError) as e:
            setattr(mock_image_export_options, property_name, value)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
