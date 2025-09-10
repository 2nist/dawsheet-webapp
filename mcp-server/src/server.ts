import { WebSocketServer } from "ws";
import { createServer } from "http";
import fetch from "cross-fetch";
import { exec } from "child_process";
import * as fs from "fs/promises";
import * as path from "path";
import os from "os";

const PORT = Number(process.env.PORT || 8974);
// Accept WS on any path so clients that can’t set a path still work
const PATH = process.env.MCP_PATH || "/mcp";
const API_BASE = process.env.API_BASE || "http://localhost:8000";
const AUTH_TOKEN = process.env.AUTH_TOKEN || ""; // optional
const WORKSPACE_ROOT =
  process.env.WORKSPACE_ROOT || path.resolve(process.cwd(), "..\\");
const MAX_READ_BYTES = 1_000_000; // 1MB
const MAX_OUTPUT_CHARS = 65_536; // 64KB approx

function authHeaders() {
  const headers: Record<string, string> = {
    "content-type": "application/json",
  };
  if (AUTH_TOKEN) headers["authorization"] = `Bearer ${AUTH_TOKEN}`;
  return headers;
}

function ensureWithinWorkspace(p: string): string {
  const full = path.isAbsolute(p)
    ? path.resolve(p)
    : path.resolve(WORKSPACE_ROOT, p);
  const root = path.resolve(WORKSPACE_ROOT);
  const normFull = full.replace(/\\/g, "/").toLowerCase();
  const normRoot = (root.endsWith(path.sep) ? root : root + path.sep)
    .replace(/\\/g, "/")
    .toLowerCase();
  if (!normFull.startsWith(normRoot)) {
    throw new Error(`Path outside workspace: ${full}`);
  }
  return full;
}

function truncate(str: string, max: number): string {
  if (str.length <= max) return str;
  return str.slice(0, max) + `\n...[truncated ${str.length - max} chars]`;
}

function runPwsh(
  command: string,
  cwd?: string,
  timeoutSec = 30
): Promise<{
  stdout: string;
  stderr: string;
  code: number | null;
  timedOut: boolean;
  durationMs: number;
}> {
  return new Promise((resolve) => {
    const started = Date.now();
    const child = exec(command, {
      cwd: cwd || WORKSPACE_ROOT,
      shell: process.env.COMSPEC || "pwsh.exe",
      windowsHide: true,
      env: { ...process.env },
      timeout: timeoutSec * 1000,
      maxBuffer: 10 * 1024 * 1024, // 10MB
    });
    let stdout = "";
    let stderr = "";
    child.stdout?.on("data", (d) => (stdout += String(d)));
    child.stderr?.on("data", (d) => (stderr += String(d)));
    child.on("close", (code, signal) => {
      const durationMs = Date.now() - started;
      const timedOut = signal === "SIGTERM" || signal === "SIGKILL";
      resolve({
        stdout: truncate(stdout, MAX_OUTPUT_CHARS),
        stderr: truncate(stderr, MAX_OUTPUT_CHARS),
        code,
        timedOut,
        durationMs,
      });
    });
  });
}

// Define tools
const tools = [
  {
    name: "list_songs",
    description: "List all songs",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false,
    },
    async handler() {
      const r = await fetch(`${API_BASE}/songs`, { headers: authHeaders() });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    },
  },
  {
    name: "get_song",
    description: "Get a song by id",
    inputSchema: {
      type: "object",
      required: ["id"],
      properties: { id: { type: "integer", minimum: 1 } },
      additionalProperties: false,
    },
    async handler(input: any) {
      const r = await fetch(`${API_BASE}/songs/${input.id}`, {
        headers: authHeaders(),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    },
  },
  {
    name: "combine_jcrd_lyrics",
    description:
      "Combine chords JSON with lyrics lines; set save=true to persist",
    inputSchema: {
      type: "object",
      required: ["jcrd"],
      properties: {
        jcrd: { type: "object" },
        lyrics: { type: "object" },
        title: { type: "string" },
        artist: { type: "string" },
        include_lyrics: { type: "boolean" },
        save: { type: "boolean" },
      },
      additionalProperties: true,
    },
    async handler(input: any) {
      const save = !!input.save;
      const url = `${API_BASE}/combine/jcrd-lyrics?save=${
        save ? "true" : "false"
      }`;
      const r = await fetch(url, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify(input),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    },
  },
  {
    name: "attach_lyrics",
    description:
      "Attach lyrics lines to an existing song (mode append|replace)",
    inputSchema: {
      type: "object",
      required: ["song_id", "lines"],
      properties: {
        song_id: { type: "integer", minimum: 1 },
        lines: {
          type: "array",
          items: {
            type: "object",
            required: ["text"],
            properties: {
              ts_sec: { type: ["number", "null"] },
              text: { type: "string" },
            },
          },
        },
        mode: { type: "string", enum: ["append", "replace"] },
      },
      additionalProperties: false,
    },
    async handler(input: any) {
      const r = await fetch(
        `${API_BASE}/songs/${input.song_id}/attach-lyrics`,
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify({
            lines: input.lines,
            mode: input.mode || "append",
          }),
        }
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    },
  },
  {
    name: "fs_list",
    description: "List files/directories under a path within the workspace",
    inputSchema: {
      type: "object",
      required: ["path"],
      properties: { path: { type: "string" } },
      additionalProperties: false,
    },
    async handler(input: any) {
      const full = ensureWithinWorkspace(input.path);
      const entries = await fs.readdir(full, { withFileTypes: true });
      const out = [] as any[];
      for (const e of entries) {
        const p = path.join(full, e.name);
        const stat = await fs.stat(p);
        out.push({
          name: e.name,
          path: p,
          type: e.isDirectory() ? "dir" : "file",
          size: stat.size,
          mtime: stat.mtimeMs,
        });
      }
      return { root: WORKSPACE_ROOT, path: full, entries: out };
    },
  },
  {
    name: "fs_read",
    description: "Read a text file within the workspace (max 1MB)",
    inputSchema: {
      type: "object",
      required: ["path"],
      properties: {
        path: { type: "string" },
        encoding: { type: "string", enum: ["utf-8"] },
      },
      additionalProperties: false,
    },
    async handler(input: any) {
      const full = ensureWithinWorkspace(input.path);
      const stat = await fs.stat(full);
      if (stat.size > MAX_READ_BYTES)
        throw new Error(`File too large: ${stat.size} bytes`);
      const content = await fs.readFile(full, "utf-8");
      return { path: full, encoding: "utf-8", size: stat.size, content };
    },
  },
  {
    name: "fs_write",
    description: "Write or append to a text file within the workspace",
    inputSchema: {
      type: "object",
      required: ["path", "content"],
      properties: {
        path: { type: "string" },
        content: { type: "string" },
        mode: { type: "string", enum: ["rewrite", "append"] },
      },
      additionalProperties: false,
    },
    async handler(input: any) {
      const full = ensureWithinWorkspace(input.path);
      await fs.mkdir(path.dirname(full), { recursive: true });
      if (input.mode === "append") {
        await fs.appendFile(full, input.content, "utf-8");
      } else {
        await fs.writeFile(full, input.content, "utf-8");
      }
      const stat = await fs.stat(full);
      return { path: full, size: stat.size };
    },
  },
  {
    name: "run_command",
    description:
      "Run a shell command (PowerShell) with workspace-limited cwd and timeout",
    inputSchema: {
      type: "object",
      required: ["command"],
      properties: {
        command: { type: "string" },
        cwd: { type: "string" },
        timeoutSec: { type: "integer", minimum: 1, maximum: 300 },
      },
      additionalProperties: false,
    },
    async handler(input: any) {
      const cwd = input.cwd ? ensureWithinWorkspace(input.cwd) : WORKSPACE_ROOT;
      const res = await runPwsh(input.command, cwd, input.timeoutSec || 30);
      return { cwd, ...res };
    },
  },
  {
    name: "notify",
    description: "Log a message on the MCP server (for debugging/keepalive)",
    inputSchema: {
      type: "object",
      required: ["message"],
      properties: { message: { type: "string" } },
      additionalProperties: false,
    },
    async handler(input: any) {
      console.log(`[MCP notify] ${input.message}`);
      return { ok: true, message: input.message, host: os.hostname() };
    },
  },
];

// HTTP server for /health and to host WS upgrade
const httpServer = createServer();

httpServer.on("request", async (req, res) => {
  // Basic CORS for dev
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "content-type, authorization, x-requested-with"
  );
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.end();
    return;
  }
  if (
    req.method === "GET" &&
    (req.url === "/health" || req.url?.startsWith("/health?"))
  ) {
    res.statusCode = 200;
    res.setHeader("content-type", "application/json");
    res.end(JSON.stringify({ ok: true, port: PORT, root: WORKSPACE_ROOT }));
    return;
  }
  res.statusCode = 404;
  res.end("Not Found");
});

// WebSocket server implementing minimal MCP over JSON-RPC 2.0
type JSONRPCMessage = {
  jsonrpc: "2.0";
  id?: number | string;
  method?: string;
  params?: any;
  result?: any;
  error?: { code: number; message: string; data?: any };
};

const wss = new WebSocketServer({ server: httpServer });

const PROTOCOL_VERSION = "2025-03-26";

function sendJSON(ws: import("ws").WebSocket, msg: JSONRPCMessage) {
  ws.send(JSON.stringify(msg));
}

wss.on("connection", (socket, req) => {
  console.log(`[MCP] WS connection path: ${req.url}`);

  socket.on("message", async (data) => {
    let msg: JSONRPCMessage;
    try {
      msg = JSON.parse(data.toString());
    } catch {
      return; // ignore non-JSON
    }
    if (!msg.method) return;
    const id: string | number | undefined = (msg.id as any) ?? undefined;
    const params = msg.params ?? {};
    try {
      switch (msg.method) {
        case "initialize": {
          const result = {
            protocolVersion: PROTOCOL_VERSION,
            capabilities: { tools: {} },
            serverInfo: { name: "dawsheet-mcp", version: "0.1.0" },
          };
          return sendJSON(socket, { jsonrpc: "2.0", id, result });
        }
        case "ping": {
          return sendJSON(socket, { jsonrpc: "2.0", id, result: {} });
        }
        case "tools/list": {
          const list = tools.map((t) => ({
            name: t.name,
            description: t.description,
            inputSchema: t.inputSchema,
          }));
          return sendJSON(socket, {
            jsonrpc: "2.0",
            id,
            result: { tools: list },
          });
        }
        case "tools/call": {
          const { name, arguments: args } = params || {};
          const tool = tools.find((t) => t.name === name);
          if (!tool) {
            return sendJSON(socket, {
              jsonrpc: "2.0",
              id,
              error: { code: -32601, message: `Unknown tool: ${name}` },
            });
          }
          try {
            const value = await tool.handler(args || {});
            const content = [
              {
                type: "text",
                text:
                  typeof value === "string"
                    ? value
                    : JSON.stringify(value, null, 2),
              },
            ];
            return sendJSON(socket, {
              jsonrpc: "2.0",
              id,
              result: { content },
            });
          } catch (err: any) {
            return sendJSON(socket, {
              jsonrpc: "2.0",
              id,
              error: { code: -32000, message: err?.message || String(err) },
            });
          }
        }
        default: {
          return sendJSON(socket, {
            jsonrpc: "2.0",
            id,
            error: { code: -32601, message: `Method not found: ${msg.method}` },
          });
        }
      }
    } catch (err: any) {
      return sendJSON(socket, {
        jsonrpc: "2.0",
        id,
        error: { code: -32603, message: err?.message || String(err) },
      });
    }
  });
});

httpServer.listen(PORT, () => {
  console.log(
    `[MCP] HTTP+WS listening on http://localhost:${PORT} (all paths)`
  );
  console.log(`[MCP] workspace root: ${WORKSPACE_ROOT}`);
});

httpServer.on("error", (err) => {
  console.error(`[MCP] HTTP server error:`, err);
});

wss.on("error", (err) => {
  console.error(`[MCP] WS server error:`, err);
});

process.on("uncaughtException", (err) => {
  console.error(`[MCP] Uncaught exception:`, err);
});

process.on("unhandledRejection", (reason) => {
  console.error(`[MCP] Unhandled rejection:`, reason);
});
