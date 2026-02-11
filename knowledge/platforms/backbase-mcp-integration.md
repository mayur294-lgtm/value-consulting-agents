# Backbase Infobank MCP Integration

## What This Is

The **Backbase Infobank** is a live MCP (Model Context Protocol) server that gives agents direct access to the full Backbase platform and product knowledge base — documentation, product capabilities, architecture references, API details, and more.

**URL:** `https://mcp.backbase.io/mcp`

This is the authoritative, up-to-date source for Backbase product knowledge. When agents need to validate capabilities, check product features, or ground recommendations in actual platform functionality, they should query this MCP server.

## Security: Authentication Required

The Infobank MCP server is protected by **Backbase SSO**. Every consultant must authenticate individually on first use. Without valid Backbase credentials, the server returns nothing.

This means:
- The `.mcp.json` config file is safe to commit to the repo — it only contains the public endpoint URL
- If this repo is forked or shared outside Backbase, the MCP server is inaccessible without Backbase SSO
- No API keys, tokens, or secrets are stored in the config
- Authentication is per-user, not per-repo

## When Agents Should Use It

| Scenario | Example Query |
|----------|--------------|
| **Validating product capabilities** | "Does Backbase support instant card issuance?" |
| **Architecture questions** | "How does the Identity layer integrate with core banking?" |
| **Product directory lookups** | "What OOTB features exist for loan origination?" |
| **Competitive positioning** | "What differentiates Backbase's engagement banking approach?" |
| **Implementation guidance** | "What are the integration patterns for payment hubs?" |
| **Version/release info** | "What capabilities were added in the latest platform release?" |

## How to Reference in Agent Prompts

When building or updating agents that need Backbase product knowledge, include this instruction:

```
## Backbase Product Knowledge

You have access to the Backbase Infobank MCP server. Use the MCP search tools
(prefixed with `mcp__backbase-infobank__`) to query live Backbase documentation
for product capabilities, architecture details, and platform features.

Always prefer MCP queries over static knowledge files when you need:
- Current product capabilities and feature availability
- Architecture and integration patterns
- API and technical specifications
- Release and version information
```

## MCP Tool Names

Once connected, the MCP tools will be available with the prefix:
```
mcp__backbase-infobank__<tool_name>
```

Use `ToolSearch` or check available tools at runtime to discover the exact tool names exposed by the server.

## Relationship to Static Knowledge

| Source | Use When |
|--------|----------|
| **MCP Infobank (live)** | Validating specific capabilities, checking current features, architecture details, anything that could change between releases |
| **Static knowledge files** (`knowledge/backbase_platform_lexicon.md`, CSVs) | Consulting frameworks, value propositions, engagement methodology, benchmark data — things that don't change with product releases |

**Rule of thumb:** Static files for *consulting methodology*, MCP for *product facts*.

## Setup for New Developers / Consultants

### Claude Code (CLI)
Already configured. The `.mcp.json` file at the project root registers the server automatically. On first use, you'll be prompted to authenticate via Backbase SSO.

### VS Code + Claude Extension
Already configured. The `.vscode/mcp.json` file registers the server. To authenticate:
1. Open Command Palette (`Cmd+Shift+P`)
2. Run `MCP: List Servers`
3. Select **backbase-infobank**
4. Click **Start Server**
5. When prompted to authenticate, click **Allow**
6. When asked about opening external website, click **Cancel**
7. On the URL Handler option, click **Yes**
8. Click **Open** and complete Backbase authentication

### Manual Setup (Other Environments)
Add this MCP server configuration:
- **Type:** HTTP
- **URL:** `https://mcp.backbase.io/mcp`
- **Name:** backbase-infobank
- **Auth:** Backbase SSO (prompted on first connection)
