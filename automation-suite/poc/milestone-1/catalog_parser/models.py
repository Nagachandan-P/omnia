# models.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Package:
    id: str
    name: str
    version: str
    supported_os: List[str]
    uri: str
    architecture: List[str]
    type: str
    tag: str = ""
    sources: Optional[List[dict]] = None

@dataclass
class FunctionalPackage(Package):
    pass

@dataclass
class OsPackage(Package):
    pass

@dataclass
class InfrastructurePackage:
    def __init__(self, id, name, version, uri, architecture, config, type, sources=None, tag=""):
        self.id = id
        self.name = name
        self.version = version
        self.uri = uri
        self.architecture = architecture
        self.config = config
        self.type = type
        self.sources = sources
        self.tag = tag

@dataclass
class Driver:
    def __init__(self, id, name, version, uri, architecture, config, type):
        self.id = id
        self.name = name
        self.version = version
        self.uri = uri
        self.architecture = architecture
        self.config = config
        self.type = type

@dataclass
class Catalog:
    name: str
    version: str
    functional_layer: List[dict]
    base_os: List[dict]
    infrastructure: List[dict]
    drivers_layer: List[dict]
    drivers: List[Driver]
    functional_packages: List[FunctionalPackage]
    os_packages: List[OsPackage]
    infrastructure_packages: List[InfrastructurePackage]
    miscellaneous: List[str]