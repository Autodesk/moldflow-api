# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test errors.py
"""

import pytest
from moldflow.common import ValueErrorReason
from moldflow.errors import raise_value_error, raise_type_error, raise_index_error, raise_save_error
from moldflow.exceptions import SaveError
from tests.core.conftest import TEST_STRING
from tests.conftest import VALID_STR, pad_and_zip


@pytest.mark.core
class TestErrors:
    """
    Test suite for errors.
    """

    @pytest.mark.parametrize("variable, types", [(int, (str, list)), (int, str)])
    def test_raise_type_error(self, variable, types, _):
        """
        Test raise_type_error function.
        """
        with pytest.raises(TypeError) as e:
            raise_type_error(variable, types)
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize(
        "reason, kwargs",
        [
            (ValueErrorReason.INVALID_ENUM_VALUE, {"value": 10, "enum_name": "TestEnum"}),
            (ValueErrorReason.NOT_IN_RANGE, {"value": 10, "min_value": 0, "max_value": 5}),
        ],
    )
    def test_raise_value_error(self, reason, kwargs, _):
        """
        Test raise_value_error function.
        """
        with pytest.raises(ValueError) as e:
            raise_value_error(reason, **kwargs)
        assert _("Invalid") in str(e.value)

    def test_raise_value_error_custom_string(self, _):
        """
        Test raise_value_error function.
        """
        with pytest.raises(ValueError) as e:
            raise_value_error(TEST_STRING)
        assert _("Invalid") in str(e.value)

    def test_raise_index_error(self, _):
        """
        Test raise_index_error function.
        """
        with pytest.raises(IndexError) as e:
            raise_index_error()
        assert _("Invalid") in str(e.value)

    @pytest.mark.parametrize("saving, file_name", list(pad_and_zip(VALID_STR, VALID_STR)))
    def test_raise_save_error(self, saving, file_name, _):
        """
        Test raise_save_error function.
        """
        with pytest.raises(SaveError) as e:
            raise_save_error(saving, file_name)
        assert _("Save Error") in str(e.value)
