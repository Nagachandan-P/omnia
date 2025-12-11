import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
CATALOG_PARSER_DIR = os.path.dirname(HERE)
PROJECT_ROOT = os.path.dirname(CATALOG_PARSER_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from catalog_parser.generator import generate_root_json_from_catalog, _DEFAULT_SCHEMA_PATH


class TestGeneratorDefaults(unittest.TestCase):
    def test_default_schema_path_points_to_resources(self):
        catalog_parser_dir = os.path.dirname(os.path.dirname(__file__))
        expected_schema = os.path.join(catalog_parser_dir, "resources", "CatalogSchema.json")
        self.assertEqual(os.path.abspath(_DEFAULT_SCHEMA_PATH), os.path.abspath(expected_schema))

    def test_generate_root_json_with_defaults_writes_output(self):
        catalog_parser_dir = os.path.dirname(os.path.dirname(__file__))
        catalog_path = os.path.join(catalog_parser_dir, "test_fixtures", "catalog_rhel.json")

        with tempfile.TemporaryDirectory() as tmpdir:
            generate_root_json_from_catalog(
                catalog_path=catalog_path,
                output_root=tmpdir,
            )

            # We expect at least one arch/os/version directory with functional_layer.json
            found = False
            for root, dirs, files in os.walk(tmpdir):
                if "functional_layer.json" in files:
                    found = True
                    break

            self.assertTrue(found, "functional_layer.json not generated under any arch/os/version")


if __name__ == "__main__":
    unittest.main()
