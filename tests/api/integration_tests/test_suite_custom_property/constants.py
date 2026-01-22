# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Constants for the Custom Property test suite.
"""

CUSTOM_PROPERTY_DEFAULTS = False
CUSTOM_PROPERTY_NAME = "Test Name"
CUSTOM_PROPERTY_ID = 1
CUSTOM_PROPERTY_TYPE = 10

FIELD_PROPERTIES = {
    1: {
        "id": 20,
        "description": "Test Description",
        "values": [1, 2, 3],
        "units": [],
        "writable": True,
        "hidden": False,
    },
    2: {
        "id": 21,
        "description": "Second Test Description",
        "values": [4, 5, 6],
        "units": [],
        "writable": True,
        "hidden": False,
    },
}

FIELD_INDEX = 1  # Index for the field to be used for single field tests
