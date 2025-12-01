# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for VectorArray Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the VectorArray class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import VectorArray, Synergy


@pytest.mark.integration
@pytest.mark.vector_array
class TestIntegrationVectorArray:
    """
    Integration test suite for the VectorArray class.
    """

    @pytest.fixture
    def vector_array(self, synergy: Synergy):
        """
        Fixture to create a real VectorArray instance for integration testing.
        """
        return synergy.create_vector_array()

    def _check_vector_array_size(self, vector_array: VectorArray, expected_size: int):
        """
        Verify the size of the vector array.
        """
        assert vector_array.size == expected_size

    def _check_vector_at_index(
        self, vector_array: VectorArray, index: int, expected_value: list[int | float]
    ):
        """
        Verify the values of a vector at a specific index in the array.
        """
        assert vector_array.x(index) == expected_value[0]
        assert vector_array.y(index) == expected_value[1]
        assert vector_array.z(index) == expected_value[2]

    @pytest.mark.synergy
    def test_create_vector_array(self, synergy: Synergy):
        """
        Test that VectorArray can be created from Synergy instance.
        """
        vector_array = synergy.create_vector_array()
        self._check_vector_array_size(vector_array, 0)

    def test_add_xyz_single_vector(self, vector_array: VectorArray):
        """
        Test adding a single vector to the array using add_xyz.
        """
        self._check_vector_array_size(vector_array, 0)

        vector_array.add_xyz(1.0, 2.0, 3.0)
        self._check_vector_array_size(vector_array, 1)
        self._check_vector_at_index(vector_array, 0, [1.0, 2.0, 3.0])

    @pytest.mark.parametrize(
        "vectors",
        [
            [(1, 2.2, 3.3), (4.4, 5.5, 6.6)],
            [(0, 0.0, 0.0), (-1.0, -2, -3.0), (10.5, 20.5, 30)],
            [(-5.5, 10.0, 15.5)],
        ],
    )
    def test_add_xyz_multiple_vectors(
        self, vector_array: VectorArray, vectors: list[tuple[float | int, float | int, float | int]]
    ):
        """
        Test adding multiple vectors to the array.
        """
        self._check_vector_array_size(vector_array, 0)

        for i, (x, y, z) in enumerate(vectors):
            vector_array.add_xyz(x, y, z)
            self._check_vector_array_size(vector_array, i + 1)
            self._check_vector_at_index(vector_array, i, [x, y, z])

        self._check_vector_array_size(vector_array, len(vectors))
        for i, (x, y, z) in enumerate(vectors):
            self._check_vector_at_index(vector_array, i, [x, y, z])

    def test_clear_empty_array(self, vector_array: VectorArray):
        """
        Test clearing an empty vector array.
        """
        # Initially empty
        self._check_vector_array_size(vector_array, 0)

        # Clear empty array
        vector_array.clear()
        self._check_vector_array_size(vector_array, 0)

    def test_clear_populated_array(self, vector_array: VectorArray):
        """
        Test clearing a populated vector array.
        """
        # Add some vectors
        test_vectors = [(1.1, 2.2, 3.3), (4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]
        for x, y, z in test_vectors:
            vector_array.add_xyz(x, y, z)

        self._check_vector_array_size(vector_array, len(test_vectors))

        # Clear the array
        vector_array.clear()
        self._check_vector_array_size(vector_array, 0)

    def test_vector_array_indexing(self, vector_array: VectorArray):
        """
        Test accessing vectors by index in the array.
        """
        test_vectors = [(10.1, 20.2, 30.3), (-5.5, 15.5, 25.5), (0.0, 100.0, 200.0)]

        # Add test vectors
        for x, y, z in test_vectors:
            vector_array.add_xyz(x, y, z)

        # Test accessing each vector by index
        for i, (expected_x, expected_y, expected_z) in enumerate(test_vectors):
            self._check_vector_at_index(vector_array, i, [expected_x, expected_y, expected_z])

    @pytest.mark.parametrize(
        "initial_vectors, additional_vectors, final_vectors",
        [([(1.1, 2.2, 3.3), (4.4, 5.5, 6.6)], [(7.7, 8.8, 9.9)], [(10.1, 11.2, 12.3)])],
    )
    def test_vector_array_state_persistence(
        self,
        vector_array: VectorArray,
        initial_vectors: list[tuple[float, float, float]],
        additional_vectors: list[tuple[float, float, float]],
        final_vectors: list[tuple[float, float, float]],
    ):
        """
        Test that VectorArray maintains state correctly across multiple operations.
        """
        # Add initial vectors
        for x, y, z in initial_vectors:
            vector_array.add_xyz(x, y, z)

        # Verify initial state
        self._check_vector_array_size(vector_array, len(initial_vectors))
        for i, (x, y, z) in enumerate(initial_vectors):
            self._check_vector_at_index(vector_array, i, [x, y, z])

        # Add additional vectors
        for x, y, z in additional_vectors:
            vector_array.add_xyz(x, y, z)

        # Verify all vectors are still correct
        all_vectors = initial_vectors + additional_vectors
        self._check_vector_array_size(vector_array, len(all_vectors))
        for i, (x, y, z) in enumerate(all_vectors):
            self._check_vector_at_index(vector_array, i, [x, y, z])

        # Clear and verify
        vector_array.clear()
        self._check_vector_array_size(vector_array, 0)

        # Add final vectors after clear
        for x, y, z in final_vectors:
            vector_array.add_xyz(x, y, z)

        self._check_vector_array_size(vector_array, len(final_vectors))
        for i, (x, y, z) in enumerate(final_vectors):
            self._check_vector_at_index(vector_array, i, [x, y, z])

    @pytest.mark.parametrize("size", [1, 5, 10])
    def test_vector_array_size_property(self, vector_array: VectorArray, size: int):
        """
        Test that the size property correctly reflects the number of vectors.
        """
        self._check_vector_array_size(vector_array, 0)

        for i in range(size):
            vector_array.add_xyz(float(i * 1.1), float(i * 2.2), float(i * 3.3))
            self._check_vector_array_size(vector_array, i + 1)

        self._check_vector_array_size(vector_array, size)

    def test_reference_behavior(self, vector_array: VectorArray):
        """
        Test reference behavior of VectorArray.
        """
        vector_array.add_xyz(1.0, 2.0, 3.0)
        vector_array_copy = vector_array
        self._check_vector_array_size(vector_array_copy, 1)
        self._check_vector_at_index(vector_array_copy, 0, [1.0, 2.0, 3.0])

        vector_array_copy.add_xyz(4.0, 5.0, 6.0)
        self._check_vector_array_size(vector_array_copy, 2)
        self._check_vector_at_index(vector_array_copy, 0, [1.0, 2.0, 3.0])
        self._check_vector_at_index(vector_array_copy, 1, [4.0, 5.0, 6.0])
        self._check_vector_at_index(vector_array, 1, [4.0, 5.0, 6.0])

        vector_array_copy2 = VectorArray(vector_array.vector_array)
        self._check_vector_array_size(vector_array_copy2, 2)
        self._check_vector_at_index(vector_array_copy2, 0, [1.0, 2.0, 3.0])
        self._check_vector_at_index(vector_array_copy2, 1, [4.0, 5.0, 6.0])

        vector_array_copy2.add_xyz(7.0, 8.0, 9.0)
        self._check_vector_array_size(vector_array_copy2, 3)
        self._check_vector_at_index(vector_array_copy2, 0, [1.0, 2.0, 3.0])
        self._check_vector_at_index(vector_array_copy2, 1, [4.0, 5.0, 6.0])
        self._check_vector_at_index(vector_array_copy2, 2, [7.0, 8.0, 9.0])
