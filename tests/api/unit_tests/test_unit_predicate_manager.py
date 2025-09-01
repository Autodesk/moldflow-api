# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for PredicateManager Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import PredicateManager, Predicate, CrossSectionType, DoubleArray
from tests.api.unit_tests.conftest import VALID_MOCK


@pytest.mark.unit
class TestUnitPredicateManager:
    """
    Test suite for the PredicateManager class.
    """

    @pytest.fixture
    def mock_predicate_manager(self, mock_object) -> PredicateManager:
        """
        Fixture to create a mock instance of PredicateManager.
        Args:
            mock_object: Mock object for the PredicateManager dependency.
        Returns:
            PredicateManager: An instance of PredicateManager with the mock object.
        """
        return PredicateManager(mock_object)

    @pytest.mark.parametrize("label", ["N1:N2", "N1:N20", "L1:L20"])
    def test_create_label_predicate(self, mock_predicate_manager, label):
        """
        Test the create_label_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
            mock_object: Mock instance of Predicate.
        """
        result = mock_predicate_manager.create_label_predicate(label)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateLabelPredicate.assert_called_once_with(label)

    @pytest.mark.parametrize("property_type, property_id", [(1, 1), (2, 2), (3, 3)])
    def test_create_property_predicate(self, mock_predicate_manager, property_type, property_id):
        """
        Test the create_property_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
            mock_object: Mock instance of Predicate.
        """
        result = mock_predicate_manager.create_property_predicate(property_type, property_id)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreatePropertyPredicate.assert_called_once_with(
            property_type, property_id
        )

    @pytest.mark.parametrize("prop_type", [1, 2, 3])
    def test_create_prop_type_predicate(self, mock_predicate_manager, prop_type):
        """
        Test the create_prop_type_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
            mock_object: Mock instance of Predicate.
        """
        result = mock_predicate_manager.create_prop_type_predicate(prop_type)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreatePropTypePredicate.assert_called_once_with(
            prop_type
        )

    @pytest.mark.parametrize("min_value, max_value", [(1.0, 2.0), (2.0, 3.0), (3.0, 4.0)])
    def test_create_thickness_predicate(self, mock_predicate_manager, min_value, max_value):
        """
        Test the create_thickness_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
            mock_object: Mock instance of Predicate.
        """
        result = mock_predicate_manager.create_thickness_predicate(min_value, max_value)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateThicknessPredicate.assert_called_once_with(
            min_value, max_value
        )

    def test_create_bool_and_predicate(self, mock_predicate_manager):
        """
        Test the bool_and_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
        """
        predicate_obj_1 = Mock()
        predicate_obj_2 = Mock()
        predicate_obj_1.predicate = Mock()
        predicate_obj_2.predicate = Mock()
        predicate1 = Predicate(predicate_obj_1)
        predicate2 = Predicate(predicate_obj_2)
        result = mock_predicate_manager.create_bool_and_predicate(predicate1, predicate2)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateBoolAndPredicate.assert_called_once_with(
            predicate1.predicate, predicate2.predicate
        )

    def test_create_bool_or_predicate(self, mock_predicate_manager):
        """
        Test the bool_or_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
        """
        predicate_obj_1 = Mock()
        predicate_obj_2 = Mock()
        predicate_obj_1.predicate = Mock()
        predicate_obj_2.predicate = Mock()
        predicate1 = Predicate(predicate_obj_1)
        predicate2 = Predicate(predicate_obj_2)
        result = mock_predicate_manager.create_bool_or_predicate(predicate1, predicate2)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateBoolOrPredicate.assert_called_once_with(
            predicate1.predicate, predicate2.predicate
        )

    def test_create_bool_not_predicate(self, mock_predicate_manager):
        """
        Test the bool_not_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
        """
        predicate_obj = Mock()
        predicate_obj.predicate = Mock()
        predicate = Predicate(predicate_obj)
        result = mock_predicate_manager.create_bool_not_predicate(predicate)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateBoolNotPredicate.assert_called_once_with(
            predicate.predicate
        )

    def test_create_bool_xor_predicate(self, mock_predicate_manager):
        """
        Test the bool_xor_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
        """
        predicate_obj_1 = Mock()
        predicate_obj_2 = Mock()
        predicate_obj_1.predicate = Mock()
        predicate_obj_2.predicate = Mock()
        predicate1 = Predicate(predicate_obj_1)
        predicate2 = Predicate(predicate_obj_2)
        result = mock_predicate_manager.create_bool_xor_predicate(predicate1, predicate2)
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateBoolXorPredicate.assert_called_once_with(
            predicate1.predicate, predicate2.predicate
        )

    @pytest.mark.parametrize(
        "cross_section, cross_section_value",
        [(cross_section, cross_section.value) for cross_section in CrossSectionType]
        + [(cross_section.value, cross_section.value) for cross_section in CrossSectionType],
    )
    def test_create_x_section_predicate(
        self, mock_predicate_manager, cross_section, cross_section_value
    ):
        """
        Test the create_x_section_predicate method of PredicateManager class.
        Args:
            mock_predicate_manager: Mock instance of PredicateManager.
            cross_section: CrossSectionType enum value or str.

        Note:
            The required number of elements in min_value and max_value differ by cross-section.
            Refer PredicateManager::create_x_section_predicate() for more details.
        """
        min_value = Mock(spec=DoubleArray)
        min_value.double_array = Mock()
        max_value = Mock(spec=DoubleArray)
        max_value.double_array = Mock()
        result = mock_predicate_manager.create_x_section_predicate(
            cross_section, min_value, max_value
        )
        assert isinstance(result, Predicate)
        mock_predicate_manager.predicate_manager.CreateXSectionPredicate.assert_called_once_with(
            cross_section_value, min_value.double_array, max_value.double_array
        )

    @pytest.mark.parametrize(
        "pascal_name, property_name, args",
        [
            ("CreateLabelPredicate", "create_label_predicate", ("N1:N2",)),
            ("CreatePropertyPredicate", "create_property_predicate", (1, 1)),
            ("CreatePropTypePredicate", "create_prop_type_predicate", (1,)),
            ("CreateThicknessPredicate", "create_thickness_predicate", (1.0, 2.0)),
            (
                "CreateBoolAndPredicate",
                "create_bool_and_predicate",
                (VALID_MOCK.PREDICATE, VALID_MOCK.PREDICATE),
            ),
            (
                "CreateBoolOrPredicate",
                "create_bool_or_predicate",
                (VALID_MOCK.PREDICATE, VALID_MOCK.PREDICATE),
            ),
            ("CreateBoolNotPredicate", "create_bool_not_predicate", (VALID_MOCK.PREDICATE,)),
            (
                "CreateBoolXorPredicate",
                "create_bool_xor_predicate",
                (VALID_MOCK.PREDICATE, VALID_MOCK.PREDICATE),
            ),
        ]
        + [
            (
                "CreateXSectionPredicate",
                "create_x_section_predicate",
                (x, VALID_MOCK.DOUBLE_ARRAY, VALID_MOCK.DOUBLE_ARRAY),
            )
            for x in CrossSectionType
        ],
    )
    # pylint: disable=R0913, R0917
    def test_function_return_none(
        self,
        mock_predicate_manager: PredicateManager,
        mock_object,
        pascal_name,
        property_name,
        args,
    ):
        """
        Test the return value of the function is None.
        """
        getattr(mock_object, pascal_name).return_value = None
        result = getattr(mock_predicate_manager, property_name)(*args)
        assert result is None
