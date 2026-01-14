# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MoldSurfaceGenerator Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import check_type, check_and_coerce_optional, check_and_coerce_optional
from .com_proxy import safe_com
from .vector import Vector


class MoldSurfaceGenerator:
    """
    Wrapper for MoldSurfaceGenerator class of Moldflow Synergy.
    """

    def __init__(self, _mold_surface_generator):
        """
        Initialize the MoldSurfaceGenerator with a MoldSurfaceGenerator instance from COM.

        Args:
            _mold_surface_generator: The MoldSurfaceGenerator instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MoldSurfaceGenerator")
        self.mold_surface_generator = safe_com(_mold_surface_generator)

    def generate(self) -> bool:
        """
        Generate the mold surfaces

        Returns:
            bool: True if the generation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="generate")
        return self.mold_surface_generator.Generate

    @property
    def centered(self) -> bool:
        """
        Specifies whether the mold surface should be centered around your model.

        :getter: Get the mold surface is centered around your model
        :setter: Set the mold surface to be centered around your model.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="centered")
        return self.mold_surface_generator.Centered

    @centered.setter
    def centered(self, value: bool) -> None:
        """
        Set the mold surface to be centered around your model.

        Args:
            value (bool): True if the mold surface should be centered, False otherwise.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="centered", value=value)
        check_type(value, bool)
        self.mold_surface_generator.Centered = value

    @property
    def origin(self) -> Vector:
        """
        Get the origin of the mold surface.

        :getter: Get the origin of the mold surface.
        :setter: Set the origin of the mold surface.
        :type: Vector
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="origin")
        result = self.mold_surface_generator.Origin
        if result is None:
            return None
        return Vector(result)

    @origin.setter
    def origin(self, value: Vector | None) -> None:
        """
        Set the origin of the mold surface.

        Args:
            value (Vector): The new origin of the mold surface.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="origin", value=value)

        self.mold_surface_generator.Origin = check_and_coerce_optional(value, Vector)

    @property
    def dimensions(self) -> Vector:
        """
        Get the dimensions of the mold surface.

        :getter: Get the dimensions of the mold surface.
        :setter: Set the dimensions of the mold surface.
        :type: Vector
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="dimensions")
        result = self.mold_surface_generator.Dimensions
        if result is None:
            return None
        return Vector(result)

    @dimensions.setter
    def dimensions(self, value: Vector | None) -> None:
        """
        Set the dimensions of the mold surface.

        Args:
            value (Vector): The new dimensions of the mold surface.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="dimensions", value=value)

        self.mold_surface_generator.Dimensions = check_and_coerce_optional(value, Vector)

    @property
    def save_as_cad(self) -> bool:
        """
        Specifies whether to generate CAD mold block.

        :getter: Get whether to generate CAD mold block.
        :setter: Set whether to generate CAD mold block.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="save_as_cad")
        return self.mold_surface_generator.SaveAsCAD

    @save_as_cad.setter
    def save_as_cad(self, value: bool) -> None:
        """
        Set whether to generate CAD mold block.

        Args:
            value (bool): True if CAD mold block should be generated, False otherwise.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="save_as_cad", value=value)
        check_type(value, bool)
        self.mold_surface_generator.SaveAsCAD = value

    @property
    def use_cad_merge_tolerance(self) -> bool:
        """
        Specifies whether to use custom merge tolerance on contact interfaces between CAD parts.

        :getter: Get whether to use custom merge tolerance on contact interfaces between CAD parts.
        :setter: Set whether to use custom merge tolerance on contact interfaces between CAD parts.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="use_cad_merge_tolerance")
        return self.mold_surface_generator.UseCADMergeTolerance

    @use_cad_merge_tolerance.setter
    def use_cad_merge_tolerance(self, value: bool) -> None:
        """
        Set whether to use custom merge tolerance on contact interfaces between CAD parts.

        Args:
            value (bool): True if custom merge tolerance should be used, False otherwise.
        """
        process_log(
            __name__, LogMessage.PROPERTY_SET, locals(), name="use_cad_merge_tolerance", value=value
        )
        check_type(value, bool)
        self.mold_surface_generator.UseCADMergeTolerance = value
