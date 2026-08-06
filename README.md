# LlamaParse Agent Plugins Marketplace

This repository contains local Codex and Claude plugin marketplace definitions with four document-focused plugins from LlamaIndex.

## Repository Contents

- `.agents/plugins/marketplace.json`: Marketplace definition consumed by Codex.
- `.claude-plugin/marketplace.json`: Marketplace definition consumed by Claude.
- `plugins/liteparse`: Local OCR parsing plugin (no cloud dependency).
- `plugins/llamaparse`: Cloud parsing skill plugin.
- `plugins/llamaparse-mcp`: LlamaParse Platform MCP plugin (tools for parse/split/classify plus Index v2 retrieval via MCP).
- `plugins/llamaparse-mcp-eu`: the same plugin pointed at the Europe region.

## Plugins Included

1. `liteparse`
- Type: Skill plugin
- Purpose: Parse and extract content from PDFs, Office docs, and images locally.

2. `llamaparse`
- Type: Skill plugin
- Purpose: Cloud-based, advanced document parsing.

3. `llamaparse-mcp`
- Type: MCP + skills plugin
- Purpose: Connects Codex to LlamaParse Platform MCP tools (document processing and Index v2 retrieval).
- Skills: `llamaparse-mcp` (parse/split/classify usage guide) and `llamacloud-index` (agentic retrieval over Index v2 knowledge bases).
- MCP server config: `plugins/llamaparse-mcp/.mcp.json` -> `https://mcp.llamaindex.ai/mcp`
- (Codex) Auth policy in marketplace: `ON_USE`

4. `llamaparse-mcp-eu`
- Type: MCP + skills plugin
- Purpose: identical to `llamaparse-mcp`, pointed at the Europe region.
- MCP server config: `plugins/llamaparse-mcp-eu/.mcp.json` -> `https://mcp.eu.llamaindex.ai/mcp`
- (Codex) Auth policy in marketplace: `ON_USE`

Install whichever matches your LlamaCloud account: `cloud.llamaindex.ai` -> `llamaparse-mcp`,
`cloud.eu.llamaindex.ai` -> `llamaparse-mcp-eu`. Region is a property of the account, not a
per-session choice, and a token issued in one region is rejected by the other.

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
- `llamaparse-mcp-eu`

**Authentication Notes**

- `liteparse`: No authentication required, runs fully locally.
- `llamaparse-mcp` / `llamaparse-mcp-eu`: Prompts on first use (`ON_USE`) when invoking MCP tools.
- `llamaparse`: Follow any in-app prompts for required credentials ([LlamaParse API key](https://cloud.llamaindex.ai/signup)).

**Verify Plugin Availability**

After enabling plugins, confirm they are available in a Codex thread:

- `liteparse` skill should appear as `liteparse:liteparse`.
- `llamaparse-mcp` skills should appear as `llamaparse-mcp:llamaparse-mcp` and `llamaparse-mcp:llamacloud-index` (or `llamaparse-mcp-eu:*` for the Europe plugin).
- MCP tools should include operations like:
- `parseFile`
- `splitFile`
- `classifyFile`
- `uploadFileByUrl`
- `listIndexes`
- `retrieveFromIndex`

### Claude

Within Claude, run:

```bash
/plugin install liteparse@llamaparse-marketplace
/plugin install llamaparse@llamaparse-marketplace
/plugin install llamaparse-mcp@llamaparse-marketplace
/plugin install llamaparse-mcp-eu@llamaparse-marketplace
```

**Use plugins**

Invoke the plugins as slash commands directly within Claude:

```bash
/liteparse:liteparse # -> run LiteParse skill
/llamaparse:llamaparse # -> run LlamaParse skill
/llamaparse-mcp:llamaparse-mcp # -> enable LlamaParse MCP and its document-processing skill
/llamaparse-mcp:llamacloud-index # -> enable LlamaParse MCP and its Index v2 agentic-retrieval skill
/llamaparse-mcp-eu:llamaparse-mcp # -> same, against the Europe region
/llamaparse-mcp-eu:llamacloud-index # -> same, against the Europe region
```

## Quick Smoke Test (LlamaParse MCP)

1. Request an upload URL with `getUploadUrl`.
2. Upload a file (for example `test.txt`) to the returned pre-signed endpoint.
3. Call `parseFile` with the returned `fileId`.

Expected result: parsed text content is returned.

## Quick Smoke Test (Index v2)

1. Call `listIndexes` to confirm at least one index is visible.
2. Call `retrieveFromIndex` with a natural-language question against one of the returned indexes.

Expected result: relevant passages from your indexed documents are returned.

## Development Notes

- Plugin manifests are located at:
  + `plugins/liteparse/.*-plugin/plugin.json`
  + `plugins/llamaparse/.*-plugin/plugin.json`
  + `plugins/llamaparse-mcp/.*-plugin/plugin.json`
  + `plugins/llamaparse-mcp-eu/.*-plugin/plugin.json`
- MCP server mapping is in `plugins/llamaparse-mcp/.mcp.json` and `plugins/llamaparse-mcp-eu/.mcp.json`.

### Validate

CI runs this on every pull request, and it is worth running before you push:

```bash
python3 scripts/validate-marketplace.py
```

It checks that both marketplace manifests list the same plugins, that every registered plugin
exists on disk (and vice versa), that each `plugin.json` name matches its directory, that the
Claude and Codex versions of a plugin agree, that `.mcp.json` and the inline `mcpServers` block
declare the same server, that no two plugins claim the same MCP server key, and that every skill
directory has a `SKILL.md`.

### Keeping skills in sync

`plugins/*/skills/llamaparse-mcp/SKILL.md` is a **copy** of the file in
[`run-llama/mcp-llamaindex-ai`](https://github.com/run-llama/mcp-llamaindex-ai/blob/main/skills/llamaparse-mcp/SKILL.md).
Edit it there first, then carry the change here — there is no automation, so it drifts silently.

Two deltas are intentional and should survive a sync: the `Index v2 Retrieval` section (which
points at the sibling `llamacloud-index` skill, something the upstream server repo has no notion
of), and the cross-region `401` advice (upstream tells the user to repoint their client, which a
plugin user cannot do because the URL is fixed in the manifest — here the instruction is to
install the sibling regional plugin).

`skills/llamacloud-index/SKILL.md` has no upstream and is owned by this repository.

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
