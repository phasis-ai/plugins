# Phasis for Codex

`AGENTS.md` in this folder holds the text that tells a Codex agent to call Phasis and to save what you say. It is the same text as the prompt hook of the Phasis plugin for Claude Code, with one more sentence that names the Codex call `tools.mcp__phasis__start`.

Why Codex needs this text: in code mode, Codex keeps MCP tools inside its `exec` tool. The model does not see the Phasis tool names or the Phasis server instructions. Without this text, the agent seldom calls Phasis (1 of 118 test questions).

## Set it up

1. Add the Phasis MCP server to `~/.codex/config.toml`. We did not test Codex sign-in to `mcp.phas.is` yet. For the sign-in, see [phasis.ai/setup](https://phasis.ai/setup).

   ```toml
   [mcp_servers.phasis]
   url = "https://mcp.phas.is/mcp"
   ```

2. Copy the text of `AGENTS.md` into your global Codex instructions: `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md`). If that file has other text, add this text at the end. If a non-empty `AGENTS.override.md` is in the same folder, Codex reads that file instead, so add the text there.
3. Start a new Codex session.

To use the text in one project only, put it in `AGENTS.md` at the root of that project instead.

## What the text asks the agent to do

- Call the Phasis `start` tool at the start of every task, and before it answers a question about you, your team, the project, earlier conversations or saved rules.
- Save a decision, rule, standard or preference that you state, or a plain statement about you, your life, your team or your work, in your exact words.
- Not save a key, a token, a password or other secret, text that it read or that you quote from someone else, or its own suggestion unless you accept it.
- If no Phasis tool is listed after one tool search, say once that Phasis is not connected, continue without it, and not say that anything is saved.
- Follow the saved rules, use the Phasis Worlds for questions about roles, jobs, employers, suppliers or chemicals, and read the case again before an action that pays, releases, sends or deletes.

The text is only instructions. It sends nothing and writes no file. For Phasis, the agent sends data only to `mcp.phas.is`, only through the Phasis MCP server, and only with your own sign-in.
