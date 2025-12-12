# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    ModelDuplicator Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import check_type
from .com_proxy import safe_com

class ModelDuplicator:
    """
    Wrapper for ModelDuplicator class of Moldflow Synergy.
    """

    def __init__(self, _model_duplicator):
        """
        Initialize the ModelDuplicator with a ModelDuplicator instance from COM.

        Args:
            _model_duplicator: The ModelDuplicator instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="ModelDuplicator")
        self.model_duplicator = safe_com(_model_duplicator)

    def generate(self):
        """
        Duplicates cavities.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="generate")
        return self.model_duplicator.Generate

    @property
    def num_cavities(self) -> int:
        """
        The number of cavities desired.

        :getter: Get the number of cavities desired.
        :setter: Set the number of cavities desired.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="num_cavities")
        return self.model_duplicator.NumCavities

    @num_cavities.setter
    def num_cavities(self, value: int) -> None:
        """
        The number of cavities desired.

        Args:
            value: The number of cavities.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="num_cavities", value=value)
        check_type(value, int)
        self.model_duplicator.NumCavities = value

    @property
    def by_columns(self) -> bool:
        """
        Whether to arrange by columns.

        :getter: Get whether to arrange by columns.
        :setter: Set whether to arrange by columns.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="by_columns")
        return self.model_duplicator.ByColumns

    @by_columns.setter
    def by_columns(self, value: bool) -> None:
        """
        Whether to arrange by columns.

        Args:
            value: True to arrange by columns, False otherwise.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="by_columns", value=value)
        check_type(value, bool)
        self.model_duplicator.ByColumns = value

    @property
    def num_cols(self) -> int:
        """
        Number of columns[relevant only if ByColumns is set to True]

        :getter: Get the number of columns.
        :setter: Set the number of columns.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="num_cols")
        return self.model_duplicator.NumCols

    @num_cols.setter
    def num_cols(self, value: int) -> None:
        """
        Number of columns[relevant only if ByColumns is set to True]

        Args:
            value: The number of columns.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="num_cols", value=value)
        check_type(value, int)
        self.model_duplicator.NumCols = value

    @property
    def num_rows(self) -> int:
        """
        Number of rows[relevant only if ByColumns is set to True]

        :getter: Get the number of rows.
        :setter: Set the number of rows.
        :type: int
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="num_rows")
        return self.model_duplicator.NumRows

    @num_rows.setter
    def num_rows(self, value: int) -> None:
        """
        Number of columns[relevant only if ByColumns is set to True]

        Args:
            value: The number of rows.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="num_rows", value=value)
        check_type(value, int)
        self.model_duplicator.NumRows = value

    @property
    def x_spacing(self) -> float:
        """
        Spacing in the X direction.

        :getter: Get the spacing in the X direction.
        :setter: Set the spacing in the X direction.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="x_spacing")
        return self.model_duplicator.XSpacing

    @x_spacing.setter
    def x_spacing(self, value: float) -> None:
        """
        Spacing in the X direction.

        Args:
            value: The spacing in the X direction.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="x_spacing", value=value)
        check_type(value, float)
        self.model_duplicator.XSpacing = value

    @property
    def y_spacing(self) -> float:
        """
        Spacing in the Y direction.

        :getter: Get the spacing in the Y direction.
        :setter: Set the spacing in the Y direction.
        :type: float
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="y_spacing")
        return self.model_duplicator.YSpacing

    @y_spacing.setter
    def y_spacing(self, value: float) -> None:
        """
        Spacing in the Y direction.

        Args:
            value: The spacing in the Y direction.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="y_spacing", value=value)
        check_type(value, float)
        self.model_duplicator.YSpacing = value

    @property
    def align_gates(self) -> bool:
        """
        Wheter to position cavities so that their gates are aligned.

        :getter: Get whether to position cavities so that their gates are aligned.
        :setter: Set whether to position cavities so that their gates are aligned.
        :type: bool
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="align_gates")
        return self.model_duplicator.AlignGates

    @align_gates.setter
    def align_gates(self, value: bool) -> None:
        """
        Wheter to position cavities so that their gates are aligned.

        Args:
            value: True to position cavities so that their gates are aligned, False otherwise.
        """
        process_log(__name__, LogMessage.PROPERTY_SET, locals(), name="align_gates", value=value)
        check_type(value, bool)
        self.model_duplicator.AlignGates = value
