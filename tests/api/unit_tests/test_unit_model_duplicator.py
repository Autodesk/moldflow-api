# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for ModelDuplicator Wrapper Class of moldflow-api module.
"""

import pytest
from moldflow import ModelDuplicator


@pytest.mark.unit
class TestUnitModelDuplicator:
    """
    Test suite for the ModelDuplicator class.
    """

    @pytest.fixture
    def mock_model_duplicator(self, mock_object) -> ModelDuplicator:
        """
        Fixture to create a mock instance of ModelDuplicator.
        Args:
            mock_object: Mock object for the ModelDuplicator dependency.
        Returns:
            ModelDuplicator: An instance of ModelDuplicator with the mock object.
        """
        return ModelDuplicator(mock_object)

    @pytest.mark.parametrize("generate", [True, False])
    def test_generate(self, mock_model_duplicator: ModelDuplicator, mock_object, generate):
        """
        Test the generate method of ModelDuplicator.
        Args:
            mock_model_duplicator: Mock instance of ModelDuplicator.
        """
        mock_object.Generate = generate
        result = mock_model_duplicator.generate()
        assert isinstance(result, bool)
        assert result == generate

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("NumCavities", "num_cavities", 1),
            ("NumCavities", "num_cavities", 2),
            ("ByColumns", "by_columns", True),
            ("ByColumns", "by_columns", False),
            ("NumCols", "num_cols", 1),
            ("NumCols", "num_cols", 2),
            ("NumRows", "num_rows", 1),
            ("NumRows", "num_rows", 2),
            ("XSpacing", "x_spacing", 0.1),
            ("XSpacing", "x_spacing", 1.0),
            ("YSpacing", "y_spacing", 0.1),
            ("YSpacing", "y_spacing", 1.0),
            ("AlignGates", "align_gates", True),
            ("AlignGates", "align_gates", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_get_properties(
        self, mock_model_duplicator: ModelDuplicator, mock_object, pascal_name, property_name, value
    ):
        """
        Test Get properties of ModelDuplicator.

        Args:
            mock_model_duplicator: Instance of ModelDuplicator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_object, pascal_name, value)
        result = getattr(mock_model_duplicator, property_name)
        assert isinstance(result, type(value))
        assert result == value

    @pytest.mark.parametrize(
        "pascal_name, property_name, value",
        [
            ("NumCavities", "num_cavities", 1),
            ("NumCavities", "num_cavities", 2),
            ("ByColumns", "by_columns", True),
            ("ByColumns", "by_columns", False),
            ("NumCols", "num_cols", 1),
            ("NumCols", "num_cols", 2),
            ("NumRows", "num_rows", 1),
            ("NumRows", "num_rows", 2),
            ("XSpacing", "x_spacing", 0.1),
            ("XSpacing", "x_spacing", 1.0),
            ("YSpacing", "y_spacing", 0.1),
            ("YSpacing", "y_spacing", 1.0),
            ("AlignGates", "align_gates", True),
            ("AlignGates", "align_gates", False),
        ],
    )
    # pylint: disable-next=R0913, R0917
    def test_set_properties(
        self, mock_model_duplicator: ModelDuplicator, mock_object, property_name, pascal_name, value
    ):
        """
        Test properties of ModelDuplicator.

        Args:
            mock_model_duplicator: Instance of ModelDuplicator.
            property_name: Name of the property to test.
            pascal_name: Pascal case name of the property.
            value: Value to set and check.
        """
        setattr(mock_model_duplicator, property_name, value)
        new_val = getattr(mock_object, pascal_name)
        assert new_val == value

    @pytest.mark.parametrize(
        "property_name, value",
        [
            ("num_cavities", "1"),
            ("num_cavities", True),
            ("num_cavities", None),
            ("by_columns", "1"),
            ("by_columns", 1),
            ("by_columns", None),
            ("num_cols", "1"),
            ("num_cols", True),
            ("num_cols", None),
            ("num_rows", "1"),
            ("num_rows", True),
            ("num_rows", None),
            ("x_spacing", "1"),
            ("x_spacing", True),
            ("x_spacing", None),
            ("y_spacing", "1"),
            ("y_spacing", True),
            ("y_spacing", None),
            ("align_gates", "1"),
            ("align_gates", 1),
            ("align_gates", None),
        ],
    )
    def test_invalid_properties(
        self, mock_model_duplicator: ModelDuplicator, property_name, value, _
    ):
        """
        Test invalid properties of ModelDuplicator.
        Args:
            mock_model_duplicator: Instance of ModelDuplicator.
            property_name: Name of the property to test.
            value: Invalid value to set and check.
        """
        with pytest.raises(TypeError) as e:
            setattr(mock_model_duplicator, property_name, value)
        assert _("Invalid") in str(e.value)
