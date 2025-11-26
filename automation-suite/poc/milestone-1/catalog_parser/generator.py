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

import json
import os
import argparse
import logging
from models import Catalog
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# This code generates JSON files
# i.e baseos.json, infrastructure.json, functional_layer.json, miscellaneous.json
# for a given catalog

def _arch_suffix(architecture) -> str:
    """Return a single-arch suffix from a catalog Package.architecture field.

    Handles both legacy string values and new List[str] values.
    """
    if isinstance(architecture, list):
        if not architecture:
            return ""
        arch = architecture[0]
    else:
        arch = architecture
    return str(arch)

@dataclass
class Package:
    package: str
    type: str
    repo_name: str
    architecture: List[str]
    uri: Optional[str] = None
    tag: Optional[str] = None
    sources: Optional[List[dict]] = None

@dataclass
class Feature:
    feature_name: str
    packages: List[Package]

@dataclass
class FeatureList:
    features: Dict[str, Feature]

def _filter_featurelist_for_arch(feature_list: FeatureList, arch: str) -> FeatureList:
    """Return a FeatureList containing only packages for the given arch.

    Arch is taken from the Package.architecture list.
    """
    filtered_features: Dict[str, Feature] = {}
    for name, feature in feature_list.features.items():
        narrowed_pkgs: List[Package] = []
        for p in feature.packages:
            if arch in getattr(p, "architecture", []):
                # Derive repo_name and uri from the catalog Sources metadata, if
                # present, for this specific architecture.
                repo_name = ""
                uri = getattr(p, "uri", None)
                if getattr(p, "sources", None):
                    for src in p.sources:
                        if src.get("Architecture") == arch:
                            if "RepoName" in src:
                                repo_name = src["RepoName"]
                            if "Uri" in src:
                                uri = src["Uri"]
                            break

                narrowed_pkgs.append(
                    Package(
                        package=p.package,
                        type=p.type,
                        repo_name=repo_name,
                        architecture=[arch],
                        uri=uri,
                        tag=p.tag,
                        sources=p.sources,
                    )
                )
        filtered_features[name] = Feature(feature_name=name, packages=narrowed_pkgs)
    return FeatureList(features=filtered_features)

def _discover_arch_os_version_from_catalog(catalog: Catalog) -> List[Tuple[str, str, str]]:
    """Discover distinct (arch, os_name, version) combinations in the Catalog.

    os_name is returned in lowercase (e.g. "rhel"), version as-is.
    """

    combos: set[Tuple[str, str, str]] = set()

    def _add_from_packages(packages):
        for pkg in packages:
            for os_entry in pkg.supported_os:
                parts = os_entry.split(" ", 1)
                if len(parts) == 2:
                    os_name_raw, os_ver = parts
                else:
                    os_name_raw, os_ver = os_entry, ""
                os_name = os_name_raw.lower()

                for arch in pkg.architecture:
                    combos.add((arch, os_name, os_ver))

    _add_from_packages(catalog.functional_packages)
    _add_from_packages(catalog.os_packages)

    combos_sorted = sorted(combos)
    logger.debug(
        "Discovered %d (arch, os, version) combinations in catalog %s",
        len(combos_sorted),
        getattr(catalog, "name", "<unknown>"),
    )
    return combos_sorted

def generate_functional_layer_json(catalog: Catalog) -> FeatureList:
    """
    Generates a JSON file containing the functional layer from a given catalog object.

    Args:
    - catalog (Catalog): The catalog object to generate the functional layer from.

    Returns:
    - FeatureList: The generated JSON data
    """
    output_json = FeatureList(features={})
    
    for layer in catalog.functional_layer:
        feature_json = Feature(
            feature_name=layer["Name"],
            packages=[]
        )
        
        for pkg_id in layer["FunctionalPackages"]:
            pkg = next((pkg for pkg in catalog.functional_packages if pkg.id == pkg_id), None)
            if pkg:
                feature_json.packages.append(
                    Package(
                        package=pkg.name,
                        type=pkg.type,
                        repo_name="",
                        architecture=pkg.architecture,
                        uri=None,
                        tag=getattr(pkg, "tag", None),
                        sources=pkg.sources,
                    )
                )
        
        output_json.features[feature_json.feature_name] = feature_json
    
    return output_json

def generate_infrastructure_json(catalog: Catalog) -> FeatureList:
    """
    Generates a JSON file containing the infrastructure from a given catalog object.

    Args:
    - catalog (Catalog): The catalog object to generate the infrastructure from.

    Returns:
    - FeatureList: The generated JSON data
    """
    output_json = FeatureList(features={})
    
    for infra in catalog.infrastructure:
        feature_json = Feature(
            feature_name=infra["Name"],
            packages=[]
        )
        
        for pkg_id in infra["InfrastructurePackages"]:
            pkg = next((pkg for pkg in catalog.infrastructure_packages if pkg.id == pkg_id), None)
            if pkg:
                feature_json.packages.append(
                    Package(
                        package=pkg.name,
                        type=pkg.type,
                        repo_name="",
                        architecture=pkg.architecture,
                        uri=None,
                        tag=getattr(pkg, "tag", None),
                        sources=pkg.sources,
                    )
                )
        
        output_json.features[feature_json.feature_name] = feature_json
    
    return output_json

def generate_drivers_json(catalog: Catalog) -> FeatureList:
    """
    Generates a JSON file containing the drivers from a given catalog object.

    Args:
    - catalog (Catalog): The catalog object to generate the drivers from.

    Returns:
    - FeatureList: The generated JSON data
    """
    output_json = FeatureList(features={})

    # Map driver package IDs -> Driver objects parsed from DriverPackages.
    drivers_by_id: Dict[str, any] = {drv.id: drv for drv in catalog.drivers}

    # If no grouping is present (backward compatibility), fall back to a single
    # "Drivers" feature containing all drivers.
    if not getattr(catalog, "drivers_layer", []):
        feature_json = Feature(
            feature_name="Drivers",
            packages=[]
        )
        for driver in catalog.drivers:
            feature_json.packages.append(
                Package(
                    package=driver.name,
                    type=driver.type,
                    repo_name="",
                    architecture=driver.architecture,
                    uri=None,
                    tag=None,
                    sources=None,
                )
            )
        output_json.features[feature_json.feature_name] = feature_json
        return output_json

    # Respect grouping similar to FunctionalLayer: one Feature per driver group.
    for group in catalog.drivers_layer:
        group_name = group.get("Name")
        driver_ids = group.get("DriverPackages", [])
        if not group_name or not driver_ids:
            continue

        feature_json = Feature(
            feature_name=group_name,
            packages=[]
        )

        for driver_id in driver_ids:
            driver = drivers_by_id.get(driver_id)
            if not driver:
                continue

            feature_json.packages.append(
                Package(
                    package=driver.name,
                    type=driver.type,
                    repo_name="",
                    architecture=driver.architecture,
                    uri=None,
                    tag=None,
                    sources=None,
                )
            )

        output_json.features[feature_json.feature_name] = feature_json

    return output_json

def generate_base_os_json(catalog: Catalog) -> FeatureList:
    """
    Generates a JSON file containing the base OS from a given catalog object.

    Args:
    - catalog (Catalog): The catalog object to generate the base OS from.

    Returns:
    - FeatureList: The generated JSON data
    """
    output_json = FeatureList(features={})
    
    feature_json = Feature(
        feature_name="Base OS",
        packages=[]
    )
    
    for entry in catalog.base_os:
        for pkg_id in entry["osPackages"]:
            pkg = next((pkg for pkg in catalog.os_packages if pkg.id == pkg_id), None)
            if pkg:
                feature_json.packages.append(
                    Package(
                        package=pkg.name,
                        type=pkg.type,
                        repo_name="",
                        architecture=pkg.architecture,
                        uri=None,
                        tag=getattr(pkg, "tag", None),
                        sources=pkg.sources,
                    )
                )
    
    output_json.features[feature_json.feature_name] = feature_json
    
    return output_json

def generate_miscellaneous_json(catalog: Catalog) -> FeatureList:
    """Generate a FeatureList for the Miscellaneous group, if present.

    The catalog is expected to carry a Miscellaneous array of package IDs,
    referencing FunctionalPackages. This creates a single feature named
    "Miscellaneous" containing those packages.
    """
    output_json = FeatureList(features={})

    feature_json = Feature(
        feature_name="Miscellaneous",
        packages=[],
    )

    misc_ids = getattr(catalog, "miscellaneous", [])
    for pkg_id in misc_ids:
        pkg = next((pkg for pkg in catalog.functional_packages if pkg.id == pkg_id), None)
        if not pkg:
            continue

        feature_json.packages.append(
            Package(
                package=pkg.name,
                type=pkg.type,
                repo_name="",
                architecture=pkg.architecture,
                uri=None,
                tag=getattr(pkg, "tag", None),
                sources=pkg.sources,
            )
        )

    output_json.features[feature_json.feature_name] = feature_json

    return output_json

def _package_common_dict(pkg: Package) -> Dict:
    """Common dict representation for a Package (no architecture).

    Shared between generator and adapter to keep JSON field formatting
    consistent for package, type, repo_name, uri, and tag.
    """
    data: Dict = {"package": pkg.package, "type": pkg.type}
    if getattr(pkg, "repo_name", ""):
        data["repo_name"] = pkg.repo_name
    if getattr(pkg, "uri", None) is not None:
        data["uri"] = pkg.uri
    if getattr(pkg, "tag", "") and pkg.tag != "":
        data["tag"] = pkg.tag
    return data


def _package_to_json_dict(pkg: Package) -> Dict:
    data = _package_common_dict(pkg)
    data["architecture"] = pkg.architecture
    return data


def _package_from_json_dict(data: Dict) -> Package:
    return Package(
        package=data["package"],
        type=data["type"],
        repo_name=data.get("repo_name", ""),
        architecture=data.get("architecture", []),
        uri=data.get("uri"),
        tag=data.get("tag"),
    )


def serialize_json(feature_list: FeatureList, output_path: str):
    """
    Serializes the output JSON data to a file.

    Args:
    - feature_list (FeatureList): The feature list data to serialize.
    - output_path (str): The path to write the serialized JSON file to.
    """
    # Custom pretty-printer so that:
    #   - Overall JSON is nicely indented
    #   - Each package entry inside "packages" is a single-line JSON object
    logger.info(
        "Writing FeatureList with %d feature(s) to %s",
        len(feature_list.features),
        output_path,
    )
    with open(output_path, "w") as f:
        f.write("{\n")

        items = list(feature_list.features.items())
        for i, (feature_name, feature) in enumerate(items):
            # Feature key
            f.write(f"  {json.dumps(feature_name)}: {{\n")
            f.write("    \"packages\": [\n")

            pkgs = feature.packages
            for j, pkg in enumerate(pkgs):
                pkg_dict = _package_to_json_dict(pkg)
                line = "      " + json.dumps(pkg_dict, separators=(", ", ": "))
                if j < len(pkgs) - 1:
                    line += ","
                f.write(line + "\n")

            f.write("    ]\n")
            f.write("  }")
            if i < len(items) - 1:
                f.write(",\n")
            else:
                f.write("\n")

        f.write("}\n")


def deserialize_json(input_path: str) -> FeatureList:
    """
    Deserializes a JSON file to output JSON data.

    Args:
    - input_path (str): The path to read the JSON file from.

    Returns:
    - FeatureList: The deserialized JSON data
    """
    with open(input_path, "r") as f:
        json_data = json.load(f)

    logger.debug("Deserializing FeatureList from %s", input_path)
    
    feature_list = FeatureList(
        features={
            feature_name: Feature(
                feature_name=feature_name,
                packages=[
                    _package_from_json_dict(pkg)
                    for pkg in feature_body.get("packages", [])
                ]
            )
            for feature_name, feature_body in json_data.items()
        }
    )
    
    logger.info("Deserialized FeatureList with %d feature(s) from %s", len(feature_list.features), input_path)

    return feature_list


if __name__ == "__main__":
    # Example usage: generate per-arch/OS/version FeatureList JSONs under
    # out/<arch>/<os_name>/<version>/
    from parser import ParseCatalog

    parser = argparse.ArgumentParser(description='Catalog Parser CLI')
    parser.add_argument('--catalog', required=True, help='Path to input catalog JSON file')
    parser.add_argument('--schema', required=False, default='resources/CatalogSchema.json', help='Path to catalog schema JSON file')
    parser.add_argument('--log-file', required=False, default=None, help='Path to log file; if not set, logs go to stderr')
    args = parser.parse_args()

    if args.log_file:
        log_dir = os.path.dirname(args.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=args.log_file,
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    logger.info("Catalog Parser CLI started for %s", args.catalog)

    catalog = ParseCatalog(args.catalog, args.schema)

    functional_layer_json = generate_functional_layer_json(catalog)
    infrastructure_json = generate_infrastructure_json(catalog)
    drivers_json = generate_drivers_json(catalog)
    base_os_json = generate_base_os_json(catalog)
    miscellaneous_json = generate_miscellaneous_json(catalog)

    combos = _discover_arch_os_version_from_catalog(catalog)
    logger.info("Discovered %d combination(s) for feature-list generation", len(combos))

    for arch, os_name, version in combos:
        base_dir = os.path.join('out', "main", arch, os_name, version)
        os.makedirs(base_dir, exist_ok=True)

        logger.info(
            "Generating feature-list JSONs for arch=%s os=%s version=%s into %s",
            arch,
            os_name,
            version,
            base_dir,
        )

        func_arch = _filter_featurelist_for_arch(functional_layer_json, arch)
        infra_arch = _filter_featurelist_for_arch(infrastructure_json, arch)
        drivers_arch = _filter_featurelist_for_arch(drivers_json, arch)
        base_os_arch = _filter_featurelist_for_arch(base_os_json, arch)
        misc_arch = _filter_featurelist_for_arch(miscellaneous_json, arch)

        serialize_json(func_arch, os.path.join(base_dir, 'functional_layer.json'))
        serialize_json(infra_arch, os.path.join(base_dir, 'infrastructure.json'))
        serialize_json(drivers_arch, os.path.join(base_dir, 'drivers.json'))
        serialize_json(base_os_arch, os.path.join(base_dir, 'base_os.json'))
        serialize_json(misc_arch, os.path.join(base_dir, 'miscellaneous.json'))

    logger.info("Catalog Parser CLI completed for %s", args.catalog)