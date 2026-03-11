# Catalog Processing

The Catalog workflow handles software catalog parsing and role generation for the Omnia platform.

## What It Does

The Catalog workflow provides:
- Software catalog parsing from JSON files
- Role generation based on catalog contents
- Package categorization and dependency resolution
- Integration with Ansible for role creation
- Validation of catalog structure and contents

## Inputs/Outputs

**Inputs:**
- Software catalog JSON files
- Package configuration mappings
- Role templates and definitions
- Platform-specific parameters

**Outputs:**
- Generated Ansible roles
- Package dependency mappings
- Validated catalog structures
- Role metadata and documentation

## Key Logic Locations

**Primary Files:**
- `api/catalog_roles/routes.py` - HTTP endpoints for catalog operations
- `api/parse_catalog/routes.py` - Catalog parsing endpoints
- `orchestrator/catalog/use_cases/parse_catalog.py` - Catalog parsing logic
- `orchestrator/catalog/use_cases/generate_input_files.py` - Input file generation
- `core/catalog/entities.py` - Catalog domain entities
- `core/catalog/repositories.py` - Catalog data access
- `generate_catalog.py` - Standalone catalog generation script

**Main Components:**
- **ParseCatalogUseCase** - Handles catalog parsing and validation
- **GenerateInputFilesUseCase** - Creates Ansible input files
- **CatalogRolesService** - Role generation and management
- **CatalogRepository** - Catalog data persistence

## Workflow Flow

1. **Catalog Upload**: Client submits catalog via `/api/v1/parse_catalog` endpoint
2. **Structure Validation**: Catalog schema and structure validated
3. **Package Parsing**: Individual packages extracted and categorized
4. **Dependency Resolution**: Package dependencies analyzed and resolved
5. **Role Generation**: Ansible roles generated based on packages
6. **Input File Creation**: Configuration files created for downstream workflows
7. **Validation**: Generated artifacts validated for completeness
8. **Storage**: Results stored in artifact repository

## Package Categorization

Packages are categorized into:
- **Functional Bundles**: Core service packages (service_k8s, slurm_custom, additional_packages)
- **Infrastructure Bundles**: CSI and infrastructure packages (csi_driver_powerscale)
- **Miscellaneous**: Additional packages that don't fit other categories

## Integration Points

- Feeds into local repository creation workflow
- Provides input for image building workflows
- Integrates with validation workflow for quality checks
- Uses Vault for secure access to package repositories

## Configuration

Catalog processing is configured through:
- Package mapping files
- Role templates
- Platform-specific configurations
- Validation rules and schemas

## Error Handling

- Comprehensive schema validation for catalogs
- Detailed error reporting for invalid packages
- Graceful handling of missing dependencies
- Rollback capabilities for failed processing

## Standalone Script

The `generate_catalog.py` script provides:
- Command-line catalog generation
- Batch processing capabilities
- Integration with external CI/CD pipelines
- Detailed logging and error reporting
