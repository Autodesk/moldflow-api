# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Helper functions for testing Moldflow Synergy API classes.
"""


def data_dict(data_class):
    """
    Data dictionary for testing setting options for Moldflow Synergy API classes.
    """
    result_dict = {}
    for data_value in data_class:
        result_dict[data_value] = data_value
    return result_dict


def enum_dict(enum_class):
    """
    Enum dictionary for testing setting options for Moldflow Synergy API classes.
    """
    result_dict = {}
    for enum_value in enum_class:
        result_dict[enum_value] = enum_value.value
        result_dict[enum_value.value] = enum_value.value
    return result_dict
