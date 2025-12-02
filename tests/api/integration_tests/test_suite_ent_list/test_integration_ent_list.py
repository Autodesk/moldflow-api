# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for EntList Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the EntList class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import EntList, Synergy
from tests.api.integration_tests.constants import FileSet


TEST_ENTITY_LIST_PARAMETERS = [
    ("select_from_string", "item_string"),
    ("select_from_predicate", "item_predicate"),
    ("select_from_saved_list", "saved_list_name"),
]


@pytest.mark.integration
@pytest.mark.ent_list
@pytest.mark.file_set(FileSet.MESHED)
class TestIntegrationEntList:
    """
    Integration test suite for the EntList class.
    """

    @pytest.fixture
    def ent_list(self, synergy: Synergy, study_with_project):
        """
        Fixture to create a real EntList instance for integration testing.
        """
        study_doc = synergy.study_doc
        return study_doc.create_entity_list()

    def _select_entities(
        self,
        synergy: Synergy,
        ent_list: EntList,
        study_file,
        select_function,
        parameter,
        values_to_select,
    ):
        """
        Select entities from the entity list.
        """
        if select_function == "select_from_string":
            getattr(ent_list, select_function)(values_to_select[parameter])
        elif select_function == "select_from_predicate":
            pm = synergy.predicate_manager
            predicate = pm.create_label_predicate(values_to_select[parameter])
            getattr(ent_list, select_function)(predicate)
        elif select_function == "select_from_saved_list":
            getattr(ent_list, select_function)(values_to_select[parameter])
        else:
            raise ValueError(f"Invalid select function: {select_function}")

    def test_entity_list(self, ent_list: EntList):
        """
        Test the entity list method of EntList.
        """
        assert ent_list.size == 0
        assert ent_list.convert_to_string() == ""

    @pytest.mark.parametrize(
        "select_function, parameter",
        TEST_ENTITY_LIST_PARAMETERS,
        ids=["select_from_string", "select_from_predicate", "select_from_saved_list"],
    )
    def test_entity_list_size(
        self,
        synergy: Synergy,
        ent_list: EntList,
        study_file,
        select_function,
        parameter,
        expected_values,
    ):
        """
        Test the size property of EntList.
        """
        assert ent_list.size == 0
        self._select_entities(
            synergy, ent_list, study_file, select_function, parameter, expected_values
        )
        assert ent_list.size == expected_values["size"]

    @pytest.mark.parametrize(
        "select_function, parameter",
        TEST_ENTITY_LIST_PARAMETERS,
        ids=["select_from_string", "select_from_predicate", "select_from_saved_list"],
    )
    def test_entity_list_convert_to_string(
        self,
        synergy: Synergy,
        ent_list: EntList,
        study_file,
        select_function,
        parameter,
        expected_values,
    ):
        """
        Test the convert_to_string method of EntList.
        """
        self._select_entities(
            synergy, ent_list, study_file, select_function, parameter, expected_values
        )
        assert ent_list.convert_to_string() == expected_values["converted_string"]

    @pytest.mark.parametrize(
        "select_function, parameter",
        TEST_ENTITY_LIST_PARAMETERS,
        ids=["select_from_string", "select_from_predicate", "select_from_saved_list"],
    )
    def test_entity_list_entity(
        self,
        synergy: Synergy,
        ent_list: EntList,
        study_file,
        select_function,
        parameter,
        expected_values,
    ):
        """
        Test the entity method of EntList.
        """
        self._select_entities(
            synergy, ent_list, study_file, select_function, parameter, expected_values
        )
        for i in range(ent_list.size):
            assert ent_list.entity(i).convert_to_string() == expected_values["entity"][str(i)]

    def test_entity_list_select_from_predicate_none(self, ent_list: EntList):
        """
        Test the select_from_saved_list method of EntList.
        """
        ent_list.select_from_predicate(None)
        assert ent_list.size == 0
        assert ent_list.convert_to_string() == ""
