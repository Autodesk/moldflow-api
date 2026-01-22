"""
Usage:
    ImageExportOptions Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import (
    check_type,
    check_is_non_negative,
    get_enum_value,
    check_range,
    check_file_extension,
)
from .common import CaptureModes
from .constants import PNG_FILE_EXT, JPG_FILE_EXT, JPEG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT


class ImageExportOptions:
    """
    Wrapper for ImageExportOptions class of Moldflow Synergy.
    """

    def __init__(self, _image_export_options):
        """
        Initialize the ImageExportOptions with a ImageExportOptions instance from COM.

        Args:
            _image_export_options: The ImageExportOptions instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="ImageExportOptions")
        self.image_export_options = _image_export_options

    @property
    def file_name(self) -> str:
        """
        The file name.

        :getter: Get the file name.
        :setter: Set the file name.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="file_name")
        return self.image_export_options.FileName

    @file_name.setter
    def file_name(self, value: str) -> None:
        """
        The file name.

        Args:
            value (str): The file name to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="file_name", value=value)
        check_type(value, str)
        value = check_file_extension(
            value, (PNG_FILE_EXT, JPG_FILE_EXT, JPEG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT)
        )
        self.image_export_options.FileName = value

    @property
    def size_x(self) -> int:
        """
        The X size (width) of the image.

        :default: 800
        :getter: Get the X size.
        :setter: Set the X size.
        :type: int (positive)
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size_x")
        return self.image_export_options.SizeX

    @size_x.setter
    def size_x(self, value: int) -> None:
        """
        Set the X size (width) of the image.

        Args:
            value (int): The X size to set (must be positive).
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="size_x", value=value)
        check_type(value, int)
        check_is_non_negative(value)
        self.image_export_options.SizeX = value

    @property
    def size_y(self) -> int:
        """
        The Y size (height) of the image.

        :default: 600
        :getter: Get the Y size.
        :setter: Set the Y size.
        :type: int (positive)
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="size_y")
        return self.image_export_options.SizeY

    @size_y.setter
    def size_y(self, value: int) -> None:
        """
        Set the Y size (height) of the image.

        Args:
            value (int): The Y size to set (must be positive).
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="size_y", value=value)
        check_type(value, int)
        check_is_non_negative(value)
        self.image_export_options.SizeY = value

    @property
    def show_result(self) -> bool:
        """
        Whether to show the result.

        :default: True
        :getter: Get show_result.
        :setter: Set show_result.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_result")
        return self.image_export_options.ShowResult

    @show_result.setter
    def show_result(self, value: bool) -> None:
        """
        Set whether to show the result.

        Args:
            value (bool): Show result or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_result", value=value)
        check_type(value, bool)
        self.image_export_options.ShowResult = value

    @property
    def show_legend(self) -> bool:
        """
        Whether to show the legend.

        :default: True
        :getter: Get show_legend.
        :setter: Set show_legend.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_legend")
        return self.image_export_options.ShowLegend

    @show_legend.setter
    def show_legend(self, value: bool) -> None:
        """
        Set whether to show the legend.

        Args:
            value (bool): Show legend or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_legend", value=value)
        check_type(value, bool)
        self.image_export_options.ShowLegend = value

    @property
    def show_rotation_angle(self) -> bool:
        """
        Whether to show the rotation angle values.

        :default: True
        :getter: Get show_rotation_angle.
        :setter: Set show_rotation_angle.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_rotation_angle")
        return self.image_export_options.ShowRotationAngle

    @show_rotation_angle.setter
    def show_rotation_angle(self, value: bool) -> None:
        """
        Set whether to show the rotation angle values.

        Args:
            value (bool): Show rotation angle values or not.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="show_rotation_angle", value=value
        )
        check_type(value, bool)
        self.image_export_options.ShowRotationAngle = value

    @property
    def show_rotation_axes(self) -> bool:
        """
        Whether to show the rotation axes.

        :default: True
        :getter: Get show_rotation_axes.
        :setter: Set show_rotation_axes.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_rotation_axes")
        return self.image_export_options.ShowRotationAxes

    @show_rotation_axes.setter
    def show_rotation_axes(self, value: bool) -> None:
        """
        Set whether to show the rotation axes.

        Args:
            value (bool): Show rotation axes or not.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="show_rotation_axes", value=value
        )
        check_type(value, bool)
        self.image_export_options.ShowRotationAxes = value

    @property
    def show_scale_bar(self) -> bool:
        """
        Whether to show the scale bar.

        :default: True
        :getter: Get show_scale_bar.
        :setter: Set show_scale_bar.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_scale_bar")
        return self.image_export_options.ShowScaleBar

    @show_scale_bar.setter
    def show_scale_bar(self, value: bool) -> None:
        """
        Set whether to show the scale bar.

        Args:
            value (bool): Show scale bar or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_scale_bar", value=value)
        check_type(value, bool)
        self.image_export_options.ShowScaleBar = value

    @property
    def show_plot_info(self) -> bool:
        """
        Whether to show the plot info.

        :default: True
        :getter: Get show_plot_info.
        :setter: Set show_plot_info.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_plot_info")
        return self.image_export_options.ShowPlotInfo

    @show_plot_info.setter
    def show_plot_info(self, value: bool) -> None:
        """
        Set whether to show the plot info.

        Args:
            value (bool): Show plot info or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_plot_info", value=value)
        check_type(value, bool)
        self.image_export_options.ShowPlotInfo = value

    @property
    def show_study_title(self) -> bool:
        """
        Whether to show the study title.

        :default: True
        :getter: Get show_study_title.
        :setter: Set show_study_title.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_study_title")
        return self.image_export_options.ShowStudyTitle

    @show_study_title.setter
    def show_study_title(self, value: bool) -> None:
        """
        Set whether to show the study title.

        Args:
            value (bool): Show study title or not.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="show_study_title", value=value
        )
        check_type(value, bool)
        self.image_export_options.ShowStudyTitle = value

    @property
    def show_ruler(self) -> bool:
        """
        Whether to show the ruler.

        :default: True
        :getter: Get show_ruler.
        :setter: Set show_ruler.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_ruler")
        return self.image_export_options.ShowRuler

    @show_ruler.setter
    def show_ruler(self, value: bool) -> None:
        """
        Set whether to show the ruler.

        Args:
            value (bool): Show ruler or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_ruler", value=value)
        check_type(value, bool)
        self.image_export_options.ShowRuler = value

    @property
    def show_histogram(self) -> bool:
        """
        Whether to show the histogram.

        :default: True
        :getter: Get show_histogram.
        :setter: Set show_histogram.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_histogram")
        return self.image_export_options.ShowHistogram

    @show_histogram.setter
    def show_histogram(self, value: bool) -> None:
        """
        Set whether to show the histogram.

        Args:
            value (bool): Show histogram or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_histogram", value=value)
        check_type(value, bool)
        self.image_export_options.ShowHistogram = value

    @property
    def show_min_max(self) -> bool:
        """
        Whether to show the min/max.

        :default: True
        :getter: Get show_min_max.
        :setter: Set show_min_max.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_min_max")
        return self.image_export_options.ShowMinMax

    @show_min_max.setter
    def show_min_max(self, value: bool) -> None:
        """
        Set whether to show the min/max.

        Args:
            value (bool): Show min/max or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_min_max", value=value)
        check_type(value, bool)
        self.image_export_options.ShowMinMax = value

    @property
    def fit_to_screen(self) -> bool:
        """
        Whether to fit the image to the screen.

        :default: True
        :getter: Get fit_to_screen.
        :setter: Set fit_to_screen.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="fit_to_screen")
        return self.image_export_options.FitToScreen

    @fit_to_screen.setter
    def fit_to_screen(self, value: bool) -> None:
        """
        Set whether to fit the image to the screen.

        Args:
            value (bool): Fit to screen or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="fit_to_screen", value=value)
        check_type(value, bool)
        self.image_export_options.FitToScreen = value

    @property
    def capture_mode(self) -> int:
        """
        The capture mode.

        :default: CaptureModes.ACTIVE_VIEW/Active View/0
        :getter: Get capture_mode.
        :setter: Set capture_mode.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="capture_mode")
        return self.image_export_options.CaptureMode

    @capture_mode.setter
    def capture_mode(self, value: CaptureModes | int) -> None:
        """
        Set the capture mode.

        Args:
            value (int): The capture mode to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="capture_mode", value=value)
        value = get_enum_value(value, CaptureModes)
        check_range(value, 0, 2, True, True)
        self.image_export_options.CaptureMode = value
