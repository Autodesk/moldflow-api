# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Viewer Class API Wrapper
"""

# pylint: disable=C0302
from win32com.client import VARIANT
import pythoncom
from .double_array import DoubleArray
from .ent_list import EntList
from .logger import process_log
from .com_proxy import safe_com
from .common import LogMessage, ViewModes, StandardViews, AnimationSpeed
from .constants import (
    MP4_FILE_EXT,
    JPG_FILE_EXT,
    JPEG_FILE_EXT,
    PNG_FILE_EXT,
    BMP_FILE_EXT,
    TIF_FILE_EXT,
)
from .helper import (
    check_min_max,
    check_range,
    check_type,
    check_optional_type,
    get_enum_value,
    check_is_positive,
    check_is_non_negative,
    check_file_extension,
    coerce_optional_dispatch,
)
from .errors import raise_value_error
from .common import ValueErrorReason
from .plot import Plot
from .vector import Vector

class Viewer:
    """
    Wrapper for Viewer class of Moldflow Synergy.
    """

    def __init__(self, _viewer):
        """
        Initialize the Viewer with a Viewer instance from COM.

        Args:
            _viewer: The Viewer instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Viewer")
        self.viewer = safe_com(_viewer)

    def reset(self) -> None:
        """
        Resets the viewer to its default state.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="reset")
        self.viewer.Reset()

    def reset_legend(self) -> None:
        """
        Resets the legend to its default state.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="reset_legend")
        self.viewer.ResetLegend()

    def reset_view(self, normal_view: Vector | None, up_view: Vector | None) -> None:
        """
        Resets the view with given normal and "up" directions.

        Args:
            normal_view (Vector | None): The normal view vector.
            up_view (Vector | None): The up view vector.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="reset_view")

        self.viewer.ResetView(
            check_and_coerce_optional(normal_view, Vector),
            check_and_coerce_optional(up_view, Vector),
        )

    def rotate(self, angle_x: float, angle_y: float, angle_z: float) -> None:
        """
        Rotates the view to the given set of angles.

        Args:
            angle_x (float): The rotation angle around the x-axis.
            angle_y (float): The rotation angle around the y-axis.
            angle_z (float): The rotation angle around the z-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate")
        check_type(angle_x, (int, float))
        check_type(angle_y, (int, float))
        check_type(angle_z, (int, float))
        self.viewer.Rotate(angle_x, angle_y, angle_z)

    def rotate_x(self, angle_x: float) -> None:
        """
        Rotates the view about the X axis to a specified angle

        Args:
            angle_x (float): The rotation angle around the x-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_x")
        check_type(angle_x, (int, float))
        self.viewer.RotateX(angle_x)

    def rotate_y(self, angle_y: float) -> None:
        """
        Rotates the view about the Y axis to a specified angle

        Args:
            angle_y (float): The rotation angle around the y-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_y")
        check_type(angle_y, (int, float))
        self.viewer.RotateY(angle_y)

    def rotate_z(self, angle_z: float) -> None:
        """
        Rotates the view about the Z axis to a specified angle

        Args:
            angle_z (float): The rotation angle around the z-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_z")
        check_type(angle_z, (int, float))
        self.viewer.RotateZ(angle_z)

    def rotate_by(self, angle_x: float, angle_y: float, angle_z: float) -> None:
        """
        Rotates by the given angles.

        Args:
            angle_x (float): The rotation angle around the x-axis.
            angle_y (float): The rotation angle around the y-axis.
            angle_z (float): The rotation angle around the z-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_by")
        check_type(angle_x, (int, float))
        check_type(angle_y, (int, float))
        check_type(angle_z, (int, float))
        self.viewer.RotateBy(angle_x, angle_y, angle_z)

    def rotate_x_by(self, angle_x: float) -> None:
        """
        Rotates the view about the X axis by a specified angle

        Args:
            angle_x (float): The rotation angle around the x-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_x_by")
        check_type(angle_x, (int, float))
        self.viewer.RotateXBy(angle_x)

    def rotate_y_by(self, angle_y: float) -> None:
        """
        Rotates the view about the Y axis by a specified angle

        Args:
            angle_y (float): The rotation angle around the y-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_y_by")
        check_type(angle_y, (int, float))
        self.viewer.RotateYBy(angle_y)

    def rotate_z_by(self, angle_z: float) -> None:
        """
        Rotates the view about the Z axis by a specified angle

        Args:
            angle_z (float): The rotation angle around the z-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_z_by")
        check_type(angle_z, (int, float))
        self.viewer.RotateZBy(angle_z)

    def set_view_mode(self, perspective: ViewModes | int) -> None:
        """
        Enables parallel or perspective projection.

        Args:
            perspective (ViewModes | int): The perspective mode.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_view_mode")
        perspective = get_enum_value(perspective, ViewModes)
        self.viewer.SetViewMode(perspective)

    def fit(self) -> None:
        """
        Fits the view to the current model.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="fit")
        self.viewer.Fit()

    def pan(self, x: float, y: float) -> None:
        """
        Pans the view

        Args:
            x (float): Pan Factor,
                < 0 to move to the left
                > 0 to move to the right

            y (float): Pan Factor,
                < 0 to move to the bottom
                > 0 to move to the top

        Notes:
            factors are normalized to the screen height,
            i.e., a factor of 1 moves the model by one screen-height to the top
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="pan")
        check_type(x, (int, float))
        check_type(y, (int, float))
        self.viewer.Pan(x, y)

    def zoom(self, factor: float) -> None:
        """
        Zooms the view

        Args:
            factor (float): Zoom Factor,
                < 0 to zoom out
                > 0 to zoom in
                factors are normalized to the screen height,
                i.e., a factor of 1 moves the model by one screen-height to the top
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="zoom")
        check_type(factor, (int, float))
        self.viewer.Zoom(factor)

    def go_to_standard_view(self, name: StandardViews | str) -> None:
        """
        Go to a standard view

        Args:
            name (StandardViews | str): The name of the standard view.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="go_to_standard_view")
        name = get_enum_value(name, StandardViews)
        self.viewer.GoToStandardView(name)

    def create_bookmark(self, name: str) -> None:
        """
        Creates a bookmark with the given name.

        Args:
            name (str): The name of the bookmark.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_bookmark")
        check_type(name, str)
        self.viewer.CreateBookmark(name)

    def delete_bookmark(self, name: str) -> None:
        """
        Deletes a bookmark with the given name.

        Args:
            name (str): The name of the bookmark.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_bookmark")
        check_type(name, str)
        self.viewer.DeleteBookmark(name)

    def go_to_bookmark(self, name: str) -> None:
        """
        Goes to a bookmark with the given name.

        Args:
            name (str): The name of the bookmark.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="go_to_bookmark")
        check_type(name, str)
        self.viewer.GoToBookmark(name)

    def print(self) -> None:
        """
        Prints the current view.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="print")
        self.viewer.Print()

    # pylint: disable=R0913, R0917
    def save_image(
        self,
        filename: str,
        x: int = 0,
        y: int = 0,
        result: bool = False,
        legend: bool = False,
        axis: bool = False,
        rotation: bool = False,
        scale_bar: bool = False,
        plot_info: bool = False,
        study_title: bool = False,
        ruler: bool = False,
        logo: bool = False,
        histogram: bool = False,
        min_max: bool = False,
    ) -> bool:
        """
        Saves the current view as an image.

        Args:
            filename (str): The name of the file to save the image to.
            x (int): The width of the image.
            y (int): The height of the image.
            result (bool): Whether to include results in the image.
            legend (bool): Whether to include the legend in the image.
            axis (bool): Whether to include axes in the image.
            rotation (bool): Whether to include rotation in the image.
            scale_bar (bool): Whether to include a scale bar in the image.
            plot_info (bool): Whether to include plot information in the image.
            study_title (bool): Whether to include study title in the image.
            ruler (bool): Whether to include a ruler in the image.
            logo (bool): Whether to include a logo in the image.
            histogram (bool): Whether to include a histogram in the image.
            min_max (bool): Whether to include min/max values in the image.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_image")
        check_type(filename, str)
        filename = check_file_extension(
            filename, (PNG_FILE_EXT, JPG_FILE_EXT, JPEG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT)
        )
        check_type(x, int)
        check_type(y, int)
        check_type(result, bool)
        check_type(legend, bool)
        check_type(axis, bool)
        check_type(rotation, bool)
        check_type(scale_bar, bool)
        check_type(plot_info, bool)
        check_type(study_title, bool)
        check_type(ruler, bool)
        check_type(logo, bool)
        check_type(histogram, bool)
        check_type(min_max, bool)

        return self.viewer.SaveImage4(
            filename,
            x,
            y,
            result,
            legend,
            axis,
            rotation,
            scale_bar,
            plot_info,
            study_title,
            ruler,
            logo,
            histogram,
            min_max,
        )

    def save_animation(
        self, filename: str, speed: AnimationSpeed | str, prompts: bool = False
    ) -> bool:
        """
        Saves the current view as an animation.

        Args:
            filename (str): The name of the file to save the animation to.
            speed (AnimationSpeed | str): The speed of the animation.
            prompts (bool): Whether to include prompts in the animation.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_animation")
        check_type(filename, str)
        filename = check_file_extension(filename, (MP4_FILE_EXT))
        speed = get_enum_value(speed, AnimationSpeed)
        check_type(prompts, bool)
        return self.viewer.SaveAnimation3(filename, speed, prompts)

    def save_image_legacy(self, filename: str, x: int | None = None, y: int | None = None) -> bool:
        """
        Save image using legacy behavior only (V1/V2):
        - filename only -> SaveImage(filename)
        - filename and positive x,y -> SaveImage2(filename, x, y)
        Args:
            filename: Output image path.
            x: Width in pixels (must be > 0 when provided).
            y: Height in pixels (must be > 0 when provided).
        Returns:
            bool: True if successful (V2 returns its bool; V1 coerced to True).
        Raises:
            TypeError: If types are invalid.
            ValueError: If only one of x/y provided or sizes are not positive.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_image_legacy")
        check_type(filename, str)
        filename = check_file_extension(
            filename, (PNG_FILE_EXT, JPG_FILE_EXT, JPEG_FILE_EXT, BMP_FILE_EXT, TIF_FILE_EXT)
        )
        check_optional_type(x, int)
        check_optional_type(y, int)

        # Route strictly to legacy COM methods
        if x is None and y is None:
            self.viewer.SaveImage(filename)
            return True

        # Both x and y must be provided together
        if (x is None) != (y is None):
            raise_value_error(ValueErrorReason.BOTH_PARAMETERS_REQUIRED, first="x", second="y")

        # Validate positive sizes
        check_is_positive(x)
        check_is_positive(y)
        return self.viewer.SaveImage2(filename, x, y)

    def enable_clipping_plane_by_id(self, plane_id: int, enable: bool) -> None:
        """
        Enables or disables clipping by plane ID.

        Args:
            plane_id (int): The ID of the plane.
            enable (bool): Whether to enable or disable clipping.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="enable_clipping_plane_by_id"
        )
        check_type(plane_id, int)
        check_type(enable, bool)
        self.viewer.EnableClippingPlaneByID(plane_id, enable)

    def delete_clipping_plane_by_id(self, plane_id: int) -> None:
        """
        Deletes clipping by plane ID.

        Args:
            plane_id (int): The ID of the plane.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="delete_clipping_plane_by_id"
        )
        check_type(plane_id, int)
        self.viewer.DeleteClippingPlaneByID(plane_id)

    # pylint: disable=R0913, R0917
    def add_bookmark(
        self,
        name: str,
        normal_view: Vector | None,
        up_view: Vector | None,
        focal_point: Vector | None,
        eye_position: Vector | None,
        clipping_range_min: float,
        clipping_range_max: float,
        view_angle: float,
        parallel_scale: float,
    ) -> None:
        """
        Adds a bookmark with the given parameters.

        Args:
            name (str): The name of the bookmark.
            normal_view (Vector | None): The normal view vector.
            up_view (Vector | None): The up view vector.
            focal_point (Vector | None): The focal point vector.
            eye_position (Vector | None): The eye position vector.
            clipping_range_min (float): The minimum clipping range.
            clipping_range_max (float): The maximum clipping range.
            view_angle (float): The view angle.
            parallel_scale (float): The parallel scale.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="add_bookmark")
        check_type(name, str)

        check_type(clipping_range_min, (int, float))
        check_is_non_negative(clipping_range_min)
        check_type(clipping_range_max, (int, float))
        check_min_max(clipping_range_min, clipping_range_max)
        check_type(view_angle, (int, float))
        check_type(parallel_scale, (int, float))
        self.viewer.AddBookmark(
            name,
            check_and_coerce_optional(normal_view, Vector),
            check_and_coerce_optional(up_view, Vector),
            check_and_coerce_optional(focal_point, Vector),
            check_and_coerce_optional(eye_position, Vector),
            clipping_range_min,
            clipping_range_max,
            view_angle,
            parallel_scale,
        )

    def show_plot(self, plot: Plot | None) -> None:
        """
        Show the given plot.

        Args:
            plot (Plot | None): The plot to show.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_plot")
        check_optional_type(plot, Plot)
        self.viewer.ShowPlot(coerce_optional_dispatch(plot, "plot"))

    def hide_plot(self, plot: Plot | None) -> None:
        """
        Hide the given plot.

        Args:
            plot (Plot | None): The plot to hide.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="hide_plot")
        check_optional_type(plot, Plot)
        self.viewer.HidePlot(coerce_optional_dispatch(plot, "plot"))

    def overlay_plot(self, plot: Plot | None) -> None:
        """
        Overlays a plot on another plot in the viewer

        Args:
            plot (Plot | None): The plot to overlay.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="overlay_plot")
        check_optional_type(plot, Plot)
        self.viewer.OverlayPlot(coerce_optional_dispatch(plot, "plot"))

    def get_plot(self, plot_id: int) -> Plot:
        """
        Get a plot by its ID.

        Args:
            plot_id (int): The ID of the plot.

        Returns:
            Plot: The plot with the given ID.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_plot")
        check_type(plot_id, int)
        result = self.viewer.GetPlot(plot_id)
        if result is None:
            return None
        return Plot(result)

    def center(self, center_x: float, center_y: float) -> None:
        """
        Centers the view at the given coordinates.

        Args:
            center_x (float): The x-coordinate to center on.
            center_y (float): The y-coordinate to center on.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="center")
        check_type(center_x, (int, float))
        check_range(center_x, 0, 1, True, True)
        check_type(center_y, (int, float))
        check_range(center_y, 0, 1, True, True)
        self.viewer.Center(center_x, center_y)

    def world_to_display(self, world_coord: Vector | None) -> Vector:
        """
        Converts world coordinates to display coordinates.

        Args:
            world_coord (Vector | None): The world coordinates to convert.

        Returns:
            Vector: The converted display coordinates.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="world_to_display")

        result = self.viewer.WorldToDisplay(check_and_coerce_optional(world_coord, Vector))
        if result is None:
            return None
        return Vector(result)

    def create_clipping_plane(self, normal: Vector | None, distance: float) -> EntList:
        """
        Creates a clipping plane with the given normal and distance.

        Args:
            normal (Vector | None): The normal vector of the clipping plane.
            distance (float): The distance from the origin to the clipping plane.

        Returns:
            EntList: Object containing created clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_clipping_plane")

        check_type(distance, (int, float))
        result = self.viewer.CreateClippingPlane(
            check_and_coerce_optional(normal, Vector), distance
        )
        if result is None:
            return None
        return EntList(result)

    def create_default_clipping_plane(self) -> EntList:
        """
        Creates a default clipping plane.

        Returns:
            EntList: Object containing created clipping plane.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="create_default_clipping_plane"
        )
        result = self.viewer.CreateDefaultClippingPlane
        if result is None:
            return None
        return EntList(result)

    def modify_clipping_plane(
        self, plane: EntList | None, normal: Vector | None, distance: float
    ) -> None:
        """
        Modifies the given clipping plane with the new normal and distance.

        Args:
            plane (EntList | None): The clipping plane to modify.
            normal (Vector | None): The new normal vector of the clipping plane.
            distance (float): The new distance from the origin to the clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="modify_clipping_plane")

        check_type(distance, (int, float))
        self.viewer.ModifyClippingPlane(
            check_and_coerce_optional(plane, EntList),
            check_and_coerce_optional(normal, Vector),
            distance,
        )

    def modify_clipping_plane_by_id(
        self, plane_id: int, normal: Vector | None, distance: float
    ) -> None:
        """
        Modifies the clipping plane with the given ID with the new normal and distance.

        Args:
            plane_id (int): The ID of the clipping plane to modify.
            normal (Vector | None): The new normal vector of the clipping plane.
            distance (float): The new distance from the origin to the clipping plane.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="modify_clipping_plane_by_id"
        )
        check_type(plane_id, int)

        check_type(distance, (int, float))
        self.viewer.ModifyClippingPlaneByID(
            plane_id, check_and_coerce_optional(normal, Vector), distance
        )

    def delete_clipping_plane(self, plane: EntList | None) -> None:
        """
        Deletes the given clipping plane.

        Args:
            plane (EntList | None): The clipping plane to delete.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete_clipping_plane")

        self.viewer.DeleteClippingPlane(check_and_coerce_optional(plane, EntList))

    def get_first_clipping_plane(self) -> EntList:
        """
        Gets the first clipping plane.

        Returns:
            EntList: The first clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_first_clipping_plane")
        result = self.viewer.GetFirstClippingPlane
        if result is None:
            return None
        return EntList(result)

    def get_next_clipping_plane(self, plane: EntList | None) -> EntList:
        """
        Gets the next clipping plane after the given one.

        Args:
            plane (EntList | None): The current clipping plane.

        Returns:
            EntList: The next clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_next_clipping_plane")

        result = self.viewer.GetNextClippingPlane(check_and_coerce_optional(plane, EntList))
        if result is None:
            return None
        return EntList(result)

    def enable_clipping_plane(self, plane: EntList | None, enable: bool) -> None:
        """
        Enables or disables the given clipping plane.

        Args:
            plane (EntList | None): The clipping plane to enable or disable.
            enable (bool): Whether to enable or disable the clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="enable_clipping_plane")

        check_type(enable, bool)
        self.viewer.EnableClippingPlane(check_and_coerce_optional(plane, EntList), enable)

    @property
    def active_clipping_plane(self) -> EntList:
        """
        Gets the active clipping plane.

        Returns:
            EntList: The active clipping plane.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_active_clipping_plane")
        result = self.viewer.GetActiveClippingPlane
        if result is None:
            return None
        return EntList(result)

    @active_clipping_plane.setter
    def active_clipping_plane(self, plane: EntList | None) -> None:
        """
        Sets the active clipping plane.

        Args:
            plane: The clipping plane to set as active.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_active_clipping_plane")

        self.viewer.SetActiveClippingPlane(check_and_coerce_optional(plane, EntList))

    def show_plot_frame(self, plot: Plot | None, frame: int) -> None:
        """
        Shows the given plot frame.

        Args:
            plot (Plot | None): The plot to show.
            frame (int): The frame number to show.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_plot_frame")
        check_optional_type(plot, Plot)
        check_type(frame, int)
        check_is_non_negative(frame)
        self.viewer.ShowPlotFrame(coerce_optional_dispatch(plot, "plot"), frame)

    def set_view_size(self, size_x: int, size_y: int) -> bool:
        """
        Sets the view size.

        Args:
            size_x (int): The width of the view.
            size_y (int): The height of the view.

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_view_size")
        check_type(size_x, int)
        check_type(size_y, int)
        check_is_non_negative(size_x)
        check_is_non_negative(size_y)
        return self.viewer.SetViewSize(size_x, size_y)

    @property
    def rotation_x(self) -> float:
        """
        Get the current rotation around the x-axis in degrees.

        Returns:
            float: The rotation around the x-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_rotation_x")
        return self.viewer.GetRotationX

    @property
    def rotation_y(self) -> float:
        """
        Get the current rotation around the y-axis in degrees.

        Returns:
            float: The rotation around the y-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_rotation_y")
        return self.viewer.GetRotationY

    @property
    def rotation_z(self) -> float:
        """
        Get the current rotation around the z-axis in degrees.

        Returns:
            float: The rotation around the z-axis.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_rotation_z")
        return self.viewer.GetRotationZ

    @property
    def view_size_x(self) -> int:
        """
        Get the current view size width in pixels on the window restored size and position

        Returns:
            int: The width of the view.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_view_size_x")
        return self.viewer.GetViewSizeX

    @property
    def view_size_y(self) -> int:
        """
        Get the current view size height in pixels on the window restored size and position

        Returns:
            int: The height of the view.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_view_size_y")
        return self.viewer.GetViewSizeY

    def save_plot_scale_image(self, filename: str) -> bool:
        """
        Saves the current plot scale as an image.

        Args:
            filename (str): The name of the file to save the image to.

        Note:The image scale and size is the same as on the screen @

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_plot_scale_image")
        check_type(filename, str)
        return self.viewer.SavePlotScaleImage(filename)

    def save_axis_image(self, filename: str) -> bool:
        """
        Saves the current axis as an image.

        Args:
            filename (str): The name of the file to save the image to.

        Note:The image scale and size is the same as on the screen @

        Returns:
            bool: True if successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="save_axis_image")
        check_type(filename, str)
        return self.viewer.SaveAxisImage(filename)

    def play_animation(self) -> None:
        """
        Plays the current animation.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="play_animation")
        self.viewer.PlayAnimation()

    def is_play_animation(self) -> bool:
        """
        Checks if the animation is currently playing.

        Returns:
            bool: True if the animation is playing, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="is_play_animation")
        return self.viewer.IsPlayAnimation

    def set_min_max_minimum_label_location(
        self, x: float, y: float, x_size: float, y_size: float
    ) -> None:
        """
        Sets the minimum label location for the min/max plot.

        Args:
            x (float): The x-coordinate of the bottom left corner of the minimum label location.
            y (float): The y-coordinate of the bottom left corner of the minimum label location.
            x_size (float): The width of the minimum label.
            y_size (float): The height of the minimum label.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="set_min_max_minimum_label_location"
        )
        check_type(x, (int, float))
        check_type(y, (int, float))
        check_type(x_size, (int, float))
        check_type(y_size, (int, float))
        self.viewer.SetMinMaxMinimumLabelLocation(x, y, x_size, y_size)

    def set_min_max_maximum_label_location(
        self, x: float, y: float, x_size: float, y_size: float
    ) -> None:
        """
        Sets the maximum label location for the min/max plot.

        Args:
            x (float): The x-coordinate of the bottom left corner of the maximum label location.
            y (float): The y-coordinate of the bottom left corner of the maximum label location.
            x_size (float): The width of the maximum label.
            y_size (float): The height of the maximum label.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="set_min_max_maximum_label_location"
        )
        check_type(x, (int, float))
        check_type(y, (int, float))
        check_type(x_size, (int, float))
        check_type(y_size, (int, float))
        self.viewer.SetMinMaxMaximumLabelLocation(x, y, x_size, y_size)

    def get_min_max_minimum_label_location(self) -> DoubleArray:
        """
        Gets the minimum label location for the min/max plot.

        Returns:
            DoubleArray: The minimum label location.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_min_max_minimum_label_location"
        )
        result = self.viewer.GetMinMaxMinimumLabelLocation
        if result is None:
            return None
        return DoubleArray(result)

    def get_min_max_maximum_label_location(self) -> DoubleArray:
        """
        Gets the maximum label location for the min/max plot.

        Returns:
            DoubleArray: The maximum label location.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_min_max_maximum_label_location"
        )
        result = self.viewer.GetMinMaxMaximumLabelLocation
        if result is None:
            return None
        return DoubleArray(result)

    def set_histogram_location(self, x: float, y: float, x_size: float, y_size: float) -> None:
        """
        Sets the histogram location.

        Args:
            x (float): The x-coordinate of the bottom left corner of the histogram location.
            y (float): The y-coordinate of the bottom left corner of the histogram location.
            x_size (float): The width of the histogram.
            y_size (float): The height of the histogram.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_histogram_location")
        check_type(x, (int, float))
        check_type(y, (int, float))
        check_type(x_size, (int, float))
        check_type(y_size, (int, float))
        self.viewer.SetHistogramLocation(x, y, x_size, y_size)

    def get_histogram_location(self) -> DoubleArray:
        """
        Gets the histogram location.

        Returns:
            DoubleArray: The histogram location.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_histogram_location")
        result = self.viewer.GetHistogramLocation
        if result is None:
            return None
        return DoubleArray(result)

    def set_banded_contours(self, plot_name: str, banding: bool, num_colours: int) -> None:
        """
        Sets banded contours for the given plot.

        Args:
            plot_name (str): The name of the plot.
            banding (bool): Whether to enable or disable banding.
            num_colours (int): The number of colours to use for banding.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_banded_contours")
        check_type(plot_name, str)
        check_type(banding, bool)
        check_type(num_colours, int)
        check_is_positive(num_colours)
        self.viewer.SetBandedContours(plot_name, banding, num_colours)

    def get_number_frames_by_name(self, plot_name: str) -> int:
        """
        Gets the number of frames for the given plot.
        Args:
            plot_name (str): The name of the plot.
        Returns:
            int: The number of frames.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="get_number_frames_by_name")
        check_type(plot_name, str)
        out_val = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        self.viewer.GetNumberFramesByName(plot_name, out_val)
        return out_val.value

    def show_plot_by_name(self, plot_name: str) -> None:
        """
        Shows the plot with the given name.

        Args:
            plot_name (str): The name of the plot to show.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_plot_by_name")
        check_type(plot_name, str)
        self.viewer.ShowPlotByName(plot_name)

    def show_plot_frame_by_name(self, plot_name: str, frame: int) -> None:
        """
        Shows the plot frame with the given name and frame number.

        Args:
            plot_name (str): The name of the plot.
            frame (int): The frame number to show.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="show_plot_frame_by_name")
        check_type(plot_name, str)
        check_type(frame, int)
        check_is_non_negative(frame)
        self.viewer.ShowPlotFrameByName(plot_name, frame)

    @property
    def active_plot(self) -> Plot:
        """
        Gets the active plot.

        Returns:
            Plot: The active plot.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="active_plot")
        result = self.viewer.ActivePlot
        if result is None:
            return None
        return Plot(result)
