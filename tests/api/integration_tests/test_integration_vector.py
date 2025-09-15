"""
Integration tests for Vector Wrapper Class of moldflow-api module.

These tests focus on testing the actual functionality and behavior
of the Vector class with real Moldflow Synergy COM objects.
"""

import pytest
from moldflow import Vector, Synergy


@pytest.mark.integration
@pytest.mark.vector
class TestIntegrationVector:
    """
    Integration test suite for the Vector class.
    """

    @pytest.fixture
    def vector(self, synergy: Synergy):
        """
        Fixture to create a real Vector instance for integration testing.
        """
        return synergy.create_vector()

    def _check_vector_values(
        self,
        vector: Vector,
        expected_x: int | float = 0.0,
        expected_y: int | float = 0.0,
        expected_z: int | float = 0.0,
    ):
        """
        Verify the values of the vector.
        """
        assert vector.x == expected_x
        assert vector.y == expected_y
        assert vector.z == expected_z

    @pytest.mark.synergy
    def test_create_vector(self, synergy: Synergy):
        """
        Test that Vector can be created from Synergy instance.
        """
        vector = synergy.create_vector()
        self._check_vector_values(vector)

    @pytest.mark.parametrize("x, y, z", [(10.0, 20.0, 30.0), (-1.1, 2.2, 3)])
    def test_set_xyz(self, vector: Vector, x: int | float, y: int | float, z: int | float):
        """
        Test that x, y, z properties can be accessed.
        """
        self._check_vector_values(vector)

        vector.set_xyz(x, y, z)
        self._check_vector_values(vector, x, y, z)

    @pytest.mark.parametrize("x, y, z", [(-1.1, 2.2, 3), (10.0, 20.0, 30.0)])
    def test_set_x_y_z_properties(
        self, vector: Vector, x: int | float, y: int | float, z: int | float
    ):
        """
        Testing setter properties of Vector.
        """
        vector.x = x
        vector.y = y
        vector.z = z

        self._check_vector_values(vector, x, y, z)

    @pytest.mark.parametrize(
        "x, y, z, new_x, new_y, new_z",
        [(1.0, 2.0, 3.0, 100.0, 2.0, 3.0), (1.0, 2.0, 3.0, 1.0, 20.0, 30.0)],
    )
    # pylint: disable-next=R0913, R0917
    def test_vector_state_persistence(
        self,
        vector: Vector,
        x: int | float,
        y: int | float,
        z: int | float,
        new_x: int | float,
        new_y: int | float,
        new_z: int | float,
    ):
        """
        Test Vector state persistence.
        """
        vector.set_xyz(x, y, z)

        vector.x = new_x
        self._check_vector_values(vector, new_x, y, z)

        vector.y = new_y
        self._check_vector_values(vector, new_x, new_y, z)

        vector.z = new_z
        self._check_vector_values(vector, new_x, new_y, new_z)

    def test_reference_behavior(self, vector: Vector):
        """
        Test reference behavior of Vector.
        """
        vector.set_xyz(1.0, 2.0, 3.0)
        vector_copy = vector
        self._check_vector_values(vector_copy, 1.0, 2.0, 3.0)

        vector_copy.set_xyz(4.0, 5.0, 6.0)
        self._check_vector_values(vector_copy, 4.0, 5.0, 6.0)
        self._check_vector_values(vector, 4.0, 5.0, 6.0)

        vector_copy2 = Vector(vector.vector)
        self._check_vector_values(vector_copy2, 4.0, 5.0, 6.0)

        vector_copy2.set_xyz(7.0, 8.0, 9.0)
        self._check_vector_values(vector_copy2, 7.0, 8.0, 9.0)
        self._check_vector_values(vector, 7.0, 8.0, 9.0)
