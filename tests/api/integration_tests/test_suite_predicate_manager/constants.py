# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Constants for predicate manager tests.
"""

from dataclasses import dataclass, field
from moldflow import CrossSectionType


@dataclass
class EntityData:
    """
    Data class for an entity.
    Produces:
    - size
    - converted_string
    - triple_split (if split=True)
    """

    entity_type: str
    start_index: int
    end_index: int
    split: bool = True

    size: int = field(init=False)
    label: str = field(init=False)
    converted_string: str = field(init=False)

    def __post_init__(self):
        # Size of this entity block
        self.size = self.end_index - self.start_index + 1

        # Convert index range to strings like "N1 N2 N3 ..."
        self.label = f"{self.entity_type}{self.start_index}:{self.end_index}"
        self.converted_string = "".join(
            f"{self.entity_type}{i} " for i in range(self.start_index, self.end_index + 1)
        )

        if self.split:
            self.triple_split = self._triple_split()

    def _triple_split(self):
        """
        Triple split this entity into three non-overlapping ranges.

        Example:
          N1:100 → (N1:50), (N26:75), (N51:100)
        """
        half = self.size // 2
        q1 = self.size // 4
        q3 = 3 * self.size // 4

        split1_end = self.start_index + half - 1
        split2_start = self.start_index + q1
        split2_end = self.start_index + q3 - 1
        split3_start = split1_end + 1

        return (
            EntityData(self.entity_type, self.start_index, split1_end, split=False),
            EntityData(self.entity_type, split2_start, split2_end, split=False),
            EntityData(self.entity_type, split3_start, self.end_index, split=False),
        )


MODEL_NAMES = ["dd_model", "midplane_model", "3d_model"]

PREDICATE_DATA = {
    "dd_model": [
        EntityData("N", 1, 804),
        EntityData("T", 1, 1604, split=False),
        EntityData("STL", 1, 1, split=False),
    ],
    "midplane_model": [EntityData("N", 1, 397), EntityData("T", 1, 718, split=False)],
    "3d_model": [
        EntityData("N", 805, 3333),
        EntityData("TE", 1, 12605, split=False),
        EntityData("STL", 1, 1, split=False),
    ],
}

# Property predicate constants

TEST_PROPERTY_TYPE = 1
TEST_PROPERTY_ID = 1

PROPERTY_PREDICATE_TEST_DATA = {model: {"size": 0, "converted_string": ""} for model in MODEL_NAMES}

PROPERTY_TYPE_PREDICATE_TEST_DATA = {
    model: {"size": 0, "converted_string": ""} for model in MODEL_NAMES
}

# Thickness predicate expected values

TEST_MIN_THICKNESS = 0.1
TEST_MAX_THICKNESS = 10.0

THICKNESS_PREDICATE_TEST_DATA = {
    model: {"size": 0, "converted_string": ""} for model in MODEL_NAMES
}

# X-section predicate expected values

X_SECTION_PREDICATE_TEST_DATA_LIST = [
    (CrossSectionType.CIRCULAR, [5.0], [10.0]),
    (CrossSectionType.RECTANGULAR, [2.0, 3.0], [4.0, 5.0]),
    (CrossSectionType.ANNULAR, [5.0, 3.0], [6.0, 4.0]),
    (CrossSectionType.HALF_CIRCULAR, [5.0, 3.0], [10.0, 4.0]),
    (CrossSectionType.U_SHAPE, [2.0, 3.0], [4.0, 5.0]),
    (CrossSectionType.TRAPEZOIDAL, [2.0, 3.0, 4.0], [4.0, 5.0, 6.0]),
]

X_SECTION_PREDICATE_TEST_DATA = {
    model: {
        cs_type.value: {
            "min_value": min_vals,
            "max_value": max_vals,
            "size": 0,
            "converted_string": "",
        }
        for cs_type, min_vals, max_vals in X_SECTION_PREDICATE_TEST_DATA_LIST
    }
    for model in MODEL_NAMES
}
