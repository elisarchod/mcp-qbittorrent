# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP-based Model Context Protocol server that provides direct interaction with qBittorrent's Web API. The MCP server runs as a container alongside qbittorrent in a docker compose stack.

**Current Status**: Phase 2 complete - Core qBittorrent API client fully implemented and tested. Ready for Phase 3 (MCP tools implementation).

## Technology Stack

- **Python 3.11+**: Async/await, structural pattern matching
- **FastMCP 0.2+**: Decorator-based MCP server framework
- **aiohttp**: Async HTTP client for qBittorrent Web API
- **Pydantic v2**: Data validation and settings management
- **uv**: Fast Python package manager and project setup

## Project Structure

```
mcp-qbittorrent/
├── Dockerfile                  # MCP server container (Phase 4 - pending)
├── docker-compose.yml          # Standalone deployment config (Phase 4 - pending)
├── pyproject.toml              # uv project config ✅
├── main.py                     # Client test script ✅
├── src/
│   └── mcp_qbittorrent/
│       ├── server.py           # FastMCP server entry point (Phase 3 - pending)
│       ├── config.py           # Pydantic settings ✅ (38 lines)
│       ├── tools/
│       │   └── qbittorrent_tools.py   # qBittorrent API tools (Phase 3 - pending)
│       ├── clients/
│       │   └── qbittorrent_client.py  # qBittorrent API client ✅ (251 lines)
│       └── models/
│           └── schemas.py      # Pydantic models ✅ (129 lines)
└── tests/
    ├── test_qbittorrent_tools.py
    └── fixtures.py
```

## Development Commands

### Local Development (Current Phase)

```bash
# Test qBittorrent client
uv run python main.py

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy src/

# Run MCP server (once implemented)
uv run python -m mcp_qbittorrent.server
```

### Container-based Development (Phase 4+)

```bash
# Build container
docker-compose build mcp-qbittorrent

# Start service
docker-compose up mcp-qbittorrent

# Restart after code changes
docker-compose restart mcp-qbittorrent

# Run tests in container
docker-compose exec mcp-qbittorrent uv run pytest

# View logs
docker-compose logs -f mcp-qbittorrent

# Full stack with existing services
cd build && docker-compose up -d
```

## Architecture

### Container Communication

```
turtle-mcp-qbittorrent (container)
    │
    │ HTTP (qBittorrent Web API)
    │
    ▼
qbittorrent (container)
```

### Configuration

Configuration is managed via environment variables with `QB_MCP_` prefix:
- `QB_MCP_QBITTORRENT_URL`: qBittorrent Web API URL (default: http://qbittorrent:15080)
- `QB_MCP_QBITTORRENT_USERNAME`: qBittorrent username (default: admin)
- `QB_MCP_QBITTORRENT_PASSWORD`: qBittorrent password (default: adminadmin)

Settings are defined in `src/mcp_qbittorrent/config.py` using Pydantic BaseSettings.

## MCP Tools (Phase 3 - To Be Implemented)

The server will expose 6 qBittorrent Web API tools:
1. `qb_search_torrents`: Search for torrents through qBittorrent's search plugins
2. `qb_add_torrent`: Add torrent by URL or magnet link
3. `qb_list_torrents`: List all torrents with status
4. `qb_torrent_info`: Get detailed info for specific torrent
5. `qb_control_torrent`: Control torrent (pause/resume/delete)
6. `qb_get_preferences`: Get qBittorrent settings

Tools will be implemented in `src/mcp_qbittorrent/tools/qbittorrent_tools.py` using FastMCP decorators.

### qBittorrent Client (✅ Implemented)

The `QBittorrentClient` class in `clients/qbittorrent_client.py` provides:
- Authentication with qBittorrent Web API (session cookie management)
- Async context manager support (`async with`)
- 6 core methods mapped to the planned MCP tools:
  - `list_torrents(filter, category)` - for qb_list_torrents
  - `get_torrent_info(hash)` - for qb_torrent_info
  - `add_torrent(urls, savepath, category, paused)` - for qb_add_torrent
  - `control_torrent(hashes, action, delete_files)` - for qb_control_torrent
  - `search_torrents(query, plugins, category, limit)` - for qb_search_torrents
  - `get_preferences()` - for qb_get_preferences
- Comprehensive error handling (AuthenticationError, APIError)
- Proper timeout handling

## Implementation Pattern

### FastMCP Server Entry Point (server.py)
```python
from fastmcp import FastMCP
from mcp_qbittorrent.tools import qbittorrent_tools

mcp = FastMCP("qbittorrent-manager")
qbittorrent_tools.register(mcp)

if __name__ == "__main__":
    mcp.run()
```


### Testing Strategy
- Unit tests: Mock qBittorrent API responses
- Integration tests: Use real qBittorrent instance in container (marked with `@pytest.mark.integration`)
- E2E tests: Test via MCP protocol from host to container

## Development Workflow

### Phase Order (Actual Workflow)

**✅ Phase 1: Project Setup (Complete)**
- uv project initialized with pyproject.toml
- Dependencies added: fastmcp, aiohttp, pydantic, pydantic-settings
- Project structure created with src/ and tests/ directories
- Feature branch created: `feature/mcp-qbittorrent-server`

**✅ Phase 2: Core Client Implementation (Complete)**
- config.py: Pydantic settings with environment variable support (38 lines)
- qbittorrent_client.py: Full async API client implementation (251 lines)
- schemas.py: Pydantic models for all API responses (129 lines)
- main.py: Test script for validating client functionality
- Successfully tested against local qBittorrent instance (http://localhost:15080)

**⏳ Phase 3: MCP Tools Implementation (Next)**
1. Implement `server.py` with FastMCP initialization
2. Create FastMCP tool decorators in `qbittorrent_tools.py` for all 6 operations
3. Wire up tools to use QBittorrentClient methods
4. Add tool parameter validation and descriptions
5. Test tools locally via MCP protocol: `uv run python -m mcp_qbittorrent.server`
6. Run test suite: `uv run pytest`

**⏳ Phase 4: Containerization (After Phase 3)**
1. Create `Dockerfile` for MCP server (use python:3.11-slim base)
2. Create `docker-compose.yml` for standalone deployment
3. Configure environment variables for container
4. Build and test: `docker-compose build && docker-compose up`
5. Verify container-to-container communication with qBittorrent

**⏳ Phase 5: Integration (After Phase 4)**
1. Update `build/docker-compose.yml` to include mcp-qbittorrent service
2. Configure networking between mcp-qbittorrent and qbittorrent containers
3. Test full stack: `cd build && docker-compose up -d`
4. Verify MCP server accessible via Claude Desktop

**✅ Phase 6: Documentation (Updated)**
- README.md: Updated with current project status and usage
- CLAUDE.md: Updated with actual workflow and phase tracking

### Branching
Use feature branch: `feature/mcp-qbittorrent-server`

## Security Considerations

1. **Never hardcode credentials** - use environment variables only
2. **Validate all inputs** - especially torrent URLs and hashes before passing to qBittorrent API
3. **Container isolation** - run MCP server with minimal privileges
4. **Network isolation** - only expose MCP server on internal docker network

## References

- FastMCP: https://github.com/jlowin/fastmcp
- qBittorrent Web API: https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
- MCP Protocol: https://spec.modelcontextprotocol.io/
