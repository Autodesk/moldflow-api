# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Test for DataTransform Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import DataTransform, IntegerArray, DoubleArray
from moldflow import TransformFunctions, TransformOperations, TransformScalarOperations


@pytest.mark.unit
class TestUnitDataTransform:
    """
    Test suite for the DataTransform class.
    """

    @pytest.fixture
    def mock_data_transform(self, mock_object) -> DataTransform:
        """
        Fixture to create a mock instance of DataTransform.
        Args:
            mock_object: Mock object for the DataTransform dependency.
        Returns:
            DataTransform: An instance of DataTransform with the mock object.
        """
        return DataTransform(mock_object)

    @pytest.fixture
    def mock_integer_array(self) -> IntegerArray:
        """
        Fixture for mock IntegerArray

        Returns:
            IntegerArray: An instance of IntegerArray
        """
        mock_integer_arr = Mock(spec=IntegerArray)
        mock_integer_arr.integer_array = Mock()
        return mock_integer_arr

    @pytest.fixture
    def mock_double_array(self) -> DoubleArray:
        """
        Fixture for mock DoubleArray

        Returns:
            DoubleArray: An instance of DoubleArray
        """
        mock_double_arr = Mock(spec=DoubleArray)
        mock_double_arr.double_array = Mock()
        return mock_double_arr

    @pytest.mark.parametrize(
        "func_name, expected",
        [(func_name, func_name.value) for func_name in TransformFunctions]
        + [(func_name.value, func_name.value) for func_name in TransformFunctions],
    )
    # pylint: disable-next=R0913, R0917
    def test_func(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        func_name,
        mock_integer_array: IntegerArray,
        mock_double_array: DoubleArray,
        expected,
    ):
        """
        Test the func method of DataTransform.
        Args:
            mock_data_transform: Mock instance of DataTransform.
            func_name: Name of the function to be tested.
            mock_integer_array: Mock instance of IntegerArray.
            mock_double_array: Mock instance of DoubleArray.
        """
        mock_object.Func.return_value = True
        result = mock_data_transform.func(
            func_name, mock_integer_array, mock_double_array, mock_integer_array, mock_double_array
        )
        assert result is True
        mock_object.Func.assert_called_once_with(
            expected,
            mock_integer_array.integer_array,
            mock_double_array.double_array,
            mock_integer_array.integer_array,
            mock_double_array.double_array,
        )

    @pytest.mark.parametrize(
        "op, expected",
        [(op_name, op_name.value) for op_name in TransformOperations]
        + [(op_name.value, op_name.value) for op_name in TransformOperations],
    )
    # pylint: disable-next=R0913, R0917
    def test_op(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array: IntegerArray,
        mock_double_array: DoubleArray,
        op,
        expected,
    ):
        """
        Test the op method of DataTransform.
        Args:
            mock_data_transform: Mock instance of DataTransform.
            mock_object: Mock object for the DataTransform dependency.
            label_1: First input label array.
            data_1: First input data array.
            op: Operation to be applied.
            label_2: Second input label array.
            data_2: Second input data array.
            label_out: Output label array.
            data_out: Output data array.
        """
        mock_object.Op.return_value = True
        result = mock_data_transform.op(
            mock_integer_array,
            mock_double_array,
            op,
            mock_integer_array,
            mock_double_array,
            mock_integer_array,
            mock_double_array,
        )
        assert result
        mock_object.Op.assert_called_once_with(
            mock_integer_array.integer_array,
            mock_double_array.double_array,
            expected,
            mock_integer_array.integer_array,
            mock_double_array.double_array,
            mock_integer_array.integer_array,
            mock_double_array.double_array,
        )

    @pytest.mark.parametrize(
        "op, scalar_value, expected",
        [(op_name, 1.1, op_name.value) for op_name in TransformScalarOperations]
        + [(op_name.value, 1, op_name.value) for op_name in TransformScalarOperations],
    )
    # pylint: disable-next=R0913, R0917
    def test_scalar(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array: IntegerArray,
        mock_double_array: DoubleArray,
        op,
        scalar_value,
        expected,
    ):
        """
        Test the scalar method of DataTransform.
        Args:
            mock_data_transform: Mock instance of DataTransform.
            func_name: Name of the function to be tested.
            label_in: Input label array.
            data_in: Input data array.
            label_out: Output label array.
            data_out: Output data array.
        """
        mock_object.Scalar.return_value = True
        result = mock_data_transform.scalar(
            mock_integer_array,
            mock_double_array,
            op,
            scalar_value,
            mock_integer_array,
            mock_double_array,
        )
        assert result
        mock_object.Scalar.assert_called_once_with(
            mock_integer_array.integer_array,
            mock_double_array.double_array,
            expected,
            scalar_value,
            mock_integer_array.integer_array,
            mock_double_array.double_array,
        )

    @pytest.mark.parametrize("func_name", list([1, 1.1, True, None]))
    # pylint: disable-next=R0913, R0917
    def test_func_invalid_func_type(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array,
        mock_double_array,
        func_name,
        _,
    ):
        """
        Test the func method of DataTransform with invalid types.

        Args:
            mock_data_transform: Mock instance of DataTransform.
        """
        with pytest.raises(TypeError) as e:
            mock_data_transform.func(
                func_name,
                mock_integer_array,
                mock_double_array,
                mock_integer_array,
                mock_double_array,
            )
        assert _("Invalid") in str(e.value)
        mock_object.Func.assert_not_called()

    @pytest.mark.parametrize("op", list([1, 1.1, True, None]))
    # pylint: disable-next=R0913, R0917
    def test_op_invalid_op_type(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array,
        mock_double_array,
        op,
        _,
    ):
        """
        Test the op method of DataTransform with invalid types.

        Args:
            mock_data_transform: Mock instance of DataTransform.
        """
        with pytest.raises(TypeError) as e:
            mock_data_transform.op(
                mock_integer_array,
                mock_double_array,
                op,
                mock_integer_array,
                mock_double_array,
                mock_integer_array,
                mock_double_array,
            )
        assert _("Invalid") in str(e.value)
        mock_object.Op.assert_not_called()

    @pytest.mark.parametrize("op, scalar_value", [(x, 1.1) for x in [1, 1.1, True, None]])
    # pylint: disable-next=R0913, R0917
    def test_scalar_invalid_op_type(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array,
        mock_double_array,
        op,
        scalar_value,
        _,
    ):
        """
        Test the scalar method of DataTransform with invalid types.

        Args:
            mock_data_transform: Mock instance of DataTransform.
        """
        with pytest.raises(TypeError) as e:
            mock_data_transform.scalar(
                mock_integer_array,
                mock_double_array,
                op,
                scalar_value,
                mock_integer_array,
                mock_double_array,
            )
        assert _("Invalid") in str(e.value)
        mock_object.Scalar.assert_not_called()

    @pytest.mark.parametrize(
        "op, scalar_value", [(x, y) for x in TransformScalarOperations for y in ["1", True, None]]
    )
    # pylint: disable-next=R0913, R0917
    def test_scalar_invalid_scalar_type(
        self,
        mock_data_transform: DataTransform,
        mock_object,
        mock_integer_array,
        mock_double_array,
        op,
        scalar_value,
        _,
    ):
        """
        Test the scalar method of DataTransform with invalid types.

        Args:
            mock_data_transform: Mock instance of DataTransform.
        """
        with pytest.raises(TypeError) as e:
            mock_data_transform.scalar(
                mock_integer_array,
                mock_double_array,
                op,
                scalar_value,
                mock_integer_array,
                mock_double_array,
            )
        assert _("Invalid") in str(e.value)
        mock_object.Scalar.assert_not_called()
