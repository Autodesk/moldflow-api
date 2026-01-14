# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MeshSummary Class API Wrapper
"""

from .logger import process_log
from .common import LogMessage
from .com_proxy import safe_com


class MeshSummary:
    """
    Wrapper for MeshSummary class of Moldflow Synergy.
    """

    def __init__(self, _mesh_summary):
        """
        Initialize the MeshSummary with a MeshSummary instance from COM.

        Args:
            _mesh_summary: The MeshSummary instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MeshSummary")
        self.mesh_summary = safe_com(_mesh_summary)

    @property
    def min_aspect_ratio(self) -> float:
        """
        Minimum aspect ratio of the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="min_aspect_ratio")
        return self.mesh_summary.MinAspectRatio

    @property
    def max_aspect_ratio(self) -> float:
        """
        Maximum aspect ratio of the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="max_aspect_ratio")
        return self.mesh_summary.MaxAspectRatio

    @property
    def ave_aspect_ratio(self) -> float:
        """
        Average aspect ratio of the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="ave_aspect_ratio")
        return self.mesh_summary.AveAspectRatio

    @property
    def free_edges_count(self) -> int:
        """
        Number of free edges in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="free_edges_count")
        return self.mesh_summary.FreeEdgesCount

    @property
    def manifold_edges_count(self) -> int:
        """
        Number of manifold edges in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="manifold_edges_count")
        return self.mesh_summary.ManifoldEdgesCount

    @property
    def non_manifold_edges_count(self) -> int:
        """
        Number of non-manifold edges in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="non_manifold_edges_count")
        return self.mesh_summary.NonManifoldEdgesCount

    @property
    def triangles_count(self) -> int:
        """
        Number of triangles in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="triangles_count")
        return self.mesh_summary.TrianglesCount

    @property
    def tetras_count(self) -> int:
        """
        Number of tetrahedra in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="tetras_count")
        return self.mesh_summary.TetrasCount

    @property
    def nodes_count(self) -> int:
        """
        Number of nodes in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="nodes_count")
        return self.mesh_summary.NodesCount

    @property
    def beams_count(self) -> int:
        """
        Number of beams in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="beams_count")
        return self.mesh_summary.BeamsCount

    @property
    def connectivity_regions(self) -> int:
        """
        Number of connectivity regions in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="connectivity_regions")
        return self.mesh_summary.ConnectivityRegions

    @property
    def unoriented(self) -> int:
        """
        Number of unoriented elements in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="unoriented")
        return self.mesh_summary.Unoriented

    @property
    def intersection_elements(self) -> int:
        """
        Number of intersection elements in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="intersection_elements")
        return self.mesh_summary.IntersectionElements

    @property
    def match_ratio(self) -> float:
        """
        Mesh match ratio
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="match_ratio")
        return self.mesh_summary.MatchRatio

    @property
    def reciprocal_match_ratio(self) -> float:
        """
        Mesh reciprocal match ratio
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="reciprocal_match_ratio")
        return self.mesh_summary.ReciprocalMatchRatio

    @property
    def mesh_volume(self) -> float:
        """
        Volume of mesh
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="mesh_volume")
        return self.mesh_summary.MeshVolume

    @property
    def runner_volume(self) -> float:
        """
        Volume of runner
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="runner_volume")
        return self.mesh_summary.RunnerVolume

    @property
    def fusion_area(self) -> float:
        """
        Area of fusion
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="fusion_area")
        return self.mesh_summary.FusionArea

    @property
    def overlap_elements(self) -> int:
        """
        Number of overlap elements in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="overlap_elements")
        return self.mesh_summary.OverlapElements

    @property
    def duplicated_beams(self) -> int:
        """
        Number of duplicated beams in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="duplicated_beams")
        return self.mesh_summary.DuplicatedBeams

    @property
    def zero_triangles(self) -> int:
        """
        Number of zero triangles in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="zero_triangles")
        return self.mesh_summary.ZeroTriangles

    @property
    def zero_beams(self) -> int:
        """
        Number of zero beams in the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="zero_beams")
        return self.mesh_summary.ZeroBeams

    @property
    def percent_tets_ar_gt_thresh(self) -> float:
        """
        Percent of tetrahedra with aspect ratio greater than the threshold.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="percent_tets_ar_gt_thresh")
        return self.mesh_summary.PercentTetsARgtThresh

    @property
    def max_dihedral_angle(self) -> float:
        """
        Max dihedral angle of the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="max_dihedral_angle")
        return self.mesh_summary.MaxDihedralAngle

    @property
    def percent_tets_mda_gt_thresh(self) -> float:
        """
        Percent of tetrahedra with dihedral angle greater than the threshold.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="percent_tets_mda_gt_thresh")
        return self.mesh_summary.PercentTetsMDAgtThresh

    @property
    def max_volume_ratio(self) -> float:
        """
        Max volume ratio of the mesh.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="max_volume_ratio")
        return self.mesh_summary.MaxVolumeRatio

    @property
    def percent_tets_vr_gt_thresh(self) -> float:
        """
        Percent of tetrahedra with volume ratio greater than the threshold.
        """
        process_log(__name__, LogMessage.PROPERTY_GET, locals(), name="percent_tets_vr_gt_thresh")
        return self.mesh_summary.PercentTetsVRgtThresh
