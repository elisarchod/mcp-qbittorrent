# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP-based Model Context Protocol server that provides direct interaction with qBittorrent's Web API. The MCP server runs as a container alongside qbittorrent in a docker compose stack.

**CRITICAL**: This project is initialized and deployed via Docker Compose from the start. All development and production deployment use containerized workflows. Do NOT develop locally first - create Dockerfile and docker-compose.yml BEFORE writing Python code.

## Technology Stack

- **Python 3.11+**: Async/await, structural pattern matching
- **FastMCP 0.2+**: Decorator-based MCP server framework
- **aiohttp**: Async HTTP client for qBittorrent Web API
- **Pydantic v2**: Data validation and settings management
- **uv**: Fast Python package manager and project setup

## Project Structure

```
mcp-qbittorrent/
├── Dockerfile                  # MCP server container (CREATE FIRST)
├── docker-compose.yml          # Standalone deployment config (CREATE FIRST)
├── pyproject.toml              # uv project config
├── src/
│   └── mcp_qbittorrent/
│       ├── server.py           # FastMCP server entry point
│       ├── config.py           # Pydantic settings
│       ├── tools/
│       │   └── qbittorrent_tools.py   # qBittorrent API tools
│       ├── clients/
│       │   └── qbittorrent_client.py  # qBittorrent API client
│       └── models/
│           └── schemas.py      # Pydantic models
└── tests/
    ├── test_qbittorrent_tools.py
    └── fixtures.py
```

## Development Commands

### Container-based Development (PRIMARY METHOD)

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

### Local Development (ONLY for quick testing)

```bash
# Initialize uv project
uv init mcp-qbittorrent

# Add dependencies
uv add fastmcp aiohttp pydantic pydantic-settings

# Run tests
uv run pytest

# Run server
uv run python -m mcp_qbittorrent.server
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

## MCP Tools

The server exposes 6 qBittorrent Web API tools:
1. `qb_search_torrents`: Search for torrents through qBittorrent's search plugins
2. `qb_add_torrent`: Add torrent by URL or magnet link
3. `qb_list_torrents`: List all torrents with status
4. `qb_torrent_info`: Get detailed info for specific torrent
5. `qb_control_torrent`: Control torrent (pause/resume/delete)
6. `qb_get_preferences`: Get qBittorrent settings

All tools are implemented in `src/mcp_qbittorrent/tools/qbittorrent_tools.py` using FastMCP decorators.

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

### qBittorrent Client (clients/qbittorrent_client.py)
- Handles authentication with qBittorrent Web API
- Manages session cookies (SID)
- Provides async methods for all API operations
- Uses aiohttp for HTTP requests

### Testing Strategy
- Unit tests: Mock qBittorrent API responses
- Integration tests: Use real qBittorrent instance in container (marked with `@pytest.mark.integration`)
- E2E tests: Test via MCP protocol from host to container

## Development Workflow

### Phase Order (MUST FOLLOW)
1. **Project Setup**: Create Dockerfile and docker-compose.yml FIRST, then initialize uv project
2. **Core Implementation**: Implement in container, test via `docker-compose restart`
3. **Testing**: Run tests via `docker-compose exec`
4. **Integration**: Update `build/docker-compose.yml` to include mcp-qbittorrent service
5. **Documentation**: Update README.md with MCP server info

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
