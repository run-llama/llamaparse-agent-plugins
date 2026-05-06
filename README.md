# LlamaParse Codex Plugin Marketplace

This repository contains a local Codex plugin marketplace with three document-focused plugins from LlamaIndex.

## Repository Contents

- `.agents/plugins/marketplace.json`: Marketplace definition consumed by Codex.
- `plugins/liteparse`: Local OCR parsing plugin (no cloud dependency).
- `plugins/llamaparse`: Cloud parsing skill plugin.
- `plugins/llamaparse-mcp`: LlamaParse Platform MCP plugin (tools for parse/split/classify via MCP).

## Plugins Included

1. `liteparse`
- Type: Skill plugin
- Purpose: Parse and extract content from PDFs, Office docs, and images locally.
- Auth policy in marketplace: `ON_INSTALL`

2. `llamaparse`
- Type: Skill plugin
- Purpose: Cloud-based, advanced document parsing.
- Auth policy in marketplace: no explicit auth gate in marketplace policy

3. `llamaparse-mcp`
- Type: MCP + skill plugin
- Purpose: Connects Codex to LlamaParse Platform MCP tools.
- MCP server config: `plugins/llamaparse-mcp/.mcp.json` -> `https://mcp.llamaindex.ai/mcp`
- Auth policy in marketplace: `ON_USE`

## Install The Marketplace

```bash
codex plugin marketplace add run-llama/llamaparse-codex-plugins
```

## Enable Plugins In Codex

1. Start or reload Codex
2. Open plugin management in Codex.
3. Find marketplace `llamaparse-marketplace` (display name: `LlamaParse Codex MarketPlace`).
4. Install any of the following plugins:
- `liteparse`
- `llamaparse`
- `llamaparse-mcp`

## Authentication Notes

- `liteparse`: No authentication required, runs fully locally.
- `llamaparse-mcp`: Prompts on first use (`ON_USE`) when invoking MCP tools.
- `llamaparse`: Follow any in-app prompts for required credentials ([LlamaParse API key](https://cloud.llamaindex.ai/signup)).

## Verify Plugin Availability

After enabling plugins, confirm they are available in a Codex thread:

- `liteparse` skill should appear as `liteparse:liteparse`.
- `llamaparse-mcp` skill should appear as `llamaparse-mcp:llamaparse-mcp`.
- MCP tools should include operations like:
- `parseFile`
- `splitFile`
- `classifyFile`
- `uploadFileByUrl`

## Quick Smoke Test (LlamaParse MCP)

1. Request an upload URL with `getUploadUrl`.
2. Upload a file (for example `test.txt`) to the returned pre-signed endpoint.
3. Call `parseFile` with the returned `fileId`.

Expected result: parsed text content is returned.

## Development Notes

- Plugin manifests are located at:
- `plugins/liteparse/.codex-plugin/plugin.json`
- `plugins/llamaparse/.codex-plugin/plugin.json`
- `plugins/llamaparse-mcp/.codex-plugin/plugin.json`
- MCP server mapping is in `plugins/llamaparse-mcp/.mcp.json`.
