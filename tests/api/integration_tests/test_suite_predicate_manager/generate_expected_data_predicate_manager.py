# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for the PredicateManager class.
Returns a dict with relevant properties.
"""

from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json
from tests.api.integration_tests.constants import FileSet
from tests.api.integration_tests.test_suite_predicate_manager.constants import (
    PREDICATE_DATA,
    PROPERTY_PREDICATE_TEST_DATA,
    PROPERTY_TYPE_PREDICATE_TEST_DATA,
    THICKNESS_PREDICATE_TEST_DATA,
    X_SECTION_PREDICATE_TEST_DATA,
)


def _entity_to_dict(entity):
    """Convert an EntityData into a JSON-safe dict used by the integration tests."""
    data = {
        "entity_type": entity.entity_type,
        "start_index": entity.start_index,
        "end_index": entity.end_index,
        "label": entity.label,
        "size": entity.size,
        "converted_string": entity.converted_string,
    }

    if entity.split:
        data["triple_split"] = [_entity_to_dict(s) for s in entity.triple_split]

    return data


def _index_range(entity_dict):
    return range(entity_dict["start_index"], entity_dict["end_index"] + 1)


def _converted_string(entity_type, indices):
    return "".join(f"{entity_type}{i} " for i in sorted(indices))


def _build_boolean_predicate_data(final):
    """
    Build expected results for boolean predicates (AND, OR, NOT, XOR).
    Tests consume exactly this structure.
    """
    first_entity = final["entities"][0]
    entity_type = first_entity["entity_type"]

    s1_dict, s2_dict, s3_dict = first_entity["triple_split"]
    s1 = set(_index_range(s1_dict))
    s2 = set(_index_range(s2_dict))
    s3 = set(_index_range(s3_dict))

    out = {}

    out["and"] = {
        "common_case": {
            "size": len(s1 & s2),
            "converted_string": _converted_string(entity_type, s1 & s2),
        },
        "no_common_case": {
            "size": len(s1 & s3),
            "converted_string": _converted_string(entity_type, s1 & s3),
        },
    }

    out["or"] = {
        "first_second": {
            "size": len(s1 | s2),
            "converted_string": _converted_string(entity_type, s1 | s2),
        },
        "all_splits": {
            "size": first_entity["size"],
            "converted_string": first_entity["converted_string"],
        },
    }

    others = final["entities"][1:]
    others_size = sum(e["size"] for e in others)
    others_string = "".join(e["converted_string"] for e in others)

    full_first = set(_index_range(first_entity))

    out["not"] = {}
    for name, split_set in zip(["first_split", "second_split", "third_split"], [s1, s2, s3]):
        not_indices = full_first - split_set
        out["not"][name] = {
            "size": len(not_indices) + others_size,
            "converted_string": _converted_string(entity_type, not_indices) + others_string,
        }

    out["xor"] = {
        "first_second": {
            "size": len(s1 ^ s2),
            "converted_string": _converted_string(entity_type, s1 ^ s2),
        },
        "first_third": {
            "size": len(s1 ^ s3),
            "converted_string": _converted_string(entity_type, s1 ^ s3),
        },
    }

    final["boolean_predicate_expected_data"] = out


@generate_json(file_set=FileSet.MESHED)
def generate_predicate_manager_data(synergy: Synergy = None, *args, **kwargs):
    """
    Build and return JSON test data for PredicateManager integration tests.
    Only includes fields actually consumed by the tests.
    """
    study_file = kwargs["study_file"]

    final = {"entities": [_entity_to_dict(e) for e in PREDICATE_DATA[study_file]]}

    _build_boolean_predicate_data(final)

    final["property_predicate_expected_data"] = PROPERTY_PREDICATE_TEST_DATA[study_file]
    final["property_type_predicate_expected_data"] = PROPERTY_TYPE_PREDICATE_TEST_DATA[study_file]
    final["thickness_predicate_expected_data"] = THICKNESS_PREDICATE_TEST_DATA[study_file]
    final["x_section_predicate_expected_data"] = X_SECTION_PREDICATE_TEST_DATA[study_file]

    return final


if __name__ == "__main__":
    generate_predicate_manager_data()
