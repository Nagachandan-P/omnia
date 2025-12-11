import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
CATALOG_PARSER_DIR = os.path.dirname(HERE)
PROJECT_ROOT = os.path.dirname(CATALOG_PARSER_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from catalog_parser.generator import (
    FeatureList,
    serialize_json,
    get_functional_layer_roles_from_file,
)


class TestGetFunctionalLayerRolesFromFile(unittest.TestCase):
    def test_returns_all_role_names_from_fixture(self):
        base_dir = os.path.dirname(__file__)
        fixture_path = os.path.abspath(
            os.path.join(base_dir, "..", "test_fixtures", "functional_layer.json")
        )

        roles = get_functional_layer_roles_from_file(fixture_path)

        expected_roles = [
            "Compiler",
            "K8S Controller",
            "K8S Worker",
            "Login Node",
            "Slurm Controller",
            "Slurm Worker",
            "service_etcd",
        ]

        self.assertCountEqual(roles, expected_roles)

    def test_empty_feature_list_returns_empty_roles(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            empty_feature_list = FeatureList(features={})
            json_path = os.path.join(tmp_dir, "functional_layer.json")
            serialize_json(empty_feature_list, json_path)

            roles = get_functional_layer_roles_from_file(json_path)

            self.assertEqual(roles, [])


if __name__ == "__main__":
    unittest.main()
