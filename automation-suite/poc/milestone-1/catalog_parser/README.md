| Code | Name                      | When it happens                                                                 |
|------|---------------------------|---------------------------------------------------------------------------------|
| 0    | SUCCESS                   | All processing completed successfully.                                         |
| 2    | ERROR_CODE_INPUT_NOT_FOUND | Required input file is missing (catalog, schema, or a file needed during processing). |
| 3    | ERROR_CODE_PROCESSING_ERROR | Any other unexpected runtime error while parsing or generating outputs.       |

## Usage

### Catalog Parser CLI (`generator.py`)

Generates per-arch/OS/version feature-list JSONs (functional layer, infra, drivers, base OS, miscellaneous).

From the `poc/milestone-1` directory, run the generator as a module:

```bash
python -m catalog_parser.generator \
  --catalog <path-to-catalog.json> \
  [--schema <path-to-schema.json>] \
  [--log-file <path-to-log-file>]
```

- `--catalog` (required): Path to input catalog JSON file.
- `--schema` (optional, default: `resources/CatalogSchema.json`): Path to catalog schema JSON file.
- `--log-file` (optional): Path to log file; if set, the directory is auto-created, otherwise logs go to stderr.

Outputs are written under:

```text
out/main/<arch>/<os_name>/<version>/
  functional_layer.json
  infrastructure.json
  drivers.json
  base_os.json
  miscellaneous.json
```

### Adapter Config Generator (`adapter.py`)

Generates adapter-style config JSONs from the catalog.

From the `poc/milestone-1` directory, run the adapter as a module:

```bash
python -m catalog_parser.adapter \
  --catalog <path-to-catalog.json> \
  [--schema <path-to-schema.json>] \
  [--log-file <path-to-log-file>]
```

- `--catalog` (required): Path to input catalog JSON file.
- `--schema` (optional, default: `resources/CatalogSchema.json`): Path to catalog schema JSON file.
- `--log-file` (optional): Path to log file; if set, the directory is auto-created, otherwise logs go to stderr.

Outputs are written under:

```text
out/adapter/input/config/<arch>/<os_name>/<version>/
  default_packages.json
  nfs.json / openldap.json / openmpi.json (if data)
  service_k8s.json
  slurm_custom.json
  <infra-feature>.json ...
```

### Programmatic usage

You can also call both components directly from Python without going through the CLI.

#### Catalog Parser API (`generator.py`)

Programmatic entry point:

- `generate_root_json_from_catalog(catalog_path, schema_path="resources/CatalogSchema.json", output_root="out/generator", *, log_file=None, configure_logging=False, log_level=logging.INFO)`

Behavior:

- Optionally configures logging when `configure_logging=True` (and will create the log directory if needed).
- Writes per-arch/OS/version feature-list JSONs under `output_root/<arch>/<os>/<version>/`.

#### Adapter Config API (`adapter.py`)

Programmatic entry point:

- `generate_omnia_json_from_catalog(catalog_path, schema_path="resources/CatalogSchema.json", output_root="out/adapter/input/config", *, log_file=None, configure_logging=False, log_level=logging.INFO)`

Behavior:

- Optionally configures logging when `configure_logging=True` (and will create the log directory if needed).
- Writes adapter-style config JSONs under `output_root/<arch>/<os>/<version>/`.

#### Sample code

Example Python code showing how to call these APIs programmatically is available in:

- `tests/sample.py`
