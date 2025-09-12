# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""Localization Constants for Moldflow API."""

import winreg
import os

# Constants for color bands
COLOR_BAND_RANGE = tuple(range(1, 257))

# Localization constants
DEFAULT_THREE_LETTER_CODE = "enu"
LOCALE_FILE_NAME = "locale"
MOLDFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALE_DIR = os.path.join(MOLDFLOW_DIR, "locale")

# Registry constants
USER_LOCALE_KEY = winreg.HKEY_CURRENT_USER
DEFAULT_LOCALE_KEY = winreg.HKEY_LOCAL_MACHINE
LOCALE_LOCATION = "SOFTWARE\\Autodesk\\{product_name}\\{version}\\Environment"

# Environment variable constants
LOCALE_ENVIRONMENT_VARIABLE_NAME = "MFSYN_LOCALE"
LOCALE_REGISTRY_VARIABLE_NAME = "MFSYN_LOCALE"

# BCP-47 standard constants
THREE_LETTER_TO_BCP_47 = {
    "chs": "zh-CN",
    "cht": "zh-TW",
    "deu": "de-DE",
    "enu": "en-US",
    "esn": "es-ES",
    "fra": "fr-FR",
    "ita": "it-IT",
    "jpn": "ja-JP",
    "kor": "ko-KR",
    "ptg": "pt-PT",
}
DEFAULT_BCP_47_STD = THREE_LETTER_TO_BCP_47[DEFAULT_THREE_LETTER_CODE]

# Logging Constants
DEFAULT_LOG_FILE = 'moldflow.log'

# File Types
UDM_FILE_EXT = ".udm"
XML_FILE_EXT = ".xml"
ELE_FILE_EXT = ".ele"
STL_FILE_EXT = ".stl"
TXT_FILE_EXT = ".txt"
FBX_FILE_EXT = ".fbx"
CAD_FILE_EXT = ".cad"
SDZ_FILE_EXT = ".sdz"
PNG_FILE_EXT = ".png"
JPG_FILE_EXT = ".jpg"
JPEG_FILE_EXT = ".jpeg"
BMP_FILE_EXT = ".bmp"
TIF_FILE_EXT = ".tif"
MP4_FILE_EXT = ".mp4"
