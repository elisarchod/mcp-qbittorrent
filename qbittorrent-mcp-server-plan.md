# qBittorrent MCP Server Plan

## Overview

Create a FastMCP-based Model Context Protocol server that provides direct interaction with qBittorrent's Web API through Claude. The MCP server will run as a container alongside qbittorrent in the existing docker compose stack.

**IMPORTANT**: Development will start locally with the Python client and MCP server, then containerized for deployment via Docker Compose.

## Architecture

### Technology Stack

- **Python 3.11+**: Modern async/await, structural pattern matching
- **FastMCP 0.2+**: Decorator-based MCP server framework
- **aiohttp**: Async HTTP client for qBittorrent Web API
- **Pydantic v2**: Data validation and settings management
- **uv**: Fast Python package manager and project setup

### Container Architecture

```
┌─────────────────────────────────────────┐
│   turtle-mcp-qbittorrent (container)   │
│                                         │
│  ┌─────────────────────────────────┐  │
│  │     FastMCP Server              │  │
│  │  - qBittorrent API Tools        │  │
│  │  - MCP Protocol Handler         │  │
│  └─────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
         │
         │ HTTP (qBittorrent Web API)
         │
         ▼
┌──────────────────┐
│  qbittorrent     │
│  (container)     │
└──────────────────┘
```

## MCP Tools Design

### qBittorrent Web API Tools

#### `qb_search_torrents`
- **Description**: Search for torrents through qBittorrent's search plugins
- **Parameters**: `query`, `category` (optional), `plugins` (optional)
- **Returns**: List of search results with name, size, seeders, link

#### `qb_add_torrent`
- **Description**: Add torrent by URL or magnet link
- **Parameters**: `url`, `save_path` (optional), `category` (optional)
- **Returns**: Torrent hash and status

#### `qb_list_torrents`
- **Description**: List all torrents with status
- **Parameters**: `filter` (all/downloading/completed/paused), `category` (optional)
- **Returns**: List of torrents with progress, speed, ETA

#### `qb_torrent_info`
- **Description**: Get detailed info for specific torrent
- **Parameters**: `hash`
- **Returns**: Full torrent details including files, trackers, peers

#### `qb_control_torrent`
- **Description**: Control torrent (pause/resume/delete)
- **Parameters**: `hash`, `action` (pause/resume/delete), `delete_files` (bool)

#### `qb_get_preferences`
- **Description**: Get qBittorrent settings
- **Returns**: Download limits, default paths, connection settings

## Project Structure

```
mcp-qbittorrent/
├── Dockerfile                  # MCP server container (create after core implementation)
├── docker-compose.yml          # Standalone deployment config (create after core implementation)
├── pyproject.toml              # uv project config
├── README.md
├── src/
│   └── mcp_qbittorrent/
│       ├── __init__.py
│       ├── server.py           # FastMCP server entry point
│       ├── config.py           # Pydantic settings
│       ├── tools/
│       │   ├── __init__.py
│       │   └── qbittorrent_tools.py   # qBittorrent API tools
│       ├── clients/
│       │   ├── __init__.py
│       │   └── qbittorrent_client.py  # qBittorrent API client
│       └── models/
│           ├── __init__.py
│           └── schemas.py      # Pydantic models
└── tests/
    ├── __init__.py
    ├── test_qbittorrent_tools.py
    └── fixtures.py
```

## Implementation Details

### FastMCP Server Setup

```python
from fastmcp import FastMCP
from mcp_qbittorrent.tools import qbittorrent_tools

mcp = FastMCP("qbittorrent-manager")

# Register qBittorrent API tools
qbittorrent_tools.register(mcp)

if __name__ == "__main__":
    mcp.run()
```

### qBittorrent Client Wrapper

```python
import aiohttp
from typing import Optional

class QBittorrentClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookie: Optional[str] = None

    async def login(self):
        """Authenticate with qBittorrent Web API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v2/auth/login",
                data={"username": self.username, "password": self.password}
            ) as resp:
                if resp.status == 200:
                    self.cookie = resp.cookies.get("SID").value

    async def search_torrents(self, query: str, plugins: str = "all", category: str = "all"):
        """Search for torrents"""
        # Implementation using /api/v2/search/start
        pass
```

### Configuration Management

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # qBittorrent settings
    qbittorrent_url: str = Field(default="http://localhost:15080")
    qbittorrent_username: str = Field(default="admin")
    qbittorrent_password: str = Field(default="adminadmin")  # qBittorrent WebUI password (username: admin)

    class Config:
        env_file = ".env"
        env_prefix = "QB_MCP_"
```

## Dockerfile Design

```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Run server
CMD ["uv", "run", "python", "-m", "mcp_qbittorrent.server"]
```

## Docker Compose Integration

Add to existing `build/docker-compose.yml`:

```yaml
services:
  mcp-qbittorrent:
    build:
      context: ../mcp-qbittorrent
      dockerfile: Dockerfile
    container_name: turtle-mcp-qbittorrent
    environment:
      - QB_MCP_QBITTORRENT_URL=http://localhost:15080
      - QB_MCP_QBITTORRENT_USERNAME=${QB_USERNAME:-admin}
      - QB_MCP_QBITTORRENT_PASSWORD=${QB_PASSWORD:-adminadmin}  # qBittorrent WebUI password (username: admin)
    networks:
      - turtle-network
    depends_on:
      - qbittorrent
```

## Development Workflow

### Phase 1: Local Development Setup
1. Create new branch: `feature/mcp-qbittorrent-server`
2. Initialize uv project: `uv init mcp-qbittorrent`
3. Add dependencies: `fastmcp`, `aiohttp`, `pydantic`, `pydantic-settings`
4. Create project structure with directories for src, tools, clients, models

### Phase 2: Core Client Implementation
1. Implement qBittorrent API client with authentication
2. Test client against local qBittorrent instance (http://localhost:15080)
3. Create Pydantic models for API responses
4. Add comprehensive error handling and logging

### Phase 3: MCP Tools Implementation
1. Create FastMCP server entry point
2. Implement FastMCP tool decorators for all qBittorrent operations
3. Test tools locally via MCP protocol
4. Run tests: `uv run pytest`

### Phase 4: Containerization
1. Create `Dockerfile` for MCP server
2. Create `docker-compose.yml` for standalone deployment
3. Build and test container: `docker-compose build && docker-compose up`
4. Verify container can communicate with qBittorrent container

### Phase 5: Integration with Existing Stack
1. Update `build/docker-compose.yml` to include mcp-qbittorrent service
2. Configure networking between mcp-qbittorrent and qbittorrent containers
3. Test full stack orchestration: `cd build && docker-compose up -d`

### Phase 6: Documentation
1. Update main README.md with MCP server info
2. Create usage examples for Claude Desktop
3. Document all MCP tools with examples
4. Document docker-compose deployment steps

## Security Considerations

1. **Credentials**: Never hardcode qBittorrent credentials, use environment variables
2. **Input Validation**: Validate all torrent URLs and hashes before passing to qBittorrent
3. **Rate Limiting**: Implement rate limiting for API calls to prevent abuse
4. **Container Isolation**: Run MCP server with minimal privileges
5. **Network Isolation**: Only expose MCP server on internal docker network

## Testing Strategy

```python
# Example test structure
import pytest
from mcp_qbittorrent.clients.qbittorrent_client import QBittorrentClient

@pytest.mark.asyncio
async def test_qbittorrent_login(mock_qb_client):
    client = QBittorrentClient(
        base_url="http://localhost:15080",
        username="admin",
        password="adminadmin"  # qBittorrent WebUI password (username: admin)
    )
    await client.login()
    assert client.cookie is not None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_qbittorrent_search(real_qb_client):
    results = await real_qb_client.search_torrents("ubuntu")
    assert len(results) > 0
    assert all("name" in r and "size" in r for r in results)
```

## Success Metrics

1. **Functionality**: All 8 qBittorrent API MCP tools working correctly
2. **Performance**: API calls respond in <500ms
3. **Reliability**: 99%+ uptime for MCP server
4. **Integration**: Runs alongside qbittorrent in docker compose stack
5. **User Experience**: Claude can interact with qBittorrent without direct API knowledge

## Future Enhancements

1. **Advanced Monitoring**: Grafana/Prometheus metrics for torrent activity
2. **Notification Tools**: MCP tools for torrent completion events
3. **Multi-Instance Support**: Manage multiple qBittorrent instances
4. **Batch Operations**: Add multiple torrents, bulk pause/resume
5. **Smart Categories**: Auto-categorization based on content analysis
6. **Storage Management**: Tools for managing download paths and disk usage

## References

- FastMCP Documentation: https://github.com/jlowin/fastmcp
- qBittorrent Web API: https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
- Docker SDK for Python: https://docker-py.readthedocs.io/
- MCP Protocol Specification: https://spec.modelcontextprotocol.io/
