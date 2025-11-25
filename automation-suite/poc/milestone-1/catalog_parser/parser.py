
import json
from jsonschema import validate
from models import Catalog, FunctionalPackage, OsPackage, InfrastructurePackage, Driver


def ParseCatalog(file_path: str, schema_path: str = "resources/CatalogSchema.json") -> Catalog:
    with open(schema_path) as f:
        schema = json.load(f)
    with open(file_path) as f:
        catalog_json = json.load(f)

    validate(instance=catalog_json, schema=schema)
    data = catalog_json["Catalog"]

    functional_packages = [
        FunctionalPackage(
            id=key,
            name=pkg["Name"],
            version=pkg.get("Version", ""),
            supported_os=[f"{os['Name']} {os['Version']}" for os in pkg["SupportedOS"]],
            uri="",
            type=pkg["Type"],
            architecture=pkg["Architecture"],
            tag=pkg.get("Tag", ""),
            sources=pkg.get("Sources", []),
        )
        for key, pkg in data["FunctionalPackages"].items()
    ]

    os_packages = [
        OsPackage(
            id=key,
            name=pkg["Name"],
            version=pkg.get("Version", ""),
            supported_os=[f"{os['Name']} {os['Version']}" for os in pkg["SupportedOS"]],
            uri="",
            architecture=pkg["Architecture"],
            sources=pkg.get("Sources", []),
            type=pkg["Type"],
            tag=pkg.get("Tag", ""),
        )
        for key, pkg in data["OSPackages"].items()
    ]

    infrastructure_packages = [
        InfrastructurePackage(
            id=key,
            name=pkg["Name"],
            version=pkg["Version"],
            uri="",
            architecture=[],
            config=pkg["SupportedFunctions"],
            type=pkg["Type"],
            sources=[],
            tag=pkg.get("Tag", ""),
        )
        for key, pkg in data["InfrastructurePackages"].items()
    ]

    driver_packages = data.get("DriverPackages", {})
    drivers = [
        Driver(
            id=key,
            name=drv["Name"],
            version=drv["Version"],
            uri=drv["Uri"],
            architecture=drv["Architecture"],
            config=drv["Config"],
            type=drv["Type"],
        )
        for key, drv in driver_packages.items()
    ]

    catalog = Catalog(
        name=data["Name"],
        version=data["Version"],
        functional_layer=data["FunctionalLayer"],
        base_os=data["BaseOS"],
        infrastructure=data["Infrastructure"],
        drivers_layer=data.get("Drivers", []),
        drivers=drivers,
        functional_packages=functional_packages,
        os_packages=os_packages,
        infrastructure_packages=infrastructure_packages,
        miscellaneous=data.get("Miscellaneous", []),
    )

    return catalog
