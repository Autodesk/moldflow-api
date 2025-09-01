# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=C0302
"""
Test for DiagnosisManager Wrapper Class of moldflow-api module.
"""

from unittest.mock import Mock
import pytest
from moldflow import DiagnosisManager
from moldflow import MeshSummary, EntList
from moldflow.logger import set_is_logging
from tests.api.unit_tests.conftest import VALID_MOCK, INVALID_MOCK_WITH_NONE
from tests.conftest import (
    INVALID_BOOL,
    INVALID_INT,
    INVALID_FLOAT,
    VALID_BOOL,
    VALID_INT,
    VALID_FLOAT,
    pad_and_zip,
)


@pytest.mark.unit
class TestUnitDiagnosisManager:
    """
    Test suite for the DiagnosisManager class.
    """

    set_is_logging(True)

    @pytest.fixture
    def mock_diagnosis_manager(self, mock_object) -> DiagnosisManager:
        """
        Fixture to create a mock instance of DiagnosisManager.
        Args:
            mock_object: Mock object for the DiagnosisManager dependency.
        Returns:
            DiagnosisManager: An instance of DiagnosisManager with the mock object.
        """
        return DiagnosisManager(mock_object)

    def test_create_entity_list(self, mock_diagnosis_manager, mock_object):
        """
        Test the create_entity_list method
        """
        mock_ent_list = Mock()
        mock_object.CreateEntityList = mock_ent_list
        result = mock_diagnosis_manager.create_entity_list()
        assert result.ent_list == mock_ent_list
        assert isinstance(result, EntList)

    def test_create_entity_list_with_none(self, mock_diagnosis_manager, mock_object):
        """
        Test the create_entity_list method
        """
        mock_object.CreateEntityList = None
        result = mock_diagnosis_manager.create_entity_list()
        assert result is None

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [("show_diagnosis", "ShowDiagnosis", (x,), (x,)) for x in VALID_BOOL]
        + [
            ("show_thickness", "ShowThickness2", (w, x, y, z), (w, x, y, z))
            for w in VALID_FLOAT
            for x in VALID_FLOAT
            if x >= w
            for y in VALID_BOOL
            for z in VALID_BOOL
        ]
        + [  # Default tests
            ("show_thickness", "ShowThickness2", (w, x, y), (w, x, y, False))
            for w in VALID_FLOAT
            for x in VALID_FLOAT
            if x >= w
            for y in VALID_BOOL
        ]
        + [
            ("show_aspect_ratio", "ShowAspectRatio2", (w, x, y, z, a, b), (w, x, y, z, a, b))
            for w in VALID_FLOAT
            for x in VALID_FLOAT
            if x >= w
            for y in VALID_BOOL
            for z in VALID_BOOL
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_aspect_ratio", "ShowAspectRatio2", (w, x, y, z, a), (w, x, y, z, a, False))
            for w in VALID_FLOAT
            for x in VALID_FLOAT
            if x >= w
            for y in VALID_BOOL
            for z in VALID_BOOL
            for a in VALID_BOOL
        ]
        + [
            ("show_connect", "ShowConnect2", (w, x, y, z, a), (w.ent_list, x, y, z, a))
            for w, x, y, z, a in pad_and_zip(
                VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL, VALID_BOOL, VALID_BOOL
            )
        ]
        + [
            ("show_connect", "ShowConnect2", (w, x, y, z), (w.ent_list, x, y, z, False))
            for w, x, y, z in pad_and_zip(VALID_MOCK.ENT_LIST, VALID_BOOL, VALID_BOOL, VALID_BOOL)
        ]
        + [
            ("show_edges", "ShowEdges2", (w, x, y, z), (w, x, y, z))
            for w in VALID_BOOL
            for x in VALID_BOOL
            for y in VALID_BOOL
            for z in VALID_BOOL
        ]
        + [
            ("show_edges", "ShowEdges2", (w, x, y), (w, x, y, False))
            for w in VALID_BOOL
            for x in VALID_BOOL
            for y in VALID_BOOL
            for z in VALID_BOOL
        ]
        + [
            ("show_overlapping", "ShowOverlapping3", (a, b, c, d, e, f, g), (a, b, c, d, e, f, g))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in VALID_BOOL
            for f in VALID_BOOL
            for g in VALID_BOOL
        ]
        + [
            ("show_overlapping", "ShowOverlapping3", (a, b, c, d, e, f), (a, b, c, d, e, f, False))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in VALID_BOOL
            for f in VALID_BOOL
        ]
        + [
            ("show_overlapping_txt", "ShowOverlappingTxt", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_match_info", "ShowMatchInfo2", (a, b, c), (a, b, c))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [
            ("show_match_info", "ShowMatchInfo2", (a, b), (a, b, False))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_occurrence", "ShowOccurrence2", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [("show_occurrence", "ShowOccurrence2", (a,), (a, False)) for a in VALID_BOOL]
        + [
            ("show_orient", "ShowOrient2", (a, b, c), (a, b, c))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [
            ("show_orient", "ShowOrient2", (a, b), (a, b, False))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_summary", "ShowSummary2", (a, b, c), (a, b, c))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [("show_summary", "ShowSummary2", (), (False, True, True))]
        + [
            ("show_degen_elements", "ShowDegenElements", (a, b, c), (a, b, c))
            for a in VALID_FLOAT
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [
            ("show_surface_defects_for_3d", "ShowSurfaceDefectsFor3D", (a, b, c, d), (a, b, c, d))
            for a in VALID_INT
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_surface_defects_for_3d", "ShowSurfaceDefectsFor3D", (a, b, c), (a, b, c, False))
            for a in VALID_INT
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [("show_summary_for_beams", "ShowSummaryForBeams", (a,), (a,)) for a in VALID_BOOL]
        + [("show_summary_for_beams", "ShowSummaryForBeams", (), (False,))]
        + [
            ("show_summary_for_tris", "ShowSummaryForTris", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [("show_summary_for_tets", "ShowSummaryForTets", (a,), (a,)) for a in VALID_BOOL]
        + [
            ("show_zero_area_elements", "ShowZeroAreaElements2", (a, b, c, d), (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_zero_area_elements", "ShowZeroAreaElements2", (a, b, c), (a, b, c, False))
            for a in VALID_FLOAT
            for b in VALID_BOOL
            for c in VALID_BOOL
        ]
        + [
            (
                "show_surface_with_bad_trim_curve",
                "ShowSurfWithBadTrimCurv",
                (a, b, c, d, e, f),
                (a, b, c, d, e, f),
            )
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in VALID_BOOL
            for f in VALID_BOOL
        ]
        + [
            (
                "show_surface_with_bad_trim_curve",
                "ShowSurfWithBadTrimCurv",
                (a, b, c, d, e),
                (a, b, c, d, e, False),
            )
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in VALID_BOOL
        ]
        + [
            (
                "get_surface_with_bad_trim_curve",
                "GetSurfWithBadTrimCurv",
                (a, b, c, d, e, f),
                (a, b, c, d, e.integer_array, f.double_array),
            )
            for a, b, c, d, e, f in pad_and_zip(
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "get_surface_with_free_trim_curve",
                "GetSurfWithFreeTrimCurv",
                (a, b, c, d, e),
                (a, b, c, d.integer_array, e.double_array),
            )
            for a, b, c, d, e in pad_and_zip(
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "show_surface_with_free_trim_curve",
                "ShowSurfWithFreeTrimCurv",
                (a, b, c, d, e),
                (a, b, c, d, e),
            )
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in VALID_BOOL
        ]
        + [
            (
                "show_surface_with_free_trim_curve",
                "ShowSurfWithFreeTrimCurv",
                (a, b, c, d),
                (a, b, c, d, False),
            )
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_ld_ratio", "ShowLDRatio", (a, b, c, d), (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_ld_ratio", "ShowLDRatio", (a, b, c), (a, b, c, False))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
        ]
        + [
            ("show_centroid_closeness", "ShowCentroidCloseness", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_centroid_closeness", "ShowCentroidCloseness", (a,), (a, False))
            for a in VALID_BOOL
        ]
        + [
            ("show_beam_element_count", "ShowBeamElementCount", (a, b, c, d), (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_beam_element_count", "ShowBeamElementCount", (a, b, c), (a, b, c, False))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
        ]
        + [
            ("show_cooling_circuit_validity", "ShowCoolingCircuitValidity", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_cooling_circuit_validity", "ShowCoolingCircuitValidity", (a,), (a, False))
            for a in VALID_BOOL
        ]
        + [
            ("show_bubbler_baffle_check", "ShowBubblerBaffleCheck", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [
            ("show_bubbler_baffle_check", "ShowBubblerBaffleCheck", (a,), (a, False))
            for a in VALID_BOOL
        ]
        + [
            ("show_trapped_beam", "ShowTrappedBeam", (a, b), (a, b))
            for a in VALID_BOOL
            for b in VALID_BOOL
        ]
        + [("show_trapped_beam", "ShowTrappedBeam", (a,), (a, False)) for a in VALID_BOOL]
        + [
            ("update_thickness_display", "UpdateThicknessDisplay", (a, b), (a, b))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
        ]
        + [
            ("show_dimensions", "ShowDimensions", (a, b, c, d), (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_dimensions", "ShowDimensions", (a, b, c), (a, b, c, False))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
        ]
        + [
            ("update_dimensional_display", "UpdateDimensionalDisplay", (a, b), (a, b))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
        ],
    )
    # pylint: disable=R0913,R0917
    def test_function_no_return(
        self, mock_diagnosis_manager, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of DiagnosisManager.
        """
        getattr(mock_diagnosis_manager, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, passed_args",
        [
            (
                "get_thickness_diagnosis",
                "GetThicknessDiagnosis2",
                (a, b, c, d, e),
                (a, b, c, d.integer_array, e.double_array),
            )
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
            for d in [VALID_MOCK.INTEGER_ARRAY]
            for e in [VALID_MOCK.DOUBLE_ARRAY]
        ]
        + [
            (
                "get_aspect_ratio_diagnosis",
                "GetAspectRatioDiagnosis2",
                (a, b, c, d, e, f),
                (a, b, c, d, e.integer_array, f.double_array),
            )
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b >= a
            for c in VALID_BOOL
            for d in VALID_BOOL
            for e in [VALID_MOCK.INTEGER_ARRAY]
            for f in [VALID_MOCK.DOUBLE_ARRAY]
        ]
        + [
            (
                "get_connectivity_diagnosis",
                "GetConnectivityDiagnosis2",
                (a, b, c, d, e),
                (a.ent_list, b, c, d.integer_array, e.double_array),
            )
            for a, b, c, d, e in pad_and_zip(
                VALID_MOCK.ENT_LIST,
                VALID_BOOL,
                VALID_BOOL,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "get_edges_diagnosis",
                "GetEdgesDiagnosis2",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_BOOL, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_overlap_diagnosis",
                "GetOverlapDiagnosis2",
                (a, b, c, d, e),
                (a, b, c, d.integer_array, e.double_array),
            )
            for a, b, c, d, e in pad_and_zip(
                VALID_BOOL,
                VALID_BOOL,
                VALID_BOOL,
                VALID_MOCK.INTEGER_ARRAY,
                VALID_MOCK.DOUBLE_ARRAY,
            )
        ]
        + [
            (
                "get_occurrence_diagnosis",
                "GetOccurrenceDiagnosis2",
                (a, b, c),
                (a, b.integer_array, c.double_array),
            )
            for a, b, c in pad_and_zip(
                VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_match_info_diagnosis",
                "GetMatchInfoDiagnosis",
                (a, b),
                (a.integer_array, b.double_array),
            )
            for a, b in pad_and_zip(VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY)
        ]
        + [
            (
                "get_orientation_diagnosis",
                "GetOrientationDiagnosis2",
                (a, b, c),
                (a, b.integer_array, c.double_array),
            )
            for a, b, c in pad_and_zip(
                VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_zero_area_elements_diagnosis",
                "GetZeroAreaElementsDiagnosis2",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            ("get_inverted_tetras", "GetInvertedTetras", (a, b), (a, b.integer_array))
            for a, b in pad_and_zip(VALID_BOOL, VALID_MOCK.INTEGER_ARRAY)
        ]
        + [
            ("get_collapsed_faces", "GetCollapsedFaces", (a, b), (a, b.integer_array))
            for a, b in pad_and_zip(VALID_BOOL, VALID_MOCK.INTEGER_ARRAY)
        ]
        + [
            (
                "get_insufficient_refinement_through_thickness",
                "GetInsufficientRefinementThroughThickness",
                (a, b, c),
                (a, b, c.integer_array),
            )
            for a, b, c in pad_and_zip(VALID_INT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY)
        ]
        + [
            (
                "get_internal_long_edges",
                "GetInternalLongEdges",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_tetras_with_extremely_large_volume",
                "GetTetrasWithExtremelyLargeVolume",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_tetras_with_high_aspect_ratio",
                "GetTetrasWithHighAspectRatio",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_tetras_with_extreme_min_angle_between_faces",
                "GetTetrasWithExtremeMinAngleBetweenFaces",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ]
        + [
            (
                "get_tetras_with_extreme_max_angle_between_faces",
                "GetTetrasWithExtremeMaxAngleBetweenFaces",
                (a, b, c, d),
                (a, b, c.integer_array, d.double_array),
            )
            for a, b, c, d in pad_and_zip(
                VALID_FLOAT, VALID_BOOL, VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY
            )
        ],
    )
    # pylint: disable=R0913,R0917
    def test_function_int_return(
        self, mock_diagnosis_manager, mock_object, property_name, pascal_name, args, passed_args
    ):
        """
        Test the function method of DiagnosisManager that returns an integer.
        """
        expected = 1
        getattr(mock_object, pascal_name).return_value = expected
        result = getattr(mock_diagnosis_manager, property_name)(*args)
        getattr(mock_object, pascal_name).assert_called_once_with(*passed_args)
        assert result == expected
        assert isinstance(result, int)

    @pytest.mark.parametrize(
        "args, passed_args",
        [
            ((a, b, c, d), (a, b, c, d))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [((a,), (a, True, True, False)) for a in VALID_BOOL],
    )
    def test_get_mesh_summary(self, mock_diagnosis_manager, mock_object, args, passed_args):
        """
        Test the get_mesh_summary method of DiagnosisManager.
        """
        expected = Mock(spec=MeshSummary)
        expected.mesh_summary = Mock()
        mock_object.GetMeshSummary2.return_value = expected
        result = mock_diagnosis_manager.get_mesh_summary(*args)
        mock_object.GetMeshSummary2.assert_called_once_with(*passed_args)
        assert result.mesh_summary == expected

    @pytest.mark.parametrize(
        "args, passed_args",
        [
            ((a, b, c, d), (a, b, c, d))
            for a in VALID_BOOL
            for b in VALID_BOOL
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [((a,), (a, True, True, False)) for a in VALID_BOOL],
    )
    def test_get_mesh_summary_none(self, mock_diagnosis_manager, mock_object, args, passed_args):
        """
        Test the get_mesh_summary method of DiagnosisManager.
        """
        expected = None
        mock_object.GetMeshSummary2.return_value = expected
        result = mock_diagnosis_manager.get_mesh_summary(*args)
        mock_object.GetMeshSummary2.assert_called_once_with(*passed_args)
        assert result == expected

    @pytest.mark.parametrize(
        "property_name, pascal_name, args, invalid_val",
        [
            ("show_diagnosis", "ShowDiagnosis", [VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL]))
        ]
        + [
            (
                "show_thickness",
                "ShowThickness2",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "show_aspect_ratio",
                "ShowAspectRatio2",
                [
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "show_connect",
                "ShowConnect2",
                [VALID_MOCK.ENT_LIST, VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "show_edges",
                "ShowEdges2",
                [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_BOOL, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "show_overlapping",
                "ShowOverlapping3",
                [
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            ("show_match_info", "ShowMatchInfo2", [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_BOOL, INVALID_BOOL, INVALID_BOOL])
            )
        ]
        + [
            ("show_occurrence", "ShowOccurrence2", [VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            ("show_orient", "ShowOrient2", [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_BOOL, INVALID_BOOL, INVALID_BOOL])
            )
        ]
        + [
            ("show_summary", "ShowSummary2", [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_BOOL, INVALID_BOOL, INVALID_BOOL])
            )
        ]
        + [
            ("show_summary_for_beams", "ShowSummaryForBeams", [VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL]))
        ]
        + [
            ("show_summary_for_tris", "ShowSummaryForTris", [VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            ("show_summary_for_tets", "ShowSummaryForTets", [VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL]))
        ]
        + [
            (
                "show_zero_area_elements",
                "ShowZeroAreaElements2",
                [VALID_FLOAT[0], VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "show_surface_with_bad_trim_curve",
                "ShowSurfWithBadTrimCurv",
                [
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "get_surface_with_bad_trim_curve",
                "GetSurfWithBadTrimCurv",
                [
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "show_surface_with_free_trim_curve",
                "ShowSurfWithFreeTrimCurv",
                [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_BOOL, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_surface_with_free_trim_curve",
                "GetSurfWithFreeTrimCurv",
                [
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "show_ld_ratio",
                "ShowLDRatio",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            ("show_centroid_closeness", "ShowCentroidCloseness", [VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            (
                "show_beam_element_count",
                "ShowBeamElementCount",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "show_cooling_circuit_validity",
                "ShowCoolingCircuitValidity",
                [VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            (
                "show_bubbler_baffle_check",
                "ShowBubblerBaffleCheck",
                [VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            ("show_trapped_beam", "ShowTrappedBeam", [VALID_BOOL[0], VALID_BOOL[0]], x)
            for x in ((index, value) for index, value in enumerate([INVALID_BOOL, INVALID_BOOL]))
        ]
        + [
            (
                "update_thickness_display",
                "UpdateThicknessDisplay",
                [VALID_FLOAT[0], VALID_FLOAT[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT]))
        ]
        + [
            (
                "show_dimensions",
                "ShowDimensions",
                [VALID_FLOAT[0], VALID_FLOAT[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_FLOAT, INVALID_BOOL, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "update_dimensional_display",
                "UpdateDimensionalDisplay",
                [VALID_FLOAT[0], VALID_FLOAT[0]],
                x,
            )
            for x in ((index, value) for index, value in enumerate([INVALID_FLOAT, INVALID_FLOAT]))
        ]
        + [
            (
                "get_mesh_summary",
                "GetMeshSummary2",
                [VALID_BOOL[0], VALID_BOOL[0], VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_BOOL, INVALID_BOOL, INVALID_BOOL])
            )
        ]
        + [
            (
                "get_thickness_diagnosis",
                "GetThicknessDiagnosis2",
                [
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "get_aspect_ratio_diagnosis",
                "GetAspectRatioDiagnosis2",
                [
                    VALID_FLOAT[0],
                    VALID_FLOAT[0],
                    VALID_BOOL[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_FLOAT,
                        INVALID_FLOAT,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "get_connectivity_diagnosis",
                "GetConnectivityDiagnosis2",
                [
                    VALID_MOCK.ENT_LIST,
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                    ]
                )
            )
        ]
        + [
            (
                "get_edges_diagnosis",
                "GetEdgesDiagnosis2",
                [VALID_BOOL[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_BOOL, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_overlap_diagnosis",
                "GetOverlapDiagnosis2",
                [
                    VALID_BOOL[0],
                    VALID_BOOL[0],
                    VALID_MOCK.INTEGER_ARRAY,
                    VALID_MOCK.DOUBLE_ARRAY,
                    VALID_BOOL[0],
                ],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [
                        INVALID_BOOL,
                        INVALID_BOOL,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_MOCK_WITH_NONE,
                        INVALID_BOOL,
                    ]
                )
            )
        ]
        + [
            (
                "get_occurrence_diagnosis",
                "GetOccurrenceDiagnosis2",
                [VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_match_info_diagnosis",
                "GetMatchInfoDiagnosis",
                [VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE])
            )
        ]
        + [
            (
                "get_orientation_diagnosis",
                "GetOrientationDiagnosis2",
                [VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_zero_area_elements_diagnosis",
                "GetZeroAreaElementsDiagnosis2",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_inverted_tetras",
                "GetInvertedTetras",
                [VALID_MOCK.INTEGER_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value) for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_BOOL])
            )
        ]
        + [
            (
                "get_collapsed_faces",
                "GetCollapsedFaces",
                [VALID_MOCK.INTEGER_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value) for index, value in enumerate([INVALID_MOCK_WITH_NONE, INVALID_BOOL])
            )
        ]
        + [
            (
                "get_insufficient_refinement_through_thickness",
                "GetInsufficientRefinementThroughThickness",
                [VALID_INT[0], VALID_MOCK.INTEGER_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate([INVALID_INT, INVALID_MOCK_WITH_NONE, INVALID_BOOL])
            )
        ]
        + [
            (
                "get_internal_long_edges",
                "GetInternalLongEdges",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_tetras_with_extremely_large_volume",
                "GetTetrasWithExtremelyLargeVolume",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_tetras_with_high_aspect_ratio",
                "GetTetrasWithHighAspectRatio",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_tetras_with_extreme_min_angle_between_faces",
                "GetTetrasWithExtremeMinAngleBetweenFaces",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ]
        + [
            (
                "get_tetras_with_extreme_max_angle_between_faces",
                "GetTetrasWithExtremeMaxAngleBetweenFaces",
                [VALID_FLOAT[0], VALID_MOCK.INTEGER_ARRAY, VALID_MOCK.DOUBLE_ARRAY, VALID_BOOL[0]],
                x,
            )
            for x in (
                (index, value)
                for index, value in enumerate(
                    [INVALID_FLOAT, INVALID_MOCK_WITH_NONE, INVALID_MOCK_WITH_NONE, INVALID_BOOL]
                )
            )
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_inputs(
        self, mock_diagnosis_manager, mock_object, property_name, pascal_name, args, invalid_val, _
    ):
        """
        Test the function method of DiagnosisManager with invalid inputs.
        """
        for i in invalid_val[1]:
            args[invalid_val[0]] = i
            with pytest.raises(TypeError) as e:
                getattr(mock_diagnosis_manager, property_name)(*tuple(args))
            assert _("Invalid") in str(e.value)
            getattr(mock_object, pascal_name).assert_not_called()

    @pytest.mark.parametrize(
        "property_name, pascal_name, args",
        [
            ("show_thickness", "ShowThickness2", (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("show_aspect_ratio", "ShowAspectRatio2", (a, b, c, d, e, f))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in [VALID_MOCK.INTEGER_ARRAY]
            for e in [VALID_MOCK.DOUBLE_ARRAY]
            for f in VALID_BOOL
        ]
        + [
            ("get_thickness_diagnosis", "GetThicknessDiagnosis2", (a, b, d, e, c))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in [VALID_MOCK.INTEGER_ARRAY]
            for e in [VALID_MOCK.DOUBLE_ARRAY]
        ]
        + [
            ("get_aspect_ratio_diagnosis", "GetAspectRatioDiagnosis2", (a, b, c, d, e, f))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in [VALID_MOCK.INTEGER_ARRAY]
            for e in [VALID_MOCK.DOUBLE_ARRAY]
            for f in VALID_BOOL
        ]
        + [
            ("show_ld_ratio", "ShowLDRatio", (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("update_thickness_display", "UpdateThicknessDisplay", (a, b))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a or a > b
        ]
        + [
            ("show_dimensions", "ShowDimensions", (a, b, c, d))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
            for c in VALID_BOOL
            for d in VALID_BOOL
        ]
        + [
            ("update_dimensional_display", "UpdateDimensionalDisplay", (a, b))
            for a in VALID_FLOAT
            for b in VALID_FLOAT
            if b < a
        ],
    )
    # pylint: disable=R0913,R0917
    def test_invalid_range(
        self, mock_diagnosis_manager, mock_object, property_name, pascal_name, args, _
    ):
        """
        Test the function method of DiagnosisManager with invalid range inputs.
        """
        with pytest.raises(ValueError) as e:
            getattr(mock_diagnosis_manager, property_name)(*args)
        assert _("Invalid") in str(e.value)
        getattr(mock_object, pascal_name).assert_not_called()
