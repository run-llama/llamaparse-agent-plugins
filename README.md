# LlamaParse Agent Plugins Marketplace

This repository contains local Codex and Claude plugin marketplace definitions with three document-focused plugins from LlamaIndex.

## Repository Contents

- `.agents/plugins/marketplace.json`: Marketplace definition consumed by Codex.
- `.claude-plugin/marketplace.json`: Marketplace definition consumed by Claude.
- `plugins/liteparse`: Local OCR parsing plugin (no cloud dependency).
- `plugins/llamaparse`: Cloud parsing skill plugin.
- `plugins/llamaparse-mcp`: LlamaParse Platform MCP plugin (tools for parse/split/classify via MCP).

## Plugins Included

1. `liteparse`
- Type: Skill plugin
- Purpose: Parse and extract content from PDFs, Office docs, and images locally.

2. `llamaparse`
- Type: Skill plugin
- Purpose: Cloud-based, advanced document parsing.

3. `llamaparse-mcp`
- Type: MCP + skill plugin
- Purpose: Connects Codex to LlamaParse Platform MCP tools.
- MCP server config: `plugins/llamaparse-mcp/.mcp.json` -> `https://mcp.llamaindex.ai/mcp`
- (Codex) Auth policy in marketplace: `ON_USE`

## Install The Marketplace

### Codex

```bash
codex plugin marketplace add run-llama/llamaparse-codex-plugins
```

### Claude

(within Claude)

```bash
/plugin marketplace add run-llama/llamaparse-agent-plugins
```

## Enable Plugins

### Codex

1. Start or reload Codex
2. Open plugin management in Codex.
3. Find marketplace `llamaparse-marketplace` (display name: `LlamaParse Codex MarketPlace`).
4. Install any of the following plugins:
- `liteparse`
- `llamaparse`
- `llamaparse-mcp`

**Authentication Notes**

- `liteparse`: No authentication required, runs fully locally.
- `llamaparse-mcp`: Prompts on first use (`ON_USE`) when invoking MCP tools.
- `llamaparse`: Follow any in-app prompts for required credentials ([LlamaParse API key](https://cloud.llamaindex.ai/signup)).

**Verify Plugin Availability**

After enabling plugins, confirm they are available in a Codex thread:

- `liteparse` skill should appear as `liteparse:liteparse`.
- `llamaparse-mcp` skill should appear as `llamaparse-mcp:llamaparse-mcp`.
- MCP tools should include operations like:
- `parseFile`
- `splitFile`
- `classifyFile`
- `uploadFileByUrl`

### Claude

Within Claude, run:

```bash
/plugin install liteparse@llamaparse-marketplace
/plugin install llamaparse@llamaparse-marketplace
/plugin install llamaparse-mcp@llamaparse-marketplace
```

**Use plugins**

Invoke the plugins as slash commands directly within Claude:

```bash
/liteparse:liteparse # -> run liteparse skill

```

## Quick Smoke Test (LlamaParse MCP)

1. Request an upload URL with `getUploadUrl`.
2. Upload a file (for example `test.txt`) to the returned pre-signed endpoint.
3. Call `parseFile` with the returned `fileId`.

Expected result: parsed text content is returned.

## Development Notes

- Plugin manifests are located at:
  + `plugins/liteparse/.*-plugin/plugin.json`
  + `plugins/llamaparse/.*-plugin/plugin.json`
  + `plugins/llamaparse-mcp/.*-plugin/plugin.json`
- MCP server mapping is in `plugins/llamaparse-mcp/.mcp.json`.

### Bump version

Bump the version of a plugin for a specific agent with:

```bash
python3 scripts/bump-version.py <claude|codex> <plugin> --bump <patch|minor|major>
# if you have uv
./scripts/bump-version.py <claude|codex> <plugin> --bump <patch|minor|major>
```

For example:

```bash
./scripts/bump-version.py codex liteparse --bump minor
./scripts/bump-version.py claude liteparse --bump minor
```
