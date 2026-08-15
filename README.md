# LlamaParse Agent Plugins

Four document-focused plugins from LlamaIndex, packaged as a marketplace for both Claude and Codex.
Parse documents locally with LiteParse, or connect to the LlamaParse Platform for cloud parsing and
agentic retrieval over Index v2 knowledge bases.

| Plugin | Type | What it does | Needs an account? |
| --- | --- | --- | --- |
| `liteparse` | Skill | Local OCR parsing for PDFs, Office docs, and images | No — fully local |
| `llamaparse` | Skill | Cloud parsing via the LlamaParse API | Yes — API key |
| `llamaparse-mcp` | MCP + skills | Parse/split/classify plus Index v2 retrieval | Yes — OAuth |
| `llamaparse-mcp-eu` | MCP + skills | The same, pointed at the Europe region | Yes — OAuth |

**Which MCP plugin?** Region follows your LlamaCloud account, not a per-session choice. Accounts on
`cloud.llamaindex.ai` need `llamaparse-mcp`; accounts on `cloud.eu.llamaindex.ai` need
`llamaparse-mcp-eu`. A token issued in one region is rejected by the other.

## Install

<details>
<summary><b>Claude</b></summary>

Add the marketplace:

```
/plugin marketplace add run-llama/llamaparse-agent-plugins
```

Then install whichever plugins you want:

```
/plugin install liteparse@llamaparse-marketplace
/plugin install llamaparse@llamaparse-marketplace
/plugin install llamaparse-mcp@llamaparse-marketplace
/plugin install llamaparse-mcp-eu@llamaparse-marketplace
```

Skills are namespaced by plugin, so invoke them as `/<plugin>:<skill>`:

```
/liteparse:liteparse
/llamaparse:llamaparse
/llamaparse-mcp:llamaparse-mcp   # parse / split / classify
/llamaparse-mcp:llamacloud-index # Index v2 agentic retrieval
```

The `llamaparse-mcp-eu` plugin exposes the same skills under its own namespace
(`/llamaparse-mcp-eu:llamaparse-mcp`, and so on).

If the install summary says `Run /reload-plugins to activate`, run it.

</details>

<details>
<summary><b>Codex</b></summary>

Add the marketplace:

```bash
codex plugin marketplace add run-llama/llamaparse-agent-plugins
```

Then start or reload Codex, open plugin management, find the marketplace `llamaparse-marketplace`
(display name: `LlamaParse Codex MarketPlace`), and install any of `liteparse`, `llamaparse`,
`llamaparse-mcp`, or `llamaparse-mcp-eu`.

Confirm availability in a Codex thread — skills appear as `liteparse:liteparse`,
`llamaparse-mcp:llamaparse-mcp`, `llamaparse-mcp:llamacloud-index`, and so on.

The MCP plugins declare `authentication: ON_USE` in the Codex marketplace, so Codex prompts on the
first tool call rather than at install time.

</details>

## Authentication

- `liteparse` — none. Runs fully locally.
- `llamaparse` — needs a [LlamaParse API key](https://cloud.llamaindex.ai/signup) in
  `LLAMA_CLOUD_API_KEY`.
- `llamaparse-mcp` / `llamaparse-mcp-eu` — OAuth, no API key. The flow runs in your client on first
  tool use.

## Verify it works

<details>
<summary><b>LlamaParse MCP — document processing</b></summary>

1. Request an upload URL with `getUploadUrl`.
2. Upload a file (for example `test.txt`) to the returned pre-signed endpoint.
3. Call `parseFile` with the returned `fileId`.

Expected result: parsed text content is returned.

</details>

<details>
<summary><b>LlamaParse MCP — Index v2 retrieval</b></summary>

1. Call `listIndexes` to confirm at least one index is visible.
2. Call `retrieveFromIndex` with a natural-language question against one of the returned indexes.

Expected result: relevant passages from your indexed documents are returned.

An empty `listIndexes` result still means auth succeeded — you just have no indexes yet.

</details>

## Privacy Policy & Terms

`liteparse` runs entirely locally and transmits no data. The `llamaparse`, `llamaparse-mcp`, and
`llamaparse-mcp-eu` plugins send the documents you ask them to process to the LlamaParse Platform
for parsing, indexing, and retrieval.

- [Privacy Notice](https://www.llamaindex.ai/legal/privacy-notice)
- [Terms of Service](https://www.llamaindex.ai/legal/terms-of-service)
- Support: support@llamaindex.ai

## Repository layout

```
.claude-plugin/marketplace.json    marketplace definition consumed by Claude
.agents/plugins/marketplace.json   marketplace definition consumed by Codex
plugins/<name>/
  .claude-plugin/plugin.json       Claude manifest
  .codex-plugin/plugin.json        Codex manifest
  .mcp.json                        MCP server config (MCP plugins only)
  skills/<skill>/SKILL.md          skills, one directory each
  assets/                          icon and logo
```

Each plugin carries a manifest per agent. The two must agree on name and version — the validator
enforces this.

## Development

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

For Claude specifically, also run the first-party validator — the plugin directory's review
pipeline runs the same check:

```bash
claude plugin validate .
claude plugin validate ./plugins/<name>
```

### Bump version

```bash
python3 scripts/bump-version.py <claude|codex> <plugin> --bump <patch|minor|major>
# if you have uv
./scripts/bump-version.py <claude|codex> <plugin> --bump <patch|minor|major>
```

Bump both agents so the versions stay in sync:

```bash
./scripts/bump-version.py codex liteparse --bump minor
./scripts/bump-version.py claude liteparse --bump minor
```

### Keeping skills in sync

Most skills here are **copies** with an upstream elsewhere. There is no automation, so they drift
silently. Check them before a release.

| Skill | Upstream | Relationship |
| --- | --- | --- |
| `liteparse/skills/liteparse` | [`llamaparse-agent-skills`](https://github.com/run-llama/llamaparse-agent-skills/blob/main/skills/liteparse/SKILL.md) | Verbatim copy — sync as-is |
| `llamaparse/skills/llamaparse` | [`llamaparse-agent-skills`](https://github.com/run-llama/llamaparse-agent-skills/blob/main/skills/llamaparse/SKILL.md) | Verbatim copy — sync as-is |
| `llamaparse-mcp*/skills/llamaparse-mcp` | [`mcp-llamaindex-ai`](https://github.com/run-llama/mcp-llamaindex-ai/blob/main/skills/llamaparse-mcp/SKILL.md) | Copy with intentional deltas — see below |
| `llamaparse-mcp*/skills/llamacloud-index` | [`llamaparse-agent-skills`](https://github.com/run-llama/llamaparse-agent-skills/blob/main/skills/llamacloud-index/SKILL.md) | Deliberate rewrite — do **not** sync |

`llamacloud-index` shares a name with the upstream skill but is a different document: upstream
drives the REST API with `curl` and an API key, while the version here drives the MCP tools over
OAuth. They are not interchangeable — treat them as separate skills that happen to share a title.

Two deltas in `llamaparse-mcp` are intentional and should survive a sync: the `Index v2 Retrieval`
section (which points at the sibling `llamacloud-index` skill, something the upstream server repo
has no notion of), and the cross-region `401` advice (upstream tells the user to repoint their
client, which a plugin user cannot do because the URL is fixed in the manifest — here the
instruction is to install the sibling regional plugin).

The EU plugin's skills are copies of the NA plugin's with the hostname and region swapped. Change
one, change the other.
