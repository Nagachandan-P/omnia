# Adapter Policy Guide

This guide explains how to write the **adapter policy file** (`adapter_policy_default.json`) to generate adapter config JSONs.

The adapter policy file lets you:

- Pull one or more **roles** (top-level keys) from one or more **source JSON files** into a **target JSON file**.
- Optionally **rename** roles while pulling.
- Optionally **filter** packages while pulling (currently substring match).
- Create a **derived role** that contains **common packages** across multiple roles.
- Remove those common packages from the source roles so packages do not appear twice.

---

## 1. What the generator expects

### 1.1 Source files

The generator reads source files from the `--input-dir` directory, for each architecture/OS/version:

```text
<input-dir>/<arch>/<os_family>/<os_version>/
  base_os.json
  functional_layer.json
  infrastructure.json
  miscellaneous.json
  ...
```

Each source file is expected to be an object where each top-level key is a **role** or **feature**, e.g. `"K8S Controller"`, `"K8S Worker"`, etc.

Each role has a `packages` list:

```json
{
  "K8S Controller": {
    "packages": [
      {"package": "kubeadm-v1.31.4-amd64", "type": "tarball", "uri": "..."}
    ]
  }
}
```

### 1.2 Output files

The mapping adapter writes target files under `--output-dir`:

```text
<output-dir>/<arch>/<os_family>/<os_version>/
  service_k8s.json
  slurm_custom.json
  default_packages.json
  ...
```

Each target file is an object of roles where each role contains a `cluster` list:

```json
{
  "service_kube_node": {
    "cluster": [
      {"package": "vim", "type": "rpm", "repo_name": "x86_64_appstream"}
    ]
  }
}
```

---

## 2. Adapter policy file structure

The adapter policy file is a JSON object with this shape:

- `version`: schema version (use `"2.0.0"`)
- `description`: human-readable
- `targets`: mapping of **target filename** -> **target specification**

At a high level:

```json
{
  "version": "2.0.0",
  "description": "...",
  "targets": {
    "service_k8s.json": {
      "transform": {"exclude_fields": ["architecture"]},
      "sources": [ ... ],
      "derived": [ ... ]
    }
  }
}
```

---

## 3. Target spec

A target spec describes how to build a single target file.

### 3.1 `transform` (optional)

Applied to all packages written in this target, unless overridden per pull.

Currently supported:

- `exclude_fields`: removes keys from each package object (commonly `architecture`).
- `rename_fields`: renames keys inside each package object.

### 3.2 `sources` (required)

A list of source specs. Each source spec pulls one or more roles from a single source file.

Each `source` has:

- `source_file`: e.g. `functional_layer.json`
- `pulls`: list of roles to pull

Each `pull` has:

- `source_key`: the role name in the source file
- `target_key` (optional): rename the role in the output. If omitted, the role name is unchanged.
- `filter` (optional): filter packages while pulling
- `transform` (optional): per-role transform override

### 3.3 `derived` (optional)

Defines derived roles that are computed from roles already pulled into the target.

Currently supported derived operation:

- `extract_common`
  - Computes packages that appear in `min_occurrences` or more of the `from_keys` roles
  - Writes them into `target_key`
  - If `remove_from_sources=true`, those common packages are removed from each role in `from_keys`

---

## 4. Fully worked example: `service_k8s.json`

Goal:

- Pull two roles from `functional_layer.json`
  - `K8S Controller` -> `service_kube_control_plane`
  - `K8S Worker` -> `service_kube_node`
- Derive a new role called `service_k8s` containing packages common to both pulled roles
- Remove those common packages from `service_kube_control_plane` and `service_kube_node`

```json
{
  "version": "2.0.0",
  "description": "Example mapping: build service_k8s.json from functional_layer.json",
  "targets": {
    "service_k8s.json": {
      "transform": {
        "exclude_fields": ["architecture"]
      },
      "sources": [
        {
          "source_file": "functional_layer.json",
          "pulls": [
            {
              "source_key": "K8S Controller",
              "target_key": "service_kube_control_plane"
            },
            {
              "source_key": "K8S Worker",
              "target_key": "service_kube_node"
            }
          ]
        }
      ],
      "derived": [
        {
          "target_key": "service_k8s",
          "operation": {
            "type": "extract_common",
            "from_keys": ["service_kube_control_plane", "service_kube_node"],
            "min_occurrences": 2,
            "remove_from_sources": true
          }
        }
      ]
    }
  }
}
```

Resulting output file (`service_k8s.json`) will contain:

- `service_kube_control_plane`: only control-plane-unique packages
- `service_kube_node`: only node-unique packages
- `service_k8s`: the common packages extracted from both

---

## 5. Example: substring filtering (e.g., `nfs.json`)

Goal:

- Pull `Base OS` packages from `base_os.json`
- Only keep packages whose `package` contains substring `"nfs"`

```json
{
  "version": "2.0.0",
  "description": "Example mapping: build nfs.json from base_os.json",
  "targets": {
    "nfs.json": {
      "transform": {
        "exclude_fields": ["architecture"]
      },
      "sources": [
        {
          "source_file": "base_os.json",
          "pulls": [
            {
              "source_key": "Base OS",
              "target_key": "nfs",
              "filter": {
                "type": "substring",
                "field": "package",
                "values": ["nfs"],
                "case_sensitive": false
              }
            }
          ]
        }
      ]
    }
  }
}
```

---


## 6. Tips and common mistakes

- **Role names must match exactly**: `source_key` must exist in the source JSON.
- **Derived roles operate on target role names**: `from_keys` refers to the names after renaming (`target_key`).
- If you set `remove_from_sources=true`, verify you included the right keys in `from_keys`.
- Filters apply *before* transforms.
