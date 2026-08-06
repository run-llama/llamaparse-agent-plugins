#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Structural checks over the marketplace manifests and every plugin.

Each check exists because the corresponding mistake is easy to make and
invisible until a user tries to install something.
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGINS = REPO / "plugins"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"

errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def load_json(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        error(f"{path.relative_to(REPO)}: missing")
    except json.JSONDecodeError as e:
        error(f"{path.relative_to(REPO)}: invalid JSON ({e})")
    return None


def check_marketplaces_agree() -> set[str]:
    """A plugin registered in one marketplace and not the other half-ships:
    it installs under one agent and is invisible in the other."""
    claude = load_json(CLAUDE_MARKETPLACE)
    codex = load_json(CODEX_MARKETPLACE)
    if claude is None or codex is None:
        return set()

    claude_names = {p["name"] for p in claude.get("plugins", [])}
    codex_names = {p["name"] for p in codex.get("plugins", [])}
    for name in sorted(claude_names - codex_names):
        error(f"{name}: in the Claude marketplace but not the Codex one")
    for name in sorted(codex_names - claude_names):
        error(f"{name}: in the Codex marketplace but not the Claude one")

    on_disk = {p.name for p in PLUGINS.iterdir() if p.is_dir()}
    for name in sorted(claude_names | codex_names):
        if name not in on_disk:
            error(f"{name}: registered in a marketplace but plugins/{name} does not exist")
    for name in sorted(on_disk - (claude_names | codex_names)):
        error(f"{name}: plugins/{name} exists but is registered in no marketplace")

    return (claude_names | codex_names) & on_disk


def check_plugin(name: str, mcp_servers: dict[str, str]) -> None:
    directory = PLUGINS / name
    versions = {}

    for agent in ("claude", "codex"):
        manifest = load_json(directory / f".{agent}-plugin" / "plugin.json")
        if manifest is None:
            continue
        if manifest.get("name") != name:
            error(
                f"{name}: .{agent}-plugin/plugin.json declares name "
                f"{manifest.get('name')!r}, which does not match the directory"
            )
        versions[agent] = manifest.get("version")

    if len(set(versions.values())) > 1:
        error(f"{name}: version differs between agents: {versions}")

    claude_manifest = load_json(directory / ".claude-plugin" / "plugin.json") or {}
    inline = claude_manifest.get("mcpServers") or {}
    mcp_file = directory / ".mcp.json"

    if not inline and not mcp_file.exists():
        return

    standalone = (load_json(mcp_file) or {}).get("mcpServers", {}) if mcp_file.exists() else {}
    # The endpoint lives in two files per plugin; updating one and not the
    # other points Claude and Codex at different servers.
    if inline and standalone and inline != standalone:
        error(
            f"{name}: .claude-plugin/plugin.json and .mcp.json declare different "
            f"MCP servers ({inline} vs {standalone})"
        )

    for key, server in (inline or standalone).items():
        url = server.get("url")
        # Two plugins claiming the same server key collide when both are installed.
        if key in mcp_servers:
            error(
                f"{name}: MCP server key {key!r} is already used by "
                f"{mcp_servers[key]}; both cannot be installed together"
            )
        else:
            mcp_servers[key] = name
        if not url or not url.startswith("https://"):
            error(f"{name}: MCP server {key!r} has a non-HTTPS url {url!r}")

    skills = directory / "skills"
    if skills.is_dir():
        for skill in sorted(p for p in skills.iterdir() if p.is_dir()):
            if not (skill / "SKILL.md").exists():
                error(f"{name}: skills/{skill.name}/ has no SKILL.md")


def main() -> int:
    if not PLUGINS.is_dir():
        print(f"no plugins/ directory at {PLUGINS}", file=sys.stderr)
        return 1

    mcp_servers: dict[str, str] = {}
    for name in sorted(check_marketplaces_agree()):
        check_plugin(name, mcp_servers)

    if errors:
        print(f"{len(errors)} problem(s):\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"marketplace manifests and {len(mcp_servers)} MCP server(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
