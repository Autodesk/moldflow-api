"""
Usage:
    AnimationExportOptions Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import (
    check_type,
    check_is_non_negative,
    get_enum_value,
    check_range,
    check_file_extension,
)
from .common import AnimationSpeed, CaptureModes
from .constants import MP4_FILE_EXT, GIF_FILE_EXT, ANIMATION_SPEED_CONVERTER


class AnimationExportOptions:
    """
    Wrapper for AnimationExportOptions class of Moldflow Synergy.
    """

    def __init__(self, _animation_export_options):
        """
        Initialize the AnimationExportOptions with a AnimationExportOptions instance from COM.

        Args:
            _animation_export_options: The AnimationExportOptions instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="AnimationExportOptions")
        self.animation_export_options = _animation_export_options

    @property
    def file_name(self) -> str:
        """
        The file name.

        :getter: Get the file name.
        :setter: Set the file name.
        :type: str
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="file_name")
        return self.animation_export_options.FileName

    @file_name.setter
    def file_name(self, value: str) -> None:
        """
        Set the file name.

        Args:
            value (str): The file name to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="file_name", value=value)
        check_type(value, str)
        value = check_file_extension(value, (MP4_FILE_EXT, GIF_FILE_EXT))
        self.animation_export_options.FileName = value

    # Remove the function when legacy support is removed.
    def _convert_animation_speed(self, speed: AnimationSpeed | int | str) -> str:
        """
        Convert animation speed to string for legacy support.
        """
        speed = get_enum_value(speed, AnimationSpeed)
        return ANIMATION_SPEED_CONVERTER[speed]

    @property
    def animation_speed(self) -> int:
        """
        Animation speed (Slow=0, Medium=1, Fast=2).

        :default: Medium(1)
        :getter: Get the animation speed.
        :setter: Set the animation speed.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="animation_speed")
        return self.animation_export_options.AnimationSpeed

    @animation_speed.setter
    def animation_speed(self, value: AnimationSpeed | int) -> None:
        """
        The animation speed.

        Args:
            value (int): The animation speed to set.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="animation_speed", value=value
        )
        if isinstance(value, AnimationSpeed):
            value = self._convert_animation_speed(value)
        else:
            check_type(value, int)
        check_range(value, 0, 2, True, True)
        self.animation_export_options.AnimationSpeed = value

    @property
    def show_prompts(self) -> bool:
        """
        Whether to show prompts during the export process.

        :default: True
        :getter: Get show_prompts.
        :setter: Set show_prompts.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="show_prompts")
        return self.animation_export_options.ShowPrompts

    @show_prompts.setter
    def show_prompts(self, value: bool) -> None:
        """
        Set whether to show prompts during the export process.

        Args:
            value (bool): Show prompts or not.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="show_prompts", value=value)
        check_type(value, bool)
        self.animation_export_options.ShowPrompts = value

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
        return self.animation_export_options.SizeX

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
        self.animation_export_options.SizeX = value

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
        return self.animation_export_options.SizeY

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
        self.animation_export_options.SizeY = value

    @property
    def capture_mode(self) -> int:
        """
        The capture mode.

        :default: Active View(0)
        :getter: Get the capture mode.
        :setter: Set the capture mode.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="capture_mode")
        return self.animation_export_options.CaptureMode

    @capture_mode.setter
    def capture_mode(self, value: CaptureModes | int) -> None:
        """
        Set the capture mode.

        Args:
            value (CaptureModes | int): Capture mode to set.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="capture_mode", value=value)
        value = get_enum_value(value, CaptureModes)
        check_range(value, 0, 2, True, True)
        self.animation_export_options.CaptureMode = value
