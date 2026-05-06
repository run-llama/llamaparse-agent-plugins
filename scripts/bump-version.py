#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
import json
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, NamedTuple

PLUGINS_PATH = Path("plugins/")
PLUGIN_FILE = ".codex-plugin/plugin.json"

BumpType = Literal["patch", "minor", "major"]


class Version(NamedTuple):
    major: int
    minor: int
    patch: int


def _parse_semver(version: str) -> Version:
    sep = version.split(".")
    assert len(sep) == 3
    assert all(s.isdigit() for s in sep)
    return Version(major=int(sep[0]), minor=int(sep[1]), patch=int(sep[2]))


def _semver_to_str(v: Version) -> str:
    return f"{v.major}.{v.minor}.{v.patch}"


def _bump_semver(version: Version, bump_type: BumpType) -> str:
    major = version.major
    minor = version.minor
    patch = version.patch
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return _semver_to_str(Version(major=major, minor=minor, patch=patch))


def bump_codex_plugin_version(name: str, bump: BumpType) -> None:
    path = PLUGINS_PATH / name / PLUGIN_FILE
    with open(path, "r") as f:
        data = json.load(f)
    version = data.get("version")
    if version is None:
        raise KeyError(f"No version in the {name} plugin")
    vers = _parse_semver(version)
    new_vers = _bump_semver(version=vers, bump_type=bump)
    data["version"] = new_vers
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Successfully bumped {name} version: {_semver_to_str(vers)} -> {new_vers}")


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "name", help="Name of the plugin whose version needs to be bumped"
    )
    parser.add_argument(
        "-b",
        "--bump",
        help="Version bump (can be patch, minor or major)",
        choices=["patch", "minor", "major"],
    )
    args = parser.parse_args()
    bump_codex_plugin_version(args.name, args.bump)


if __name__ == "__main__":
    main()
