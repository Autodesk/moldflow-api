"""
Usage:
    BoundaryConditions Class API Wrapper
"""

from .helper import coerce_optional_dispatch
from .common import LogMessage, AnalysisType, ConstraintType
from .helper import check_type, get_enum_value
from .com_proxy import safe_com
from .logger import process_log
from .ent_list import EntList
from .vector import Vector
from .prop import Property


class BoundaryConditions:
    """
    Wrapper for BoundaryConditions class of Moldflow Synergy.
    """

    def __init__(self, _boundary_conditions):
        """
        Initialize the BoundaryConditions with a BoundaryConditions instance from COM.

        Args:
            _boundary_conditions: The BoundaryConditions instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="BoundaryConditions")
        self.boundary_conditions = safe_com(_boundary_conditions)

    def _check_vector(self, vector: Vector | None) -> Vector:
        """
        Check if the vector is valid.

        Args:
            vector (Vector | None): The vector to check.

        Returns:
            bool: True if the vector is valid, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="check_vector")
        if vector is None:
            return None
        if vector.x == int(vector.x):
            vector.x = get_enum_value(int(vector.x), ConstraintType)
        if vector.y == int(vector.y):
            vector.y = get_enum_value(int(vector.y), ConstraintType)
        if vector.z == int(vector.z):
            vector.z = get_enum_value(int(vector.z), ConstraintType)
        return vector

    def create_entity_list(self) -> EntList:
        """
        Creates a new entity list.

        Returns:
            EntList: The created entity list."""
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.boundary_conditions.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def create_fixed_constraints(self, nodes: EntList | None, analysis: AnalysisType | int) -> int:
        """
        Creates fixed constraints at given nodes for the specified analysis type.

        Args:
            nodes (EntList | None): The nodes to apply the fixed constraints to.
            analysis (AnalysisType | int): The analysis type (e.g., CORE_SHIFT).

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_fixed_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        analysis = get_enum_value(analysis, AnalysisType)
        return self.boundary_conditions.CreateFixedConstraints(
            coerce_optional_dispatch(nodes, "ent_list"), analysis
        )

    def create_core_shift_fixed_constraints(
        self, nodes: EntList | None, retract_time: float = 0
    ) -> int:
        """
        Creates core shift fixed constraints at given nodes with specified retract time.

        Args:
            nodes (EntList | None): The nodes to apply the fixed constraints to.
            retract_time (float): float that specified retract time.

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_fixed_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(retract_time, (float, int))
        return self.boundary_conditions.CreateFixedConstraints2(
            coerce_optional_dispatch(nodes, "ent_list"), retract_time
        )

    def create_pin_constraints(self, nodes: EntList | None, analysis: AnalysisType | int) -> int:
        """
        Creates pin constraints at given nodes for the specified analysis type.

        Args:
            nodes (EntList | None): The nodes to apply the pin constraints to.
            analysis (AnalysisType | int): The analysis type (e.g., WARP).

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_pin_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        analysis = get_enum_value(analysis, AnalysisType)
        return self.boundary_conditions.CreatePinConstraints(
            coerce_optional_dispatch(nodes, "ent_list"), analysis
        )

    def create_core_shift_pin_constraints(
        self, nodes: EntList | None, retract_time: float = 0
    ) -> int:
        """
        Creates core shift pin constraints at given nodes with specified retract time.

        Args:
            nodes (EntList | None): The nodes to apply the pin constraints to.
            retract_time (float): Optional retract time for CORE_SHIFT analysis.

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_pin_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(retract_time, (float, int))
        return self.boundary_conditions.CreatePinConstraints2(
            coerce_optional_dispatch(nodes, "ent_list"), retract_time
        )

    # pylint: disable-next=R0913,R0917
    def create_spring_constraints(
        self,
        nodes: EntList | None,
        analysis: AnalysisType | int,
        trans: Vector | None,
        rotation: Vector | None,
    ) -> int:
        """
        Creates spring constraints at given nodes for the specified analysis type.

        Args:
            nodes (EntList | None): The nodes to apply the spring constraints to.
            analysis (AnalysisType | int): The analysis type (e.g., WARP).
            trans (Vector | None): Vector object that specifies translation stiffnesses
            rotation (Vector | None): Vector object that specifies rotation stiffnesses

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_spring_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        analysis = get_enum_value(analysis, AnalysisType)
        if trans is not None:
            check_type(trans, Vector)
        if rotation is not None:
            check_type(rotation, Vector)
        return self.boundary_conditions.CreateSpringConstraints(
            coerce_optional_dispatch(nodes, "ent_list"),
            analysis,
            coerce_optional_dispatch(trans, "vector"),
            coerce_optional_dispatch(rotation, "vector"),
        )

    # pylint: disable-next=R0913,R0917
    def create_core_shift_spring_constraints(
        self,
        nodes: EntList | None,
        trans: Vector | None,
        rotation: Vector | None,
        retract_time: float = 0,
    ) -> int:
        """
        Creates core shift spring constraints at given nodes with specified retract time.

        Args:
            nodes (EntList | None): The nodes to apply the spring constraints to.
            trans (Vector | None): Vector object that specifies translation stiffnesses
            rotation (Vector | None): Vector object that specifies rotation stiffnesses
            retract_time (float): float that specifies retract time

        Returns:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_spring_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        if trans is not None:
            check_type(trans, Vector)
        if rotation is not None:
            check_type(rotation, Vector)
        check_type(retract_time, (float, int))
        return self.boundary_conditions.CreateSpringConstraints2(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(trans, "vector"),
            coerce_optional_dispatch(rotation, "vector"),
            retract_time,
        )

    # pylint: disable-next=R0913,R0917
    def create_general_constraints(
        self,
        nodes: EntList | None,
        analysis: AnalysisType | int,
        trans: Vector | None,
        rotation: Vector | None,
        trans_types: Vector | None,
        rotation_types: Vector | None,
    ) -> int:
        """
        Creates general constraints at given nodes for the specified analysis type.

        Args:
            nodes (EntList | None): EntList object containing nodes to be constrained
            analysis (AnalysisType | int): AnalysisType or int specifying the analysis type
            trans (Vector | None): Vector object specifying translation constraints
            rotation (Vector | None): Vector object specifying rotation constraints
            trans_types (Vector | None): Vector object specifying translation constraint types
            rotation_types (Vector | None): Vector object specifying rotation constraint types

        Return:
            int: Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_general_constraints")
        if nodes is not None:
            check_type(nodes, EntList)
        if trans is not None:
            check_type(trans, Vector)
        if rotation is not None:
            check_type(rotation, Vector)
        if trans_types is not None:
            check_type(trans_types, Vector)
        if rotation_types is not None:
            check_type(rotation_types, Vector)
        analysis = get_enum_value(analysis, AnalysisType)
        trans_types = self._check_vector(trans_types)
        rotation_types = self._check_vector(rotation_types)

        return self.boundary_conditions.CreateGeneralConstraints2(
            coerce_optional_dispatch(nodes, "ent_list"),
            analysis,
            coerce_optional_dispatch(trans, "vector"),
            coerce_optional_dispatch(rotation, "vector"),
            coerce_optional_dispatch(trans_types, "vector"),
            coerce_optional_dispatch(rotation_types, "vector"),
        )

    # pylint: disable-next=R0913,R0917
    def create_core_shift_general_constraints(
        self,
        nodes: EntList | None,
        trans: Vector | None,
        rotation: Vector | None,
        trans_types: Vector | None,
        rotation_types: Vector | None,
        retract_time: float = 0,
    ) -> int:
        """
        Creates core shift general constraints at given nodes with specified retract time.

        Args:
            nodes (EntList | None): EntList object containing nodes to be constrained
            trans (Vector | None): Vector object specifying translation constraints
            rotation (Vector | None): Vector object specifying rotation constraints
            trans_types (Vector | None): Vector object specifying translation constraint types
            rotation_types (Vector | None): Vector object specifying rotation constraint types
            retract_time (float): float specifying the retract time

        Return:
            int: Number of constraints created
        """
        process_log(
            __name__,
            LogMessage.FUNCTION_CALL,
            locals(),
            name="create_core_shift_general_constraints",
        )
        if nodes is not None:
            check_type(nodes, EntList)
        if trans is not None:
            check_type(trans, Vector)
        if rotation is not None:
            check_type(rotation, Vector)
        if trans_types is not None:
            check_type(trans_types, Vector)
        if rotation_types is not None:
            check_type(rotation_types, Vector)
        check_type(retract_time, (int, float))
        trans_types = self._check_vector(trans_types)
        rotation_types = self._check_vector(rotation_types)
        return self.boundary_conditions.CreateGeneralConstraints3(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(trans, "vector"),
            coerce_optional_dispatch(rotation, "vector"),
            coerce_optional_dispatch(trans_types, "vector"),
            coerce_optional_dispatch(rotation_types, "vector"),
            retract_time,
        )

    def create_nodal_loads(
        self, nodes: EntList | None, force: Vector | None, moment: Vector | None
    ) -> int:
        """
        Creates nodal loads at selected nodes

        Args:
            nodes (EntList | None): The nodes to apply the nodal loads to.
            force (Vector | None): The force vector.
            moment (Vector | None): The moment vector.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_nodal_loads")
        if nodes is not None:
            check_type(nodes, EntList)
        if force is not None:
            check_type(force, Vector)
        if moment is not None:
            check_type(moment, Vector)
        return self.boundary_conditions.CreateNodalLoads(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(force, "vector"),
            coerce_optional_dispatch(moment, "vector"),
        )

    def create_edge_loads(self, nodes: EntList | None, force: Vector | None) -> int:
        """
        Creates edge loads at selected nodes

        Args:
            nodes (EntList | None): The nodes to apply the edge loads to.
            force (Vector | None): The force vector.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_edge_loads")
        if nodes is not None:
            check_type(nodes, EntList)
        if force is not None:
            check_type(force, Vector)
        return self.boundary_conditions.CreateEdgeLoads(
            coerce_optional_dispatch(nodes, "ent_list"), coerce_optional_dispatch(force, "vector")
        )

    def create_elemental_loads(self, tri: EntList | None, force: Vector | None) -> int:
        """
        Creates elemental loads at selected elements

        Args:
            tri (EntList | None): The elements containing triangles to be loaded.
            force (Vector | None): The force vector.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_elemental_loads")
        if tri is not None:
            check_type(tri, EntList)
        if force is not None:
            check_type(force, Vector)
        return self.boundary_conditions.CreateElementalLoads(
            coerce_optional_dispatch(tri, "ent_list"), coerce_optional_dispatch(force, "vector")
        )

    def create_pressure_loads(self, tri: EntList | None, pressure: float) -> int:
        """
        Creates pressure loads at selected elements

        Args:
            tri (EntList | None): The elements containing triangles to be loaded.
            pressure (float): The pressure value.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_pressure_loads")
        if tri is not None:
            check_type(tri, EntList)
        check_type(pressure, (float, int))
        return self.boundary_conditions.CreatePressureLoads(
            coerce_optional_dispatch(tri, "ent_list"), pressure
        )

    def create_temperature_loads(self, tri: EntList | None, top: float, bottom: float) -> int:
        """
        Creates temperature loads at selected elements

        Args:
            tri (EntList | None): The elements containing triangles to be loaded.
            top (float): Temperature at the top of the element.
            bottom (float): Temperature at the bottom of the element.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_temperature_loads")
        if tri is not None:
            check_type(tri, EntList)
        check_type(top, (float, int))
        check_type(bottom, (float, int))
        return self.boundary_conditions.CreateTemperatureLoads(
            coerce_optional_dispatch(tri, "ent_list"), top, bottom
        )

    def create_volume_loads(self, tri: EntList | None, force: Vector | None) -> int:
        """
        Creates volume loads at selected elements

        Args:
            tri (EntList | None): The elements containing triangles to be loaded.
            force (Vector | None): The force vector.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_volume_loads")
        if tri is not None:
            check_type(tri, EntList)
        if force is not None:
            check_type(force, Vector)
        return self.boundary_conditions.CreateVolumeLoads(
            coerce_optional_dispatch(tri, "ent_list"), coerce_optional_dispatch(force, "vector")
        )

    def create_critical_dimension(
        self, node1: EntList | None, node2: EntList | None, upper: float, lower: float
    ) -> int:
        """
        Creates a critical dimension between two nodes

        Args:
            node1 (EntList | None): The first node.
            node2 (EntList | None): The second node.
            upper (float): Upper Dimensional tolerance.
            lower (float): Lower Dimensional tolerance.

        Returns:
            int: Number of loads created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_critical_dimension")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        check_type(upper, (float, int))
        check_type(lower, (float, int))
        return self.boundary_conditions.CreateCriticalDimension(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            upper,
            lower,
        )

    def create_doe_critical_dimension(
        self, node1: EntList | None, node2: EntList | None, name: str
    ) -> int:
        """
        Creates a DOE critical dimension between two nodes

        Args:
            node1 (EntList | None): The first node.
            node2 (EntList | None): The second node.
            name (str): Name of the DOE critical dimension.

        Returns:
            int: Number of loads created
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="create_doe_critical_dimension"
        )
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        check_type(name, str)
        return self.boundary_conditions.CreateDoeCriticalDimension(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            name,
        )

    def create_ndbc(
        self, nodes: EntList | None, normal: Vector | None, prop_type: int, prop: Property | None
    ) -> EntList:
        """
        Creates a "generic" boundary condition such as:
            injection entrance, coolant entrance, gas entrance, etc.

        Args:
            nodes (EntList | None): The nodes to apply the boundary condition to.
            normal (Vector | None): The normal vector of the boundary condition.
            prop_type (int): Specifies the property type of the boundary condition
            prop (Property | None): Property that needs to be attached to the boundary condition.
            Specify Nothing to automatically create or select one for the given property type

        Returns:
            EntList: The list of NDBC that were created.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_ndbc")
        if nodes is not None:
            check_type(nodes, EntList)
        if normal is not None:
            check_type(normal, Vector)
        check_type(prop_type, int)
        if prop is not None:
            check_type(prop, Property)
        prop_disp = coerce_optional_dispatch(prop, "prop")
        result = self.boundary_conditions.CreateNDBC(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(normal, "vector"),
            prop_type,
            prop_disp,
        )
        if result is None:
            return None
        return EntList(result)

    def create_ndbc_at_xyz(
        self, coord: Vector | None, normal: Vector | None, prop_type: int, prop: Property | None
    ) -> EntList:
        """
        Creates a "generic" boundary condition such as:
            injection entrance, coolant entrance, gas entrance, etc.

        Args:
            coord (Vector | None): The coordinates of the boundary condition.
            normal (Vector | None): The normal vector of the boundary condition.
            prop_type (int): Specifies the property type of the boundary condition
            prop (Property | None): Property that needs to be attached to the boundary condition.
            Specify Nothing to automatically create or select one for the given property type

        Returns:
            EntList: The list of NDBC that were created.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_ndbc_at_xyz")
        if coord is not None:
            check_type(coord, Vector)
        if normal is not None:
            check_type(normal, Vector)
        check_type(prop_type, int)
        if prop is not None:
            check_type(prop, Property)
        prop_disp = coerce_optional_dispatch(prop, "prop")
        result = self.boundary_conditions.CreateNDBCAtXYZ(
            coerce_optional_dispatch(coord, "vector"),
            coerce_optional_dispatch(normal, "vector"),
            prop_type,
            prop_disp,
        )
        if result is None:
            return None
        return EntList(result)

    def move_ndbc(self, ndbc: EntList | None, nodes: EntList | None, normal: Vector | None) -> bool:
        """
        Moves the NDBC to the specified nodes and normal vector.

        Args:
            ndbc (EntList | None): The NDBC to move.
            nodes (EntList | None): The nodes to move the NDBC to.
            normal (Vector | None): The normal vector of the NDBC.

        Returns:
            bool: True if the NDBC was moved successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_ndbc")
        if ndbc is not None:
            check_type(ndbc, EntList)
        if nodes is not None:
            check_type(nodes, EntList)
        if normal is not None:
            check_type(normal, Vector)
        return self.boundary_conditions.MoveNDBC(
            coerce_optional_dispatch(ndbc, "ent_list"),
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(normal, "vector"),
        )

    def move_ndbc_to_xyz(
        self, ndbc: EntList | None, coord: Vector | None, normal: Vector | None
    ) -> bool:
        """
        Moves a boundary condition to a different position

        Args:
            ndbc (EntList | None): The NDBC to move.
            coord (Vector | None): The coordinates to move the NDBC to.
            normal (Vector | None): The normal vector of the NDBC.

        Returns:
            bool: True if successful; False if not
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_ndbc_to_xyz")
        if ndbc is not None:
            check_type(ndbc, EntList)
        if coord is not None:
            check_type(coord, Vector)
        if normal is not None:
            check_type(normal, Vector)
        return self.boundary_conditions.MoveNDBCToXYZ(
            coerce_optional_dispatch(ndbc, "ent_list"),
            coerce_optional_dispatch(coord, "vector"),
            coerce_optional_dispatch(normal, "vector"),
        )

    def find_property(self, prop_type: int, prop_id: int) -> Property:
        """
        Finds a property by its type and ID.

        Args:
            prop_type (int): The type of the property.
            prop_id (int): The ID of the property.

        Returns:
            Property: The found property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_property")
        check_type(prop_type, int)
        check_type(prop_id, int)
        result = self.boundary_conditions.FindProperty(prop_type, prop_id)
        if result is None:
            return None
        return Property(result)

    def set_prohibited_gate_nodes(self, nodes: EntList | None, analysis: AnalysisType | int) -> int:
        """
        Sets the nodes as prohibited gate nodes for the specified analysis type.

        Args:
            nodes (EntList | None): The nodes to set as prohibited gate nodes.
            analysis (AnalysisType | int): The analysis type (e.g., WARP).

        Returns:
            int : Number of constraints created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="set_prohibited_gate_nodes")
        if nodes is not None:
            check_type(nodes, EntList)
        analysis = get_enum_value(analysis, AnalysisType)
        return self.boundary_conditions.SetProhibitedGateNodes(
            coerce_optional_dispatch(nodes, "ent_list"), analysis
        )

    # pylint: disable-next=R0913,R0917
    def create_one_sided_constraints(
        self,
        nodes: EntList | None,
        positive_trans: Vector | None,
        negative_trans: Vector | None,
        positive_trans_types: Vector | None,
        negative_trans_types: Vector | None,
        retract_time: float = 0,
    ) -> int:
        """
        Creates one-sided constraints at given nodes for the specified analysis type.

        Args:
            nodes (EntList | None): The nodes to apply the one-sided constraints to.
            positive_trans (Vector | None): The positive translation vector.
            negative_trans (Vector | None): The negative translation vector.
            positive_trans_types (Vector | None): The positive translation types vector.
            negative_trans_types (Vector | None): The negative translation types vector.
            retract_time (float): The retract time.
        Returns:
            int: Number of constraints created
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="create_one_sided_constraints"
        )
        if nodes is not None:
            check_type(nodes, EntList)
        if positive_trans is not None:
            check_type(positive_trans, Vector)
        if negative_trans is not None:
            check_type(negative_trans, Vector)
        if positive_trans_types is not None:
            check_type(positive_trans_types, Vector)
        if negative_trans_types is not None:
            check_type(negative_trans_types, Vector)
        if retract_time != 0:
            check_type(retract_time, (float, int))
            positive_trans_types = self._check_vector(positive_trans_types)
            negative_trans_types = self._check_vector(negative_trans_types)
            return self.boundary_conditions.CreateOneSidedConstraints2(
                coerce_optional_dispatch(nodes, "ent_list"),
                coerce_optional_dispatch(positive_trans, "vector"),
                coerce_optional_dispatch(negative_trans, "vector"),
                coerce_optional_dispatch(positive_trans_types, "vector"),
                coerce_optional_dispatch(negative_trans_types, "vector"),
                retract_time,
            )
        positive_trans_types = self._check_vector(positive_trans_types)
        negative_trans_types = self._check_vector(negative_trans_types)
        return self.boundary_conditions.CreateOneSidedConstraints(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(positive_trans, "vector"),
            coerce_optional_dispatch(negative_trans, "vector"),
            coerce_optional_dispatch(positive_trans_types, "vector"),
            coerce_optional_dispatch(negative_trans_types, "vector"),
        )
