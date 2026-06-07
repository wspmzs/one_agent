# MCP Configurator — Deep Patterns

Read this when standard add/list/remove workflow is not enough.

## Pattern: Custom Env Variables

MCP servers often need env vars (API keys, paths, language settings).

mcp-server-icon example:
```
env: {
  "LANGUAGE": "zh-CN",          # emoji descriptions language
  "WEB_SERVER_AUTO_OPEN": "false"  # suppress auto browser open
}
```

Rule: Set env vars in the `env` object. Agent.json stores them alongside command/args.

## Pattern: Transport Types

| Transport | When to use | Config fields |
|-----------|------------|---------------|
| stdio | Local server via command | command, args, env, cwd |
| streamable_http | Remote HTTP server | url, headers |
| sse | Remote SSE server | url, headers |

mcp-server-icon uses stdio (runs locally via npx).

## Pattern: Npx vs Global Install

Two ways to run npm-based MCP servers:

**Via npx (recommended for first use):**
```
command: "npx"
args: ["-y", "@liangshanli/mcp-server-icon"]
```
Advantage: auto-downloads, always latest.

**Via global install:**
```
command: "mcp-server-icon"
```
Advantage: no download delay.
Requires: `npm install -g @liangshanli/mcp-server-icon`

## Pattern: Testing After Add

After adding MCP client, verify it's working:

1. Wait 5-10 seconds for watcher to detect change
2. Check if process started (Task Manager / `ps`)
3. Ask QwenPaw: "list tools from mcp-server-icon"
4. If fails, check `qwenpaw.log` for errors

## Pattern: Multiple Node MCP Servers

Running multiple `npx` MCP servers in same workspace:
- Each uses its own Node process
- No port conflicts (stdio isolation)
- Env vars are per-client, not global

## Pattern: Disable Without Deleting

Instead of removing a client, set `enabled: false`.
This preserves the config for later re-enable.
The watcher skips disabled clients (doesn't start them).

## Edge Cases

**npx not found**: Node installed but npm/npx not in PATH.
Fix: Install npx globally or use full path: `C:\Users\...\AppData\Roaming\npm\npx.cmd`

**Command path with spaces**: Windows path like `C:\Program Files\nodejs\npx.cmd`.
Wrap in quotes or use 8.3 filename notation.

**Port conflicts**: Some MCP servers need HTTP ports.
Check `netstat -ano | findstr :PORT` before adding.

**Watcher delay**: Config watcher polls every 2 seconds.
Wait up to 5 seconds after edit before expecting the server to be ready.

**Config not found**: agent.json missing mcp.clients.
Add the section manually:
```json
"mcp": {
  "clients": {}
}
```
