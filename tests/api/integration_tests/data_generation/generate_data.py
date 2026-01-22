# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Script to generate data for integration tests.

Usage:
    generate_data.py [<markers>...]
"""

import docopt
import sys
from tests.api.integration_tests.data_generation.generate_data_helper import (
    clean_up_temp_files,
    get_generate_data_functions,
    get_available_markers,
    fetch_data_on_markers,
)
from tests.api.integration_tests.data_generation.generate_data_logger import generate_data_logger
from tests.api.integration_tests.conftest import get_study_files


def main():
    """Main entry point for this script"""
    args = docopt.docopt(__doc__)

    try:
        markers = args.get('<markers>') or []
        get_study_files()
        generate_functions = get_generate_data_functions()

        for marker in markers:
            if marker not in generate_functions.keys():
                generate_data_logger.error(f'Invalid marker: {marker}')
                generate_data_logger.error(get_available_markers(generate_functions))
                return 0

        if len(markers) > 0:
            fetch_data_on_markers(markers, generate_functions)
        else:
            fetch_data_on_markers(generate_functions.keys(), generate_functions)

    except Exception as err:
        generate_data_logger.error(f'FAILURE: {err}')
        clean_up_temp_files()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
