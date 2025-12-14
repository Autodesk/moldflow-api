# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for PredicateManager Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the PredicateManager class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import PredicateManager, Synergy, Predicate, EntList, CrossSectionType, DoubleArray
from tests.api.integration_tests.test_suite_predicate_manager.constants import (
    TEST_PROPERTY_TYPE,
    TEST_PROPERTY_ID,
    TEST_MIN_THICKNESS,
    TEST_MAX_THICKNESS,
    X_SECTION_PREDICATE_TEST_DATA_LIST,
)
from tests.api.integration_tests.constants import FileSet


@pytest.mark.integration
@pytest.mark.predicate_manager
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationPredicateManager:
    """
    Integration-level tests for the PredicateManager wrapper.
    """

    @pytest.fixture
    def predicate_manager(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real PredicateManager instance for integration testing.
        """
        return synergy.predicate_manager

    @pytest.fixture
    def ent_list(self, synergy: Synergy):
        """
        Fixture to create a real EntList instance for integration testing.
        """
        study_doc = synergy.study_doc
        return study_doc.create_entity_list()

    def _create_label_predicate(
        self, predicate_manager: PredicateManager, values: dict, index: int
    ) -> tuple[Predicate, int, str]:
        """
        Create a label predicate from the values.
        """
        entity = values["entities"][0]
        if "triple_split" not in entity:
            return None, None, None
        entry = entity["triple_split"][index]
        predicate = predicate_manager.create_label_predicate(entry["label"])
        return predicate, entry["size"], entry["converted_string"]

    @pytest.fixture
    def _mk_predicate(self, predicate_manager: PredicateManager, expected_values):
        """Factory fixture: returns a function that creates predicates by index."""

        def make(index: int):
            return self._create_label_predicate(predicate_manager, expected_values, index)[0]

        return make

    @pytest.fixture
    def predicate1(self, _mk_predicate):
        """
        Fixture to create a predicate1 instance for integration testing.
        """
        return _mk_predicate(0)

    @pytest.fixture
    def predicate2(self, _mk_predicate):
        """
        Fixture to create a predicate2 instance for integration testing.
        """
        return _mk_predicate(1)

    @pytest.fixture
    def predicate3(self, _mk_predicate):
        """
        Fixture to create a predicate3 instance for integration testing.
        """
        return _mk_predicate(2)

    def _compare_predicate_results(
        self,
        ent_list: EntList,
        predicate: Predicate,
        expected_size: int,
        expected_string: str | None = None,
    ):
        """
        Compare the predicate results with the expected size and string.
        """
        assert isinstance(predicate, Predicate)
        ent_list.select_from_predicate(predicate)
        assert ent_list.size == expected_size

        if expected_string:
            assert ent_list.convert_to_string() == expected_string

    @pytest.mark.parametrize("split_index", [0, 1, 2])
    def test_create_label_predicate(
        self,
        predicate_manager: PredicateManager,
        ent_list: EntList,
        expected_values,
        split_index: int,
    ):
        """
        Test the create_label_predicate method of PredicateManager.
        """
        predicate, expected_size, expected_string = self._create_label_predicate(
            predicate_manager, expected_values, split_index
        )
        self._compare_predicate_results(ent_list, predicate, expected_size, expected_string)

    def test_create_label_predicate_empty_string(self, predicate_manager: PredicateManager):
        """
        Test the create_label_predicate method of PredicateManager with an empty string.
        """
        assert predicate_manager.create_label_predicate("") is None

    def test_create_label_predicate_invalid_label(
        self, predicate_manager: PredicateManager, ent_list: EntList
    ):
        """
        Test the create_label_predicate method of PredicateManager with an invalid label.
        """
        assert predicate_manager.create_label_predicate("INVALID99999:99999") is None

    def test_create_property_predicate(
        self, predicate_manager: PredicateManager, ent_list: EntList, expected_values
    ):
        """
        Test the create_property_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_property_predicate(
            TEST_PROPERTY_TYPE, TEST_PROPERTY_ID
        )
        expected = expected_values["property_predicate_expected_data"]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    def test_create_prop_type_predicate(
        self, predicate_manager: PredicateManager, ent_list: EntList, expected_values
    ):
        """
        Test the create_prop_type_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_prop_type_predicate(TEST_PROPERTY_TYPE)
        expected = expected_values["property_type_predicate_expected_data"]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    def test_create_thickness_predicate(
        self, predicate_manager: PredicateManager, ent_list: EntList, expected_values
    ):
        """
        Test the create_thickness_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_thickness_predicate(
            TEST_MIN_THICKNESS, TEST_MAX_THICKNESS
        )
        expected = expected_values["thickness_predicate_expected_data"]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    def _new_double_array(self, synergy: Synergy, values: list[float]) -> DoubleArray:
        """
        Create a new double array.
        """
        arr = synergy.create_double_array()
        for v in values:
            arr.add_double(v)
        return arr

    @pytest.mark.parametrize(
        "cross_section_type, min_values, max_values",
        X_SECTION_PREDICATE_TEST_DATA_LIST,
        ids=[case[0].value for case in X_SECTION_PREDICATE_TEST_DATA_LIST],
    )
    def test_create_x_section_predicate(
        self,
        synergy: Synergy,
        predicate_manager: PredicateManager,
        ent_list: EntList,
        expected_values,
        cross_section_type: CrossSectionType,
        min_values: list[float],
        max_values: list[float],
    ):
        """
        Test the create_x_section_predicate method of PredicateManager.
        """
        min_array = self._new_double_array(synergy, min_values)
        max_array = self._new_double_array(synergy, max_values)

        predicate = predicate_manager.create_x_section_predicate(
            cross_section_type, min_array, max_array
        )

        expected = expected_values["x_section_predicate_expected_data"][cross_section_type.value]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    @pytest.fixture
    def first_predicate(self, request):
        """
        Fixture to create a first predicate instance for integration testing (selected by index).
        """
        return request.getfixturevalue(request.param)

    @pytest.fixture
    def second_predicate(self, request):
        """
        Fixture to create a second predicate instance for integration testing (selected by index).
        """
        return request.getfixturevalue(request.param)

    @pytest.fixture
    def single_predicate(self, request):
        """
        Fixture to create a single predicate instance for integration testing (selected by index).
        """
        return request.getfixturevalue(request.param)

    @pytest.mark.parametrize(
        "data_entry_name, first_predicate, second_predicate",
        [
            ("common_case", "predicate1", "predicate2"),
            ("no_common_case", "predicate1", "predicate3"),
        ],
        indirect=["first_predicate", "second_predicate"],
        ids=["common_case", "no_common_case"],
    )
    def test_create_bool_and_predicate(
        self,
        predicate_manager: PredicateManager,
        ent_list: EntList,
        expected_values,
        data_entry_name: str,
        first_predicate: Predicate,
        second_predicate: Predicate,
    ):
        """
        Test the create_bool_and_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_bool_and_predicate(first_predicate, second_predicate)
        expected = expected_values["boolean_predicate_expected_data"]["and"][data_entry_name]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    def test_create_bool_or_predicate_first_second(
        self,
        predicate_manager: PredicateManager,
        predicate1: Predicate,
        predicate2: Predicate,
        ent_list: EntList,
        expected_values,
    ):
        """
        Test the create_bool_or_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_bool_or_predicate(predicate1, predicate2)
        expected = expected_values["boolean_predicate_expected_data"]["or"]["first_second"]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    def test_create_bool_or_predicate_all_splits(
        self,
        predicate_manager: PredicateManager,
        predicate1: Predicate,
        predicate2: Predicate,
        predicate3: Predicate,
        ent_list: EntList,
        expected_values,
    ):
        """
        Test the create_bool_or_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_bool_or_predicate(predicate1, predicate2)
        predicate = predicate_manager.create_bool_or_predicate(predicate, predicate3)
        expected = expected_values["boolean_predicate_expected_data"]["or"]["all_splits"]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    @pytest.mark.parametrize(
        "data_entry_name, single_predicate",
        [
            ("first_split", "predicate1"),
            ("second_split", "predicate2"),
            ("third_split", "predicate3"),
        ],
        indirect=["single_predicate"],
        ids=["first_split", "second_split", "third_split"],
    )
    def test_create_bool_not_predicate(
        self,
        predicate_manager: PredicateManager,
        ent_list: EntList,
        expected_values,
        data_entry_name: str,
        single_predicate: Predicate,
    ):
        """
        Test the create_bool_not_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_bool_not_predicate(single_predicate)
        expected = expected_values["boolean_predicate_expected_data"]["not"][data_entry_name]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )

    @pytest.mark.parametrize(
        "data_entry_name, first_predicate, second_predicate",
        [("first_second", "predicate1", "predicate2"), ("first_third", "predicate1", "predicate3")],
        indirect=["first_predicate", "second_predicate"],
        ids=["first_second", "first_third"],
    )
    def test_create_bool_xor_predicate(
        self,
        predicate_manager: PredicateManager,
        ent_list: EntList,
        expected_values,
        data_entry_name: str,
        first_predicate: Predicate,
        second_predicate: Predicate,
    ):
        """
        Test the create_bool_xor_predicate method of PredicateManager.
        """
        predicate = predicate_manager.create_bool_xor_predicate(first_predicate, second_predicate)
        expected = expected_values["boolean_predicate_expected_data"]["xor"][data_entry_name]
        self._compare_predicate_results(
            ent_list, predicate, expected["size"], expected["converted_string"]
        )
