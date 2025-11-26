| Code | Name                      | When it happens                                                                 |
|------|---------------------------|---------------------------------------------------------------------------------|
| 0    | SUCCESS                   | All processing completed successfully.                                         |
| 2    | ERROR_CODE_INPUT_NOT_FOUND | Required input file is missing (catalog, schema, or a file needed during processing). |
| 3    | ERROR_CODE_PROCESSING_ERROR | Any other unexpected runtime error while parsing or generating outputs.       |

## Usage

### Catalog Parser CLI (`generator.py`)

Generates per-arch/OS/version feature-list JSONs (functional layer, infra, drivers, base OS, miscellaneous).

```bash
python generator.py \
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

```bash
python adapter.py \
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
