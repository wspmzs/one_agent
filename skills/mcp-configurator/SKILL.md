---
name: mcp_configurator
description: "This skill should be used when the user asks to 'add an MCP server', 'configure MCP', 'list MCP clients', 'remove MCP server', 'enable MCP', 'disable MCP', 'test MCP connection', 'manage MCP', 'set up MCP', 'add {server} to MCP', 'check MCP config'. Also when the user provides a GitHub link to an MCP server and asks to add it."
metadata:
  qwenpaw:
    emoji: "🛠️"
    requires: {}
---

# MCP CONFIGURATOR

## WHAT

Manage MCP servers in QwenPaw.
Add, list, remove, toggle MCP clients.
Config changes auto-detected by watcher (2s poll).

No API calls needed. Edit `agent.json` directly.

## WHERE

Config file: `agent.json` → `mcp.clients.{key}`

Each client entry format:
```json
"client_key": {
  "name": "Display Name",
  "description": "What this server does",
  "enabled": true,
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "package-name"],
  "env": {"KEY": "VALUE"},
  "cwd": ""
}
```

## WORKFLOW

### Step 1: Probe (optional but recommended)

Before adding an MCP server:
- Check if runtime is available (Node, Python, etc.)
- Use **Environment Probe** skill for this
- If runtime missing, report and suggest install

### Step 2: Understand the Server

For any MCP server (especially from GitHub):
- Read its README or docs
- Find: runtime required, command to run, env vars needed
- If npx package: extract package name from install command

### Step 3: Choose Operation

**List current clients**
Read `agent.json` → `mcp.clients`. Print all keys.

**Add a new client**
1. Construct the entry object
2. Insert into `agent.json` → `mcp.clients`
3. Use `edit_file` or `read_file` + `write_file` to update JSON
4. Wait 5s for watcher to detect
5. Validate config

**Remove a client**
1. Remove key from `mcp.clients`
2. Write updated JSON
3. Server process will be cleaned up

**Toggle enable/disable**
1. Read agent.json
2. Set `mcp.clients.{key}.enabled` to false/true
3. Write it back

### Step 4: Validate

Run `scripts/validate-mcp-config.ps1` on Windows.
Or manually check:
- [ ] Valid JSON syntax
- [ ] All required fields present (name, enabled, transport)
- [ ] stdio transport has command + args
- [ ] npx command has at least one arg
- [ ] HTTP/SSE transport has url

### Step 5: Verify Connection

MCP watcher auto-detects changes within 2-5 seconds.
To verify server is running:
- Ask user: "try using the new MCP server"
- Or check if process appeared (Task Manager)
- If server fails to start, check `qwenpaw.log` for errors

## OUTPUT FORMAT

When listing MCP clients:

```
🛠️ MCP Clients (in agent.json)
  tavily_search         🟢 enabled  → stdio: npx -y tavily-mcp@latest
  mcp_server_icon       🟢 enabled  → stdio: npx -y @liangshanli/mcp-server-icon
```

When adding:

```
✅ Added mcp_server_icon to MCP clients
   Runtime: Node.js (v20.19.1) ✓
   Config: npx -y @liangshanli/mcp-server-icon
   Env: LANGUAGE=zh-CN, WEB_SERVER_AUTO_OPEN=false
   ⏳ Waiting 5s for watcher to auto-load...
   ✅ Client loaded
```

## RESOURCES

- **`scripts/validate-mcp-config.ps1`** — Validate agent.json MCP section (Windows)
- **`references/config-patterns.md`** — Deep patterns: transports, npx vs global, env vars
- **`examples/mcp-server-icon-entry.json`** — Working example entry

## VALIDATE

After any MCP config change:
- [ ] agent.json is valid JSON
- [ ] New client has all required fields
- [ ] Runtime exists for the server (Node/Python/etc.)
- [ ] Args match the server's documented command
- [ ] Enabled flag set correctly
