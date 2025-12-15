# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for PropertyEditor Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import EntList, Property, Synergy, PropertyEditor, PropertyType, CommitActions
from tests.api.integration_tests.test_suite_property_editor.constants import (
    TEST_PROPERTY_TYPE,
    TEST_MAX_PROPERTY_COUNT,
    TEST_PROPERTY_DEFAULTS,
    ENTITY_TO_SET,
    PROPERTY_TO_SET_TYPE,
    PROPERTY_TO_SET_ID,
)
from tests.api.integration_tests.constants import FileSet


@pytest.mark.integration
@pytest.mark.property_editor
@pytest.mark.file_set(FileSet.SINGLE)
class TestIntegrationPropertyEditor:
    """PropertyEditor integration test class for moldflow-api"""

    @pytest.fixture
    def property_editor(self, synergy: Synergy, study_with_project) -> PropertyEditor:
        """
        Fixture to create a PropertyEditor instance.
        """
        return synergy.property_editor

    @pytest.fixture
    def custom_property_editor(self, property_editor: PropertyEditor):
        """
        Fixture to create test properties.
        """
        for i in range(1, TEST_MAX_PROPERTY_COUNT + 1):
            property_editor.create_property(TEST_PROPERTY_TYPE, i, TEST_PROPERTY_DEFAULTS)
        yield property_editor
        for i in range(1, TEST_MAX_PROPERTY_COUNT + 1):
            found_property = property_editor.find_property(TEST_PROPERTY_TYPE, i)
            if found_property is not None:
                property_editor.delete_property(TEST_PROPERTY_TYPE, i)

    def test_property_editor(self, synergy: Synergy, study_with_project):
        """
        Test accessing PropertyEditor from Synergy.
        This test verifies that PropertyEditor can be accessed from Synergy instance.
        """
        property_editor = synergy.property_editor
        assert isinstance(property_editor, PropertyEditor)
        assert property_editor is not None
        assert property_editor.property_editor is not None

    def test_create_entity_list(self, property_editor: PropertyEditor):
        """
        Test creating an entity list.
        This test verifies that create_entity_list returns an EntList instance.
        """
        entity_list = property_editor.create_entity_list()
        assert isinstance(entity_list, EntList)
        assert entity_list is not None
        assert entity_list.ent_list is not None

    def test_create_property(self, property_editor: PropertyEditor):
        """
        Test creating a property.
        """
        new_property = property_editor.create_property(
            TEST_PROPERTY_TYPE, 1, TEST_PROPERTY_DEFAULTS
        )
        assert isinstance(new_property, Property)
        assert new_property is not None
        assert new_property.prop is not None
        found_property = property_editor.find_property(TEST_PROPERTY_TYPE, 1)
        assert found_property.type == new_property.type
        assert found_property.id == new_property.id

    def test_delete_property(self, custom_property_editor: PropertyEditor):
        """
        Test deleting a property.
        """
        for i in range(1, TEST_MAX_PROPERTY_COUNT + 1):
            property_deleted = custom_property_editor.delete_property(TEST_PROPERTY_TYPE, i)
            assert property_deleted is True
            found_deleted_property = custom_property_editor.find_property(TEST_PROPERTY_TYPE, i)
            assert found_deleted_property is None

    def test_find_property(self, custom_property_editor: PropertyEditor):
        """
        Test finding a property.
        """
        for i in range(1, TEST_MAX_PROPERTY_COUNT + 1):
            found_property = custom_property_editor.find_property(TEST_PROPERTY_TYPE, i)
            assert found_property is not None
            assert found_property.prop is not None
            assert found_property.type == TEST_PROPERTY_TYPE
            assert found_property.id == i

    def test_get_first_property(self, custom_property_editor: PropertyEditor, expected_values):
        """
        Test getting the first property.
        """
        first_property = custom_property_editor.get_first_property(TEST_PROPERTY_TYPE)
        assert first_property.type == expected_values["first_property_type"]
        assert first_property.id == expected_values["first_property_id"]

    def test_get_next_property_get_data_description(
        self, custom_property_editor: PropertyEditor, expected_values
    ):
        """
        Test getting the next property and data description.
        """
        prop_iter = custom_property_editor.get_first_property(TEST_PROPERTY_TYPE)
        res = {}
        while prop_iter is not None:
            # assert prop_iter.type == TEST_PROPERTY_TYPE
            if str(prop_iter.type) not in res:
                res[str(prop_iter.type)] = {}
            desc = custom_property_editor.get_data_description(prop_iter.type, prop_iter.id)
            res[str(prop_iter.type)][str(prop_iter.id)] = desc
            prop_iter = custom_property_editor.get_next_property(prop_iter)
        assert res == expected_values["property_dict"]

    def test_get_next_property_of_type(
        self, custom_property_editor: PropertyEditor, expected_values
    ):
        """
        Test getting the next property.
        """
        prop_iter = custom_property_editor.get_first_property(TEST_PROPERTY_TYPE)
        res = []
        while prop_iter is not None:
            assert prop_iter.type == TEST_PROPERTY_TYPE
            res.append(str(prop_iter.id))
            prop_iter = custom_property_editor.get_next_property_of_type(prop_iter)
        assert res == list(expected_values["property_dict"][str(TEST_PROPERTY_TYPE)].keys())

    def test_get_entity_property(self, custom_property_editor: PropertyEditor, expected_values):
        """
        Test getting the entity property.
        """
        entity_list = custom_property_editor.create_entity_list()
        entity_list.select_from_string(ENTITY_TO_SET)
        prop = custom_property_editor.get_entity_property(entity_list)
        assert prop.type == expected_values["original_entity_property"]["property_type"]
        assert prop.id == expected_values["original_entity_property"]["property_id"]

    def test_set_property(self, custom_property_editor: PropertyEditor, expected_values):
        """
        Test setting the property.
        """
        entity_list = custom_property_editor.create_entity_list()
        entity_list.select_from_string(ENTITY_TO_SET)
        original_prop = custom_property_editor.get_entity_property(entity_list)
        prop_to_set = custom_property_editor.find_property(PROPERTY_TO_SET_TYPE, PROPERTY_TO_SET_ID)
        custom_property_editor.set_property(entity_list, prop_to_set)
        # Check that the property is not set before committing
        prop_set = custom_property_editor.get_entity_property(entity_list)
        assert prop_set.type == original_prop.type
        assert prop_set.id == original_prop.id
        # Commit the changes
        custom_property_editor.commit_changes(CommitActions.ASSIGN)
        prop_set = custom_property_editor.get_entity_property(entity_list)
        assert prop_set.type == expected_values["property_to_set"]["property_type"]
        assert prop_set.id == expected_values["property_to_set"]["property_id"]
        assert prop_set.type != original_prop.type
        assert prop_set.id != original_prop.id

    def test_remove_unused_properties(self, property_editor: PropertyEditor, expected_values):
        """
        Test removing unused properties.
        """
        no_of_unused_properties = property_editor.remove_unused_properties()
        assert no_of_unused_properties == expected_values["no_of_removed_properties"]

    def test_fetch_property(self, custom_property_editor: PropertyEditor, expected_values):
        """
        Test fetching a property.
        """
        prop = custom_property_editor.fetch_property(TEST_PROPERTY_TYPE, 1, "", "", 0)
