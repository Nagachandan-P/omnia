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

"""Example script showing programmatic usage of the generator and adapter APIs.

This script runs the catalog feature-list generator and adapter config generator
directly from Python, configuring logging and handling common errors.
"""

import logging
import os

from catalog_parser.generator import generate_root_json_from_catalog, get_functional_layer_roles_from_file
from catalog_parser.adapter import generate_omnia_json_from_catalog

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CATALOG_PARSER_DIR = os.path.join(BASE_DIR, "")
CATALOG_PATH = os.path.join(CATALOG_PARSER_DIR, "test_fixtures", "catalog_rhel.json")
SCHEMA_PATH = os.path.join(CATALOG_PARSER_DIR, "resources", "CatalogSchema.json")
FUNCTIONAL_LAYER_PATH = os.path.join(CATALOG_PARSER_DIR, "test_fixtures", "functional_layer.json")

try:
    generate_root_json_from_catalog(
        catalog_path=CATALOG_PATH,
        schema_path=SCHEMA_PATH,
        output_root="out/generator2",
        configure_logging=True,
        log_file="logs/generator.log",
        log_level=logging.INFO,
    )

    generate_omnia_json_from_catalog(
        catalog_path=CATALOG_PATH,
        schema_path=SCHEMA_PATH,
        output_root="out/adapter/config2",
        configure_logging=True,
        log_file="logs/adapter.log",
        log_level=logging.INFO,
    )

    roles = get_functional_layer_roles_from_file(FUNCTIONAL_LAYER_PATH)
    print(f"Functional layer roles: {roles}")
except FileNotFoundError as e:
    # handle missing catalog/schema
    print(f"Missing file: {e}")
except Exception as e:
    # handle generic processing errors
    print(f"Processing failed: {e}")