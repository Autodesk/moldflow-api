# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    DataTransform Class API Wrapper
"""

from .logger import process_log, LogMessage
from .helper import check_type, check_and_coerce_optional, check_and_coerce_optional, get_enum_value
from .com_proxy import safe_com
from .common import TransformFunctions, TransformOperations, TransformScalarOperations
from .integer_array import IntegerArray
from .double_array import DoubleArray


class DataTransform:
    """
    Wrapper for DataTransform class of Moldflow Synergy.
    """

    def __init__(self, _data_transform):
        """
        Initialize the DataTransform with a DataTransform instance from COM.

        Args:
            _data_transform: The DataTransform instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="DataTransform")
        self.data_transform = safe_com(_data_transform)

    # pylint: disable=R0913, R0917
    def func(
        self,
        func_name: TransformFunctions | str,
        label_in: IntegerArray | None,
        data_in: DoubleArray | None,
        label_out: IntegerArray | None,
        data_out: DoubleArray | None,
    ) -> bool:
        """
        This function calculates data using given function.

        Args:
            func_name (TransformFunctions | str): The name of the function to be applied.
            label_in (IntegerArray): The input label array.
            data_in (DoubleArray): The input data array.
            label_out (IntegerArray): The output label array.
            data_out (DoubleArray): The output data array.

        Returns:
            bool: True if the function was applied successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="func")
        func_name = get_enum_value(func_name, TransformFunctions)

        return self.data_transform.Func(
            func_name,
            check_and_coerce_optional(label_in, IntegerArray),
            check_and_coerce_optional(data_in, DoubleArray),
            check_and_coerce_optional(label_out, IntegerArray),
            check_and_coerce_optional(data_out, DoubleArray),
        )

    # pylint: disable=R0913, R0917
    def op(
        self,
        label_1: IntegerArray | None,
        data_1: DoubleArray | None,
        op: TransformOperations | str,
        label_2: IntegerArray | None,
        data_2: DoubleArray | None,
        label_out: IntegerArray | None,
        data_out: DoubleArray | None,
    ) -> bool:
        """
        This function calculates data using given operation.

        Args:
            label_1 (IntegerArray): The first input label array.
            data_1 (DoubleArray): The first input data array.
            op (TransformOperations | str): The operation to be applied.
            label_2 (IntegerArray): The second input label array.
            data_2 (DoubleArray): The second input data array.
            label_out (IntegerArray): The output label array.
            data_out (DoubleArray): The output data array.

        Returns:
            bool: True if the operation was applied successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="op")

        op = get_enum_value(op, TransformOperations)

        return self.data_transform.Op(
            check_and_coerce_optional(label_1, IntegerArray),
            check_and_coerce_optional(data_1, DoubleArray),
            op,
            check_and_coerce_optional(label_2, IntegerArray),
            check_and_coerce_optional(data_2, DoubleArray),
            check_and_coerce_optional(label_out, IntegerArray),
            check_and_coerce_optional(data_out, DoubleArray),
        )

    # pylint: disable=R0913, R0917
    def scalar(
        self,
        label_in: IntegerArray | None,
        data_in: DoubleArray | None,
        op: TransformScalarOperations | str,
        scalar_value: float,
        label_out: IntegerArray | None,
        data_out: DoubleArray | None,
    ) -> bool:
        """
        This function calculates data using given scalar operation.

        Args:
            label_in (IntegerArray): The input label array.
            data_in (DoubleArray): The input data array.
            op (TransformScalarOperations | str): The scalar operation to be applied.
            scalar_value (float): The scalar value to be used in the operation.
            label_out (IntegerArray): The output label array.
            data_out (DoubleArray): The output data array.

        Returns:
            bool: True if the scalar operation was applied successfully, False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="scalar")

        op = get_enum_value(op, TransformScalarOperations)
        check_type(scalar_value, (float, int))

        return self.data_transform.Scalar(
            check_and_coerce_optional(label_in, IntegerArray),
            check_and_coerce_optional(data_in, DoubleArray),
            op,
            scalar_value,
            check_and_coerce_optional(label_out, IntegerArray),
            check_and_coerce_optional(data_out, DoubleArray),
        )
