# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    PredicateManager Class API Wrapper
"""

from .predicate import Predicate
from .double_array import DoubleArray
from .common import CrossSectionType, LogMessage
from .helper import check_type, get_enum_value, check_range, coerce_optional_dispatch
from .com_proxy import safe_com
from .logger import process_log


class PredicateManager:
    """
    Wrapper for PredicateManager class of Moldflow Synergy.
    """

    def __init__(self, _predicate_manager):
        """
        Initialize the PredicateManager with a PredicateManager instance from COM.

        Args:
            _predicate_manager: The PredicateManager instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="PredicateManager")
        self.predicate_manager = safe_com(_predicate_manager)

    def create_label_predicate(self, label: str) -> Predicate:
        """
        Create a predicate for a label range.

        Args:
            label (str): The label to create the predicate for.

        Returns:
            Predicate: The created label predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_label_predicate")
        check_type(label, str)
        result = self.predicate_manager.CreateLabelPredicate(label)
        if result is None:
            return None
        return Predicate(result)

    def create_property_predicate(self, property_type: int, property_id: int) -> Predicate:
        """
        Create a predicate for a property.

        Args:
            property_type (int): The type of the property.
            property_id (int): The id of the property.

        Returns:
            Predicate: The created property predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_property_predicate")
        check_type(property_type, int)
        check_type(property_id, int)
        result = self.predicate_manager.CreatePropertyPredicate(property_type, property_id)
        if result is None:
            return None
        return Predicate(result)

    def create_prop_type_predicate(self, prop_type: int) -> Predicate:
        """
        Create a predicate for a property type.

        Args:
            prop_type (int): The type of the property.

        Returns:
            Predicate: The created property type predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_prop_type_predicate")
        check_type(prop_type, int)
        result = self.predicate_manager.CreatePropTypePredicate(prop_type)
        if result is None:
            return None
        return Predicate(result)

    def create_thickness_predicate(self, min_value: float, max_value: float) -> Predicate:
        """
        Create a predicate for a thickness range.

        Args:
            min_value (float): The minimum thickness.
            max_value (float): The maximum thickness.

        Returns:
            Predicate: The created thickness predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_thickness_predicate")
        check_type(min_value, (int, float))
        check_type(max_value, (int, float))
        check_range(min_value, None, max_value, False, True)
        result = self.predicate_manager.CreateThicknessPredicate(min_value, max_value)
        if result is None:
            return None
        return Predicate(result)

    def create_bool_and_predicate(
        self, predicate1: Predicate | None, predicate2: Predicate | None
    ) -> Predicate:
        """
        Creates a predicate from two predicates using a boolean AND operation.
        An entity satisfies the AND predicate if it satisfies both its "child" predicates

        Args:
            predicate1 (Predicate | None): The left predicate.
            predicate2 (Predicate | None): The right predicate.

        Returns:
            Predicate: The created AND predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_bool_and_predicate")
        if predicate1 is not None:
            check_type(predicate1, Predicate)
        if predicate2 is not None:
            check_type(predicate2, Predicate)
        result = self.predicate_manager.CreateBoolAndPredicate(
            coerce_optional_dispatch(predicate1, "predicate"),
            coerce_optional_dispatch(predicate2, "predicate"),
        )

        if result is None:
            return None
        return Predicate(result)

    def create_bool_or_predicate(
        self, predicate1: Predicate | None, predicate2: Predicate | None
    ) -> Predicate:
        """
        Creates a predicate from two predicates using a boolean OR operation.
        An entity satisfies the OR predicate if it satisfies either of its "child" predicates"

        Args:
            predicate1 (Predicate | None): The left predicate.
            predicate2 (Predicate | None): The right predicate.

        Returns:
            Predicate: The created OR predicate
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_bool_or_predicate")
        if predicate1 is not None:
            check_type(predicate1, Predicate)
        if predicate2 is not None:
            check_type(predicate2, Predicate)
        result = self.predicate_manager.CreateBoolOrPredicate(
            coerce_optional_dispatch(predicate1, "predicate"),
            coerce_optional_dispatch(predicate2, "predicate"),
        )
        if result is None:
            return None
        return Predicate(result)

    def create_bool_not_predicate(self, predicate: Predicate | None) -> Predicate:
        """
        Creates a predicate from a predicate using a boolean NOT operation.
        An entity satisfies the NOT predicate if it does not satisfy its "child" predicate.

        Args:
            predicate (Predicate | None): The predicate to negate.

        Returns:
            Predicate: The created NOT predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_bool_not_predicate")
        if predicate is not None:
            check_type(predicate, Predicate)
        result = self.predicate_manager.CreateBoolNotPredicate(
            coerce_optional_dispatch(predicate, "predicate")
        )
        if result is None:
            return None
        return Predicate(result)

    def create_bool_xor_predicate(
        self, predicate1: Predicate | None, predicate2: Predicate | None
    ) -> Predicate:
        """
        Creates a predicate from two predicates using a boolean XOR operation.
        An entity satisfies the XOR predicate if it satisfies exactly one of its "child" predicates.

        Args:
            predicate1 (Predicate | None): The left predicate.
            predicate2 (Predicate | None): The right predicate.

        Returns:
            Predicate: The created XOR predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_bool_xor_predicate")
        if predicate1 is not None:
            check_type(predicate1, Predicate)
        if predicate2 is not None:
            check_type(predicate2, Predicate)
        result = self.predicate_manager.CreateBoolXorPredicate(
            coerce_optional_dispatch(predicate1, "predicate"),
            coerce_optional_dispatch(predicate2, "predicate"),
        )

        if result is None:
            return None
        return Predicate(result)

    def create_x_section_predicate(
        self,
        cross_section: CrossSectionType | str,
        min_value: DoubleArray | None,
        max_value: DoubleArray | None,
    ) -> Predicate:
        """
        Create a predicate for a cross section.

        Args:
            cross_section (CrossSectionType | str): The cross section type.
            min_value (DoubleArray | None): The minimum values for the cross section.
            max_value (DoubleArray | None): The maximum values for the cross section.

        +---------------+--------------------------------+
        | Cross Section | Parameters                     |
        +===============+================================+
        | Circular      | Diameter                       |
        +---------------+--------------------------------+
        | Rectangular   | Width, Height                  |
        +---------------+--------------------------------+
        | Annular       | Outer Diameter, Inner Diameter |
        +---------------+--------------------------------+
        | Half-Circular | Diameter, Height               |
        +---------------+--------------------------------+
        | U-shape       | Width, Height                  |
        +---------------+--------------------------------+
        | Trapezoidal   | Top Width, Bottom Width, Height|
        +---------------+--------------------------------+

        Returns:
            Predicate: The created cross section predicate.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_x_section_predicate")
        cross_section = get_enum_value(cross_section, CrossSectionType)
        if min_value is not None:
            check_type(min_value, DoubleArray)
        if max_value is not None:
            check_type(max_value, DoubleArray)
        result = self.predicate_manager.CreateXSectionPredicate(
            cross_section,
            coerce_optional_dispatch(min_value, "double_array"),
            coerce_optional_dispatch(max_value, "double_array"),
        )

        if result is None:
            return None
        return Predicate(result)
