# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    Modeler Class API Wrapper
"""

# pylint: disable=C0302

from .logger import process_log
from .common import LogMessage, CurveInitPosition, LCSType
from .helper import (
    check_is_non_negative,
    check_is_positive,
    check_type,
    get_enum_value,
    coerce_optional_dispatch,
)
from .com_proxy import safe_com
from .boundary_list import BoundaryList
from .prop import Property
from .vector_array import VectorArray
from .ent_list import EntList
from .vector import Vector


class Modeler:
    """
    Wrapper for Modeler class of Moldflow Synergy.
    """

    def __init__(self, _modeler):
        """
        Initialize the Modeler with a Modeler instance from COM.

        Args:
            _modeler: The Modeler instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="Modeler")
        self.modeler = safe_com(_modeler)

    def create_node_by_xyz(self, coord: Vector | None) -> EntList:
        """
        Create a node by its coordinates.

        Args:
            coord (Vector): The coordinates of the node.

        Returns:
            int: The ID of the created node.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_node_by_xyz")
        if coord is not None:
            check_type(coord, Vector)
        result = self.modeler.CreateNodeByXYZ(coerce_optional_dispatch(coord, "vector"))
        if result is None:
            return None
        return EntList(result)

    def create_nodes_between(
        self, start: Vector | None, end: Vector | None, num_nodes: int
    ) -> EntList:
        """
        Creates a set of nodes between two given points

        Args:
            start (Vector): Specifies the coordinates of the first point
            end (Vector): Specifies the coordinates of the second point
            num_nodes (int): The number of nodes to create.

        Returns:
            EntList: The list of created nodes.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_nodes_between")
        if start is not None:
            check_type(start, Vector)
        if end is not None:
            check_type(end, Vector)
        check_type(num_nodes, int)
        check_is_positive(num_nodes)
        result = self.modeler.CreateNodesBetween(
            coerce_optional_dispatch(start, "vector"),
            coerce_optional_dispatch(end, "vector"),
            num_nodes,
        )
        if result is None:
            return None
        return EntList(result)

    def create_nodes_by_offset(
        self, coord: Vector | None, offset: Vector | None, num_nodes: int
    ) -> EntList:
        """
        Creates a set of nodes by an offset operation

        Args:
            coord (Vector): The starting point.
            offset (Vector): The offset vector.
            num_nodes (int): The number of nodes to create.

        Returns:
            EntList: The list of created nodes.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_nodes_by_offset")
        if coord is not None:
            check_type(coord, Vector)
        if offset is not None:
            check_type(offset, Vector)
        check_type(num_nodes, int)
        check_is_positive(num_nodes)
        result = self.modeler.CreateNodesByOffset(
            coerce_optional_dispatch(coord, "vector"),
            coerce_optional_dispatch(offset, "vector"),
            num_nodes,
        )
        if result is None:
            return None
        return EntList(result)

    def create_nodes_by_divide(self, curve: EntList | None, num_nodes: int, ends: bool) -> EntList:
        """
        Creates a set of nodes by dividing a curve (the curve itself is not modified)

        Args:
            curve (EntList): The curve to divide.
            num_nodes (int): The number of nodes to create.
            ends (bool): Whether to include the endpoints.

        Returns:
            EntList: The list of created nodes.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_nodes_by_divide")
        if curve is not None:
            check_type(curve, EntList)
        check_type(num_nodes, int)
        check_is_positive(num_nodes)
        check_type(ends, bool)
        result = self.modeler.CreateNodesByDivide(
            coerce_optional_dispatch(curve, "ent_list"), num_nodes, ends
        )
        if result is None:
            return None
        return EntList(result)

    def create_entity_list(self) -> EntList:
        """
        Creates an empty EntList object

        Returns:
            EntList: The created entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.modeler.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def create_node_by_intersect(
        self, curve: EntList | None, curve2: EntList | None, pt: Vector | None
    ) -> EntList:
        """
        Creates a node at an intersection of two curves

        Args:
            curve (EntList): The first curve.
            curve2 (EntList): The second curve.
            pt (Vector): The point of intersection.

        Returns:
            EntList: The list of created nodes.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_node_by_intersect")
        if curve is not None:
            check_type(curve, EntList)
        if curve2 is not None:
            check_type(curve2, EntList)
        if pt is not None:
            check_type(pt, Vector)
        result = self.modeler.CreateNodeByIntersect(
            coerce_optional_dispatch(curve, "ent_list"),
            coerce_optional_dispatch(curve2, "ent_list"),
            coerce_optional_dispatch(pt, "vector"),
        )
        if result is None:
            return None
        return EntList(result)

    # pylint: disable=R0913, R0917
    def create_line(
        self,
        coord: Vector | None,
        vec: Vector | None,
        relative: bool,
        prop_set: Property | None,
        ends: bool,
    ) -> EntList:
        """
        Creates a line from between two given points

         Args:
             coord (Vector): The starting point of the line.
             vec (Vector): The direction vector of the line.
             relative (bool): Specify False if Vec specifies the coordinates of the second point
             True if Vec specifies an offset will be added to the first point to obtain the second
             prop_set (Property): The property set for the line.
             ends (bool): Whether to include the endpoints.

         Returns:
             EntList: The list of created lines.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_line")
        if coord is not None:
            check_type(coord, Vector)
        if vec is not None:
            check_type(vec, Vector)
        check_type(relative, bool)
        if prop_set is not None:
            check_type(prop_set, Property)
        check_type(ends, bool)
        prop_disp = coerce_optional_dispatch(prop_set, "prop")
        result = self.modeler.CreateLine(
            coerce_optional_dispatch(coord, "vector"),
            coerce_optional_dispatch(vec, "vector"),
            relative,
            prop_disp,
            ends,
        )
        if result is None:
            return None
        return EntList(result)

    # pylint: disable=R0913, R0917
    def create_arc_by_angle(
        self,
        center: Vector | None,
        radius: float,
        start: float,
        end: float,
        prop_set: Property | None,
        ends: bool,
    ) -> EntList:
        """
        Creates an arc from a center and start and end angles

        Args:
            center (Vector): The center of the arc.
            radius (float): The radius of the arc.
            start (float): The starting angle of the arc.
            end (float): The ending angle of the arc.
            prop_set (Property): The property set for the arc.
            ends (bool): Whether to include the endpoints.

        Returns:
            EntList: The list of created arcs.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_arc_by_angle")
        if center is not None:
            check_type(center, Vector)
        check_type(radius, (int, float))
        check_is_positive(radius)
        check_type(start, (int, float))
        check_type(end, (int, float))
        if prop_set is not None:
            check_type(prop_set, Property)
        check_type(ends, bool)
        result = self.modeler.CreateArcByAngle(
            coerce_optional_dispatch(center, "vector"),
            radius,
            start,
            end,
            coerce_optional_dispatch(prop_set, "prop"),
            ends,
        )
        if result is None:
            return None
        return EntList(result)

    # pylint: disable=R0913, R0917
    def create_arc_by_points(
        self,
        pt1: Vector | None,
        pt2: Vector | None,
        pt3: Vector | None,
        circle: bool,
        prop_set: Property | None,
        ends: bool,
    ) -> EntList:
        """
        Creates an arc from three points

        Args:
            pt1 (Vector): The first point.
            pt2 (Vector): The second point.
            pt3 (Vector): The third point.
            circle (bool): Specify True to create a circle
            False to create an arc between the first and third points, respectively
            prop_set (Property): The property set for the arc.
            ends (bool): Whether to include the endpoints.

        Returns:
            EntList: The list of created arcs.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_arc_by_points")
        if pt1 is not None:
            check_type(pt1, Vector)
        if pt2 is not None:
            check_type(pt2, Vector)
        if pt3 is not None:
            check_type(pt3, Vector)
        check_type(circle, bool)
        if prop_set is not None:
            check_type(prop_set, Property)
        check_type(ends, bool)
        result = self.modeler.CreateArcByPoints(
            coerce_optional_dispatch(pt1, "vector"),
            coerce_optional_dispatch(pt2, "vector"),
            coerce_optional_dispatch(pt3, "vector"),
            circle,
            coerce_optional_dispatch(prop_set, "prop"),
            ends,
        )
        # pylint: disable=R0801
        if result is None:
            return None
        return EntList(result)

    def find_property(self, prop_type: int, prop_id: int) -> Property:
        """
        Find a property by its type and ID

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.

        Returns:
            Property: The found property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_property")
        check_type(prop_type, int)
        check_type(prop_id, int)
        result = self.modeler.FindProperty(prop_type, prop_id)
        if result is None:
            return None
        return Property(result)

    # pylint: disable=R0913, R0917
    def create_curve_by_connect(
        self,
        curve1: EntList | None,
        end1: CurveInitPosition | float,
        curve2: EntList | None,
        end2: CurveInitPosition | float,
        factor: float,
        prop_set: Property | None,
    ) -> EntList:
        """
        Creates a curve by connecting two curves

        Args:
            curve1 (EntList): The first curve.
            end1 (float): Specify
            0 to choose the beginning of the first curve
            1 to choose its end
            curve2 (EntList): The second curve.
            end2 (float): Specify
            0 to choose the beginning of the first curve
            1 to choose its end
            factor (float): The fillet factor
            prop_set (Property): The property set for the curve.

        Returns:
            EntList: The list of created curves.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_curve_by_connect")
        if curve1 is not None:
            check_type(curve1, EntList)
        end1 = get_enum_value(end1, CurveInitPosition)
        if curve2 is not None:
            check_type(curve2, EntList)
        end2 = get_enum_value(end2, CurveInitPosition)
        check_type(factor, (int, float))
        if prop_set is not None:
            check_type(prop_set, Property)
        result = self.modeler.CreateCurveByConnect(
            coerce_optional_dispatch(curve1, "ent_list"),
            end1,
            coerce_optional_dispatch(curve2, "ent_list"),
            end2,
            factor,
            coerce_optional_dispatch(prop_set, "prop"),
        )
        if result is None:
            return None
        return EntList(result)

    def create_spline(
        self, coord: VectorArray | None, prop_set: Property | None, ends: bool
    ) -> EntList:
        """
        Creates a spline from a set of points

        Args:
            coord (VectorArray): The coordinates of the spline.
            prop_set (Property): The property that will be assigned to the spline
            ends (bool): Whether to include the endpoints.

        Returns:
            EntList: The list of created splines.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_spline")
        if coord is not None:
            check_type(coord, VectorArray)
        if prop_set is not None:
            check_type(prop_set, Property)
        check_type(ends, bool)
        result = self.modeler.CreateSpline(
            coerce_optional_dispatch(coord, "vector_array"),
            coerce_optional_dispatch(prop_set, "prop"),
            ends,
        )
        if result is None:
            return None
        return EntList(result)

    def break_curves(self, curve1: EntList | None, curve2: EntList | None) -> bool:
        """
        Breaks two curves at their intersection points

        Args:
            curve1 (EntList): The first curve.
            curve2 (EntList): The second curve.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="break_curves")
        if curve1 is not None:
            check_type(curve1, EntList)
        if curve2 is not None:
            check_type(curve2, EntList)
        return self.modeler.BreakCurves(
            coerce_optional_dispatch(curve1, "ent_list"),
            coerce_optional_dispatch(curve2, "ent_list"),
        )

    def set_property(self, ents: EntList | None, prop_set: Property | None) -> bool:
        """
        Sets the property of a set of entities

        Args:
            ents (EntList): The entities to set the property for.
            prop_set (Property): The property set.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_property")
        if ents is not None:
            check_type(ents, EntList)
        if prop_set is not None:
            check_type(prop_set, Property)
        return self.modeler.SetProperty(
            coerce_optional_dispatch(ents, "ent_list"), coerce_optional_dispatch(prop_set, "prop")
        )

    def create_region_by_boundary(
        self, curve: EntList | None, prop_set: Property | None
    ) -> EntList:
        """
        Creates a region from an ordered sequence of boundary curves

        Args:
            curve (EntList): The boundary curve.
            prop_set (Property): The property set for the region.

        Returns:
            EntList: The list of created regions.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_region_by_boundary")
        if curve is not None:
            check_type(curve, EntList)
        if prop_set is not None:
            check_type(prop_set, Property)
        result = self.modeler.CreateRegionByBoundary(
            coerce_optional_dispatch(curve, "ent_list"), coerce_optional_dispatch(prop_set, "prop")
        )
        if result is None:
            return None
        return EntList(result)

    def create_region_by_nodes(self, nodes: EntList | None, prop_set: Property | None) -> EntList:
        """
        Creates a region from an ordered sequence of boundary nodes

        Args:
            nodes (EntList): The nodes for the region.
            prop_set (Property): The property set for the region.

        Returns:
            EntList: The list of created regions.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_region_by_nodes")
        if nodes is not None:
            check_type(nodes, EntList)
        if prop_set is not None:
            check_type(prop_set, Property)
        result = self.modeler.CreateRegionByNodes(
            coerce_optional_dispatch(nodes, "ent_list"), coerce_optional_dispatch(prop_set, "prop")
        )
        if result is None:
            return None
        return EntList(result)

    def create_region_by_ruling(
        self, curve1: EntList | None, curve2: EntList | None, prop_set: Property | None
    ) -> EntList:
        """
        Creates one or more regions between two sets of curves by a ruling operation

        Args:
            curve1 (EntList): The first curve.
            curve2 (EntList): The second curve.
            prop_set (Property): The property set for the region.

        Returns:
            EntList: The list of created regions.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_region_by_ruling")
        if curve1 is not None:
            check_type(curve1, EntList)
        if curve2 is not None:
            check_type(curve2, EntList)
        if prop_set is not None:
            check_type(prop_set, Property)
        result = self.modeler.CreateRegionByRuling(
            coerce_optional_dispatch(curve1, "ent_list"),
            coerce_optional_dispatch(curve2, "ent_list"),
            coerce_optional_dispatch(prop_set, "prop"),
        )
        if result is None:
            return None
        return EntList(result)

    def create_region_by_extrusion(
        self, curve: EntList | None, direction: Vector | None, prop_set: Property | None
    ) -> EntList:
        """
        Creates one or more regions by extruding a set of curves along a given direction vector

        Args:
            curve (EntList): The curve to extrude.
            direction (Vector): The direction vector for extrusion.
            prop_set (Property): The property set for the region.

        Returns:
            EntList: The list of created regions.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_region_by_extrusion")
        if curve is not None:
            check_type(curve, EntList)
        if direction is not None:
            check_type(direction, Vector)
        if prop_set is not None:
            check_type(prop_set, Property)
        result = self.modeler.CreateRegionByExtrusion(
            coerce_optional_dispatch(curve, "ent_list"),
            coerce_optional_dispatch(direction, "vector"),
            coerce_optional_dispatch(prop_set, "prop"),
        )
        if result is None:
            return None
        return EntList(result)

    def create_hole_by_boundary(self, region: EntList | None, curve: EntList | None) -> bool:
        """
        Creates a hole in a region from an ordered sequence of boundary curves

        Args:
            region (EntList): The region to create the hole in.
            curve (EntList): The boundary curve for the hole.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_hole_by_boundary")
        if region is not None:
            check_type(region, EntList)
        if curve is not None:
            check_type(curve, EntList)
        return self.modeler.CreateHoleByBoundary(
            coerce_optional_dispatch(region, "ent_list"),
            coerce_optional_dispatch(curve, "ent_list"),
        )

    def create_hole_by_nodes(self, region: EntList | None, nodes: EntList | None) -> bool:
        """
        Creates a hole in a region from an ordered sequence of boundary nodes

        Args:
            region (EntList): The region to create the hole in.
            nodes (EntList): The nodes for the hole.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_hole_by_nodes")
        if region is not None:
            check_type(region, EntList)
        if nodes is not None:
            check_type(nodes, EntList)
        return self.modeler.CreateHoleByNodes(
            coerce_optional_dispatch(region, "ent_list"),
            coerce_optional_dispatch(nodes, "ent_list"),
        )

    def create_hole_by_ruling(
        self, region: EntList | None, curve1: EntList | None, curve2: EntList | None
    ) -> bool:
        """
        Creates a hole in a region by a ruling operation

        Args:
            region (EntList): The region to create the hole in.
            curve1 (EntList): The first curve.
            curve2 (EntList): The second curve.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_hole_by_ruling")
        if region is not None:
            check_type(region, EntList)
        if curve1 is not None:
            check_type(curve1, EntList)
        if curve2 is not None:
            check_type(curve2, EntList)
        return self.modeler.CreateHoleByRuling(
            coerce_optional_dispatch(region, "ent_list"),
            coerce_optional_dispatch(curve1, "ent_list"),
            coerce_optional_dispatch(curve2, "ent_list"),
        )

    def create_hole_by_extrusion(
        self, region: EntList | None, curve: EntList | None, direction: Vector | None
    ) -> bool:
        """
        Creates a hole in a region by extruding a set of curves along a given direction vector

        Args:
            region (EntList): The region to create the hole in.
            curve (EntList): The curve to extrude.
            direction (Vector): The direction vector for extrusion.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_hole_by_extrusion")
        if region is not None:
            check_type(region, EntList)
        if curve is not None:
            check_type(curve, EntList)
        if direction is not None:
            check_type(direction, Vector)
        return self.modeler.CreateHoleByExtrusion(
            coerce_optional_dispatch(region, "ent_list"),
            coerce_optional_dispatch(curve, "ent_list"),
            coerce_optional_dispatch(direction, "vector"),
        )

    # pylint: disable=R0913, R0917
    def reflect(
        self,
        ent: EntList | None,
        reference: Vector | None,
        plane: Vector | None,
        copy: bool,
        merge: bool,
    ) -> bool:
        """
        Reflects a set of entities about a plane defined by a reference point and a normal vector
        Args:
            ent (EntList): The entities to reflect.
            reference (Vector): The reference point for the reflection.
            plane (Vector): The normal vector of the reflection plane.
            copy (bool): Specify True to create a copy of the reflected entities
            False to move the original entities
            merge (bool): Specify True to merge the reflected entities after reflection

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="reflect")
        if ent is not None:
            check_type(ent, EntList)
        if reference is not None:
            check_type(reference, Vector)
        if plane is not None:
            check_type(plane, Vector)
        check_type(copy, bool)
        check_type(merge, bool)
        return self.modeler.Reflect(
            coerce_optional_dispatch(ent, "ent_list"),
            coerce_optional_dispatch(reference, "vector"),
            coerce_optional_dispatch(plane, "vector"),
            copy,
            merge,
        )

    # pylint: disable=R0913, R0917
    def scale(
        self,
        ent: EntList | None,
        reference: Vector | None,
        scale: Vector | None,
        copy: bool,
        merge: bool,
    ) -> bool:
        """
        Scales a set of entities about a reference point

        Args:
            ent (EntList): The entities to scale.
            reference (Vector): The reference point for the scaling.
            scale (Vector): The scaling factor.
            copy (bool): Specify True to create a copy of the scaled entities
            False to move the original entities
            merge (bool): Specify True to merge the scaled entities after scaling

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="scale")
        if ent is not None:
            check_type(ent, EntList)
        if reference is not None:
            check_type(reference, Vector)
        if scale is not None:
            check_type(scale, Vector)
        check_type(copy, bool)
        check_type(merge, bool)
        return self.modeler.Scale(
            coerce_optional_dispatch(ent, "ent_list"),
            coerce_optional_dispatch(reference, "vector"),
            coerce_optional_dispatch(scale, "vector"),
            copy,
            merge,
        )

    # pylint: disable=R0913, R0917
    def translate(
        self,
        ent: EntList | None,
        translation: Vector | None,
        copy: bool,
        num_copies: int,
        merge: bool,
    ) -> bool:
        """
        Translates a set of entities by a given vector

        Args:
            ent (EntList): The entities to translate.
            translation (Vector): The translation vector.
            copy (bool): Specify True to create a copy of the translated entities
            False to move the original entities
            num_copies (int): The number of copies to create.
            merge (bool): Specify True to merge the translated entities after translation

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="translate")
        if ent is not None:
            check_type(ent, EntList)
        if translation is not None:
            check_type(translation, Vector)
        check_type(copy, bool)
        check_type(num_copies, int)
        check_is_non_negative(num_copies)
        check_type(merge, bool)
        return self.modeler.Translate(
            coerce_optional_dispatch(ent, "ent_list"),
            coerce_optional_dispatch(translation, "vector"),
            copy,
            num_copies,
            merge,
        )

    # pylint: disable=R0913, R0917
    def rotate(
        self,
        ent: EntList | None,
        center: Vector | None,
        axis: Vector | None,
        angle: float,
        copy: bool,
        num_copies: int,
        merge: bool,
    ) -> bool:
        """
        Rotates entities about an axis passing through a reference point

        Args:
            ent (EntList): The entities to rotate.
            center (Vector): The center point for the rotation.
            axis (Vector): The direction vector of the rotation axis.
            angle (float): The rotation angle in degrees.
            copy (bool): Specify True to create a copy of the rotated entities
            False to move the original entities
            num_copies (int): The number of copies to create.
            merge (bool): Specify True to merge the rotated entities after rotation

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate")
        if ent is not None:
            check_type(ent, EntList)
        if center is not None:
            check_type(center, Vector)
        if axis is not None:
            check_type(axis, Vector)
        check_type(angle, (int, float))
        check_is_non_negative(angle)
        check_type(copy, bool)
        check_type(num_copies, int)
        check_is_non_negative(num_copies)
        check_type(merge, bool)
        return self.modeler.Rotate(
            coerce_optional_dispatch(ent, "ent_list"),
            coerce_optional_dispatch(center, "vector"),
            coerce_optional_dispatch(axis, "vector"),
            angle,
            copy,
            num_copies,
            merge,
        )

    # pylint: disable=R0913, R0917
    def rotate_3_pts(
        self,
        ents: EntList | None,
        pt1: Vector | None,
        pt2: Vector | None,
        pt3: Vector | None,
        copy: bool,
        merge: bool,
    ) -> bool:
        """
        Rotates entities about a plane defined by three points

        Args:
            ents (EntList): The entities to rotate.
            pt1 (Vector): The first point defining the plane.
            pt2 (Vector): The second point defining the plane.
            pt3 (Vector): The third point defining the plane.
            copy (bool): Specify True to create a copy of the rotated entities.
                False to move the original entities
            merge (bool): Specify True to merge the rotated entities after rotation.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="rotate_3_pts")
        if ents is not None:
            check_type(ents, EntList)
        if pt1 is not None:
            check_type(pt1, Vector)
        if pt2 is not None:
            check_type(pt2, Vector)
        if pt3 is not None:
            check_type(pt3, Vector)
        check_type(copy, bool)
        check_type(merge, bool)
        return self.modeler.Rotate3Pts(
            coerce_optional_dispatch(ents, "ent_list"),
            coerce_optional_dispatch(pt1, "vector"),
            coerce_optional_dispatch(pt2, "vector"),
            coerce_optional_dispatch(pt3, "vector"),
            copy,
            merge,
        )

    def create_lcs_by_points(
        self, coord1: Vector | None, coord2: Vector | None = None, coord3: Vector | None = None
    ) -> EntList:
        """
        Creates a local coordinate system (LCS) from three points

        Args:
            coord1 (Vector): The first point.
            coord2 (Vector): The second point. Specify None if only 1 point
            coord3 (Vector): The third point. Specify None if only 2 points

        Returns:
            EntList: The created local coordinate system.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_lcs_by_points")
        if coord1 is not None:
            check_type(coord1, Vector)
        if coord2 is not None:
            check_type(coord2, Vector)
        if coord3 is not None:
            check_type(coord3, Vector)
        result = self.modeler.CreateLCSByPoints(
            coerce_optional_dispatch(coord1, "vector"),
            coerce_optional_dispatch(coord2, "vector"),
            coerce_optional_dispatch(coord3, "vector"),
        )
        if result is None:
            return None
        return EntList(result)

    def activate_lcs(self, lcs: EntList | None, active: bool, lcs_type: LCSType | str) -> bool:
        """
        Activates or deactivates a local coordinate system (LCS)

        Args:
            lcs (EntList): The LCS to activate or deactivate.
            active (bool): Specify True to activate the LCS
            False to deactivate it
            lcs_type (LCSType | str): The type of the LCS. Ignored if LCS is deactivated

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="activate_lcs")
        if lcs is not None:
            check_type(lcs, EntList)
        check_type(active, bool)
        lcs_type = get_enum_value(lcs_type, LCSType)
        return self.modeler.ActivateLCS(coerce_optional_dispatch(lcs, "ent_list"), active, lcs_type)

    def create_boundary_list(self) -> BoundaryList:
        """
        Creates an empty BoundaryList object

        Returns:
            BoundaryList: The created boundary list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_boundary_list")
        result = self.modeler.CreateBoundaryList
        if result is None:
            return None
        return BoundaryList(result)

    # pylint: disable=R0913, R0917
    def set_mesh_size(
        self,
        global_size: float,
        ents: EntList | None,
        boundaries: BoundaryList | None,
        size: float,
        cad_bodies: EntList | None,
        num_layer: int,
    ) -> bool:
        """
        Sets the mesh size for a set of entities.

        Args:
            global_size (float): The global mesh size.
            ents (EntList): The entities to set the mesh size for.
            boundaries (BoundaryList): The boundaries to set the mesh size for.
            size (float): The mesh size.
            cad_bodies (EntList): The CAD bodies to set the mesh size for.
            num_layer (int): The number of layers.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_mesh_size")
        check_type(global_size, (int, float))
        check_is_non_negative(global_size)
        if ents is not None:
            check_type(ents, EntList)
        if boundaries is not None:
            check_type(boundaries, BoundaryList)
        check_type(size, (int, float))
        check_is_positive(size)
        if cad_bodies is not None:
            check_type(cad_bodies, EntList)
        check_type(num_layer, int)
        check_is_non_negative(num_layer)
        return self.modeler.SetMeshSize2(
            global_size,
            coerce_optional_dispatch(ents, "ent_list"),
            coerce_optional_dispatch(boundaries, "boundary_list"),
            size,
            coerce_optional_dispatch(cad_bodies, "ent_list"),
            num_layer,
        )

    def scale_mesh_density(
        self, ents: EntList | None, boundaries: BoundaryList | None, scale: float
    ) -> bool:
        """
        Scales the mesh density of a set of entities

        Args:
            ents (EntList): The entities to scale.
            boundaries (BoundaryList): The boundaries for the scaling.
            scale (float): The scaling factor.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="scale_mesh_density")
        if ents is not None:
            check_type(ents, EntList)
        if boundaries is not None:
            check_type(boundaries, BoundaryList)
        check_type(scale, (int, float))
        check_is_positive(scale)
        return self.modeler.ScaleMeshDensity(
            coerce_optional_dispatch(ents, "ent_list"),
            coerce_optional_dispatch(boundaries, "boundary_list"),
            scale,
        )

    def modified_with_inventor_fusion(self, ents: EntList | None) -> int:
        """
        Modifies a set of entities with Inventor Fusion

        Args:
            ents (EntList): The entities to modify.

        Returns:
            int: Task ID for CAD editing
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="modified_with_inventor_fusion"
        )
        if ents is not None:
            check_type(ents, EntList)
        return self.modeler.ModifiedWithInventorFusion(coerce_optional_dispatch(ents, "ent_list"))

    def is_inventor_fusion_cad_edit_done(self, job_id: int) -> bool:
        """
        Checks if the Inventor Fusion CAD edit is done

        Args:
            job_id (int): The task ID for CAD editing.

        Returns:
            bool: True if the operation is completed, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="is_inventor_fusion_cad_edit_done"
        )
        check_type(job_id, int)
        return self.modeler.IsInventorFusionCadEditDone(job_id)

    def get_new_edited_cad_study_name(self, job_id: int) -> str:
        """
        Gets the name of the new edited CAD study

        Args:
            job_id (int): The task ID for CAD editing.

        Returns:
            str: The name of the new edited CAD study.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="get_new_edited_cad_study_name"
        )
        check_type(job_id, int)
        return self.modeler.GetNewEditedCadStudyName(job_id)

    def is_inventor_fusion_cad_edit_aborted(self, job_id: int) -> bool:
        """
        Checks if the Inventor Fusion CAD edit is aborted

        Args:
            job_id (int): The task ID for CAD editing.

        Returns:
            bool: True if the operation was aborted, False otherwise.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="is_inventor_fusion_cad_edit_aborted"
        )
        check_type(job_id, int)
        return self.modeler.IsInventorFusionCadEditAborted(job_id)

    def center_lines(self) -> bool:
        """
        Extract center lines from visible CAD bodies with Channel (3D) property.
        Tapered bodies or flat bodies will not be processed.

         Returns:
             bool: True if the operation was successful, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="center_lines")
        return self.modeler.CenterLines
