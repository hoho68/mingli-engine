from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata, resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Iterator


_DISTRIBUTION_NAME = "mingli-engine"
_REQUIRED_RUNTIME_ASSETS = frozenset(
    {
        "data/calculation/school_profiles.json",
        "data/calculation/strength_weights.json",
        "data/classical_sources/evidence_units.json",
    }
)


@dataclass(frozen=True)
class PackagingVerification:
    asset_sha256: dict[str, str]
    distribution_version: str
    source_isolated: bool
    overall_status: str


def _iter_json_assets(
    directory: Traversable,
    relative_directory: str,
) -> Iterator[tuple[str, bytes]]:
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        relative_path = f"{relative_directory}/{child.name}"
        if child.is_dir():
            yield from _iter_json_assets(child, relative_path)
        elif child.is_file() and child.name.endswith(".json"):
            yield relative_path, child.read_bytes()


def build_packaging_verification() -> PackagingVerification:
    package_root = resources.files("mingli_engine")
    assets = {
        relative_path: sha256(payload).hexdigest()
        for relative_path, payload in _iter_json_assets(
            package_root.joinpath("data"),
            "data",
        )
    }

    try:
        distribution = metadata.distribution(_DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError:
        distribution_version = "not_installed"
        source_isolated = False
    else:
        distribution_version = distribution.version
        installed_package_root = Path(
            str(distribution.locate_file("mingli_engine"))
        ).resolve()
        source_isolated = Path(__file__).resolve().parent == installed_package_root

    verified = (
        bool(assets)
        and _REQUIRED_RUNTIME_ASSETS.issubset(assets)
        and distribution_version != "not_installed"
        and source_isolated
    )
    return PackagingVerification(
        asset_sha256=assets,
        distribution_version=distribution_version,
        source_isolated=source_isolated,
        overall_status="verified" if verified else "failed",
    )
