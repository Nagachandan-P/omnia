import logging

from generator import generate_root_json_from_catalog
from adapter import generate_omnia_json_from_catalog

try:
    generate_root_json_from_catalog(
        catalog_path="test_fixtures/catalog_rhel.json",
        schema_path="resources/CatalogSchema.json",
        output_root="out/generator2",
        configure_logging=True,
        log_file="logs/generator.log",
        log_level=logging.INFO,
    )

    generate_omnia_json_from_catalog(
        catalog_path="test_fixtures/catalog_rhel.json",
        schema_path="resources/CatalogSchema.json",
        output_root="out/adapter/config2",
        configure_logging=True,
        log_file="logs/adapter.log",
        log_level=logging.INFO,
    )
except FileNotFoundError as e:
    # handle missing catalog/schema
    print(f"Missing file: {e}")
except Exception as e:
    # handle generic processing errors
    print(f"Processing failed: {e}")