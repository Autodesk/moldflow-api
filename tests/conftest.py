"""This module contains the common test fixtures for the moldflow-api tests."""

import os
import logging
from enum import Enum
from unittest.mock import Mock
import pytest
from moldflow.localization import set_language
from moldflow.logger import set_is_logging
from moldflow.constants import DEFAULT_THREE_LETTER_CODE

# Logging
LOGGING = True

# Test Version
TEST_VERSION_DEFAULT = "2026"
TEST_VERSION = os.getenv("TEST_VERSION", TEST_VERSION_DEFAULT)

# Valid and Invalid Values
VALID_BOOL = [True, False]
INVALID_BOOL = [None, 1, "True", 1.1]

VALID_INT = [-1, 0, 1]
INVALID_INT = [None, 1.1, "1", True]

VALID_FLOAT = [-1.1, 1.1, 1, 0]
INVALID_FLOAT = [None, "1", True]

VALID_STR = ["Test", "Test1"]
INVALID_STR = [None, 1, 1.1, True]

# Integer Values
NEGATIVE_INT = [-1, -2, -3]
NON_POSITIVE_INT = NEGATIVE_INT + [0]
POSITIVE_INT = [1, 2, 3]
NON_NEGATIVE_INT = POSITIVE_INT + [0]

# Float Values
NEGATIVE_FLOAT = [-1.0, -2.0, -3.0]
NON_POSITIVE_FLOAT = NEGATIVE_FLOAT + [0.0]
POSITIVE_FLOAT = [1.0, 2.0, 3.0]
NON_NEGATIVE_FLOAT = POSITIVE_FLOAT + [0.0]


# Helper Functions
def pad_and_zip(*lists):
    """
    Pad the shorter lists with the last element of each list and zip them together.
    This helps the test all list inputs by making sure inputs are same length
    """
    processed = []
    for lst in lists:
        if isinstance(lst, type) and issubclass(lst, Enum):
            lst = list(lst)
        if isinstance(lst, Mock):
            lst = [lst]
        processed.append(lst)
    if len(processed) == 1:
        return processed[0]
    max_len = max(len(lst) for lst in processed)
    padded = []
    for lst in processed:
        # Append a short list to the legnth of the longest list by adding the last element
        if len(lst) < max_len:
            pad_value = lst[-1] if lst else None
            lst = lst + [pad_value] * (max_len - len(lst))
        padded.append(lst)

    return [list(col) for col in zip(*padded)]


def list_intersection(list1, list2):
    """
    Return the intersection of two lists.
    """
    return list(set(list1) & set(list2))


# Fixtures
@pytest.fixture(scope="session")
def _():
    """
    A pytest fixture that provides a mock object for the gettext translation function.
    """
    return set_language(version=TEST_VERSION, locale=DEFAULT_THREE_LETTER_CODE)


@pytest.fixture(autouse=True)
def set_logging():
    """
    Set the logging level.
    """
    logging.getLogger().setLevel(logging.DEBUG)
    set_is_logging(LOGGING)
