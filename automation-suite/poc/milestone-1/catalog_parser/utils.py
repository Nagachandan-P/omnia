# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for the catalog parser package."""

import json
from typing import Any


def load_json_file(file_path: str) -> Any:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file to load.

    Returns:
        The parsed JSON data (dict, list, or other JSON-compatible type).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)
