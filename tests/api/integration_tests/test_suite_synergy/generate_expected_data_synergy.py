# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Generate data for the Synergy class.
"""

from moldflow import Synergy
from tests.api.integration_tests.data_generation.generate_data_helper import generate_json


@generate_json(file_set=None)
def generate_synergy_data(synergy: Synergy = None):
    """
    Generate data for the Synergy class.
    Returns a dict with relevant properties.
    """

    build_number_parts = synergy.build_number.split(".")
    build_number_major_minor = ".".join(build_number_parts[:2])

    return {"version": synergy.version, "build_number": build_number_major_minor}


if __name__ == "__main__":
    generate_synergy_data()
