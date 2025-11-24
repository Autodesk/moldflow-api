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
from tests.api.integration_tests.data.set_fields import TEST_ENTITY_LIST_STRING


TEST_ENTITY_LIST_PARAMETERS = [
    ("select_from_string", "items"),
    ("select_from_predicate", "predicate"),
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
        self, synergy: Synergy, ent_list: EntList, study_file, select_function, parameter
    ):
        """
        Select entities from the entity list.
        """
        test_entity = TEST_ENTITY_LIST_STRING[study_file]
        if select_function == "select_from_string":
            getattr(ent_list, select_function)(test_entity[parameter])
        elif select_function == "select_from_predicate":
            pm = synergy.predicate_manager
            predicate = pm.create_label_predicate(test_entity[parameter])
            getattr(ent_list, select_function)(predicate)
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
        ids=["select_from_string", "select_from_predicate"],
    )
    def test_entity_list_size(
        self, synergy: Synergy, ent_list: EntList, study_file, select_function, parameter
    ):
        """
        Test the size property of EntList.
        """
        assert ent_list.size == 0
        test_entity = TEST_ENTITY_LIST_STRING[study_file]
        self._select_entities(synergy, ent_list, study_file, select_function, parameter)
        assert ent_list.size == test_entity["size"]

    @pytest.mark.parametrize(
        "select_function, parameter",
        TEST_ENTITY_LIST_PARAMETERS,
        ids=["select_from_string", "select_from_predicate"],
    )
    def test_entity_list_convert_to_string(
        self, synergy: Synergy, ent_list: EntList, study_file, select_function, parameter
    ):
        """
        Test the convert_to_string method of EntList.
        """
        test_entity = TEST_ENTITY_LIST_STRING[study_file]
        self._select_entities(synergy, ent_list, study_file, select_function, parameter)
        assert ent_list.convert_to_string() == test_entity["converted_string"]

    @pytest.mark.parametrize(
        "select_function, parameter",
        TEST_ENTITY_LIST_PARAMETERS,
        ids=["select_from_string", "select_from_predicate"],
    )
    def test_entity_list_entity(
        self, synergy: Synergy, ent_list: EntList, study_file, select_function, parameter
    ):
        """
        Test the entity method of EntList.
        """
        test_entity = TEST_ENTITY_LIST_STRING[study_file]
        self._select_entities(synergy, ent_list, study_file, select_function, parameter)
        for i in range(ent_list.size):
            assert ent_list.entity(i).convert_to_string() == test_entity["entity"][i]

    def test_entity_list_select_from_predicate_none(self, ent_list: EntList):
        """
        Test the select_from_predicate method of EntList with None.
        """
        ent_list.select_from_predicate(None)
        assert ent_list.size == 0
        assert ent_list.convert_to_string() == ""
