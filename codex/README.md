# Phasis for Codex (0.2.0)

`AGENTS.md` in this folder holds the text that connects a Codex agent to Phasis Core v2 (`start`, `recall`, `search`, `record`, `correct`, `run_way`, `check_work`, `upload`, `search_demand`). It matches the prompt hook of the Phasis `0.2.0` plugin for Claude Code, with one extra sentence that names the Codex code-mode call `tools.mcp__phasis__start`.

Why Codex needs this text: in code mode, Codex keeps MCP tools inside its `exec` tool. The model does not see the Phasis tool names or the Phasis server instructions. Without this text, the agent seldom calls Phasis (1 of 118 test questions).

## Set it up

1. Add the Phasis MCP server to `~/.codex/config.toml`. Codex CLI (`0.167.0`) OAuth/MCP sign-in to `https://mcp.phas.is/mcp` is verified live. For setup steps, see [phasis.ai/setup](https://phasis.ai/setup).

   ```toml
   [mcp_servers.phasis]
   url = "https://mcp.phas.is/mcp"
   ```

2. Copy the text of `AGENTS.md` into your global Codex instructions: `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md`). If that file has other text, add this text at the end. If a non-empty `AGENTS.override.md` is in the same folder, Codex reads that file instead, so add the text there.
3. Start a new Codex session.

To use the text in one project only, put it in `AGENTS.md` at the root of that project instead.

## What the text asks the agent to do

- Call the Phasis `start` tool at task start, and before answering a question about you, your team, the project, earlier conversations, or saved rules (calling `recall` with `about` set to the case id and narrower words if `rules_more` is nonzero, an item is cut, or the answer is partial).
- Save a decision, rule, standard, or preference that you state, or a plain statement about you, your team, or your work, in your exact words with `record` (and record corrections or withdrawals of earlier rules with `correct`).
- Never save a key, token, password, or other secret, text it read or that you quote from someone else, or its own suggestion unless you accept it.
- If no Phasis tool is listed after one tool search, note once that Phasis is not connected, continue without it, and never report anything saved.
- Apply saved rules, query Phasis shared Worlds via `search` (`where: "shared"` or `"both"`) for questions about roles, jobs, employers, suppliers, or chemicals, and re-read the case via `recall` before any action that pays, releases, sends, or deletes.

The text is only instructions. It sends nothing and writes no file. For Phasis, the agent sends data only to `mcp.phas.is`, only through the Phasis MCP server, and only with your own sign-in.
