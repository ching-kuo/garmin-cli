# Changelog

## [1.2.0] - 2026-04-07

### Added
- MCP server mode (`garmin-cli mcp-server`) exposing 19 read-only tools for Claude Code/Desktop integration
- SSE and streamable-http transports for remote MCP clients (`--transport sse|streamable-http`)
- HTTP transport options: `--host`, `--port`, `--sse-path`, `--message-path`, `--streamable-http-path`, `--stateless-http`, `--json-response`
- Transport-aware option validation (rejects HTTP-only options on stdio, cross-transport options between SSE/streamable-http)
- Optional `mcp` dependency group (`pip install "garmin-cli[mcp]"`)
- `login_status` MCP tool for checking auth state without CLI
- MCP Server documentation in SKILL.md and README.md

### Changed
- Upgraded MCP SDK from v1 FastMCP to v2 MCPServer (pinned to pre-release commit until v2 is published on PyPI)
- Narrowed import error handling in `mcp-server` CLI command to only catch mcp-related failures

## [1.1.0] - 2026-03-22

### Added
- Estimated metrics, target validation, and fixed END_CONDITIONS IDs for workout builder

### Changed
- Refactored codebase: removed dead code, consolidated helpers, split cell formatting
- Removed 104 over-engineered tests (683 to 579)

## [1.0.0] - 2026-03-20

### Added
- Initial release with health, activity, workout, and performance commands
- Login command with session management and secure directory handling
- JSON, CSV, and table output formats
- Workout CRUD commands (create, update, delete, schedule)
- SKILL.md for agent/LLM tool integration
- E2E test suite against real Garmin Connect API
- MIT license
