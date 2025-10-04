# mcp-qbittorrent

FastMCP-based Model Context Protocol server for qBittorrent Web API integration.

## Overview

This MCP server provides Claude with direct access to qBittorrent's Web API, enabling torrent management, search, and monitoring capabilities through natural language interactions.

## Project Status

**Current Phase: Phase 3 Complete - MCP Tools Implementation (2025 Best Practices)**

- ✅ Phase 1: Project setup with uv, dependencies configured
- ✅ Phase 2: qBittorrent API client simplified and optimized (120 lines, -39%)
- ✅ Phase 3: MCP tools fully implemented with 2025 best practices (22/22 tests passing)
- ⏳ Phase 4: Containerization with Docker (next)
- ⏳ Phase 5: Integration with existing docker-compose stack
- ✅ Phase 6: Documentation updated

## Technology Stack

- **Python 3.11+**: Async/await, type hints
- **FastMCP 2.12.4+**: Decorator-based MCP server framework
- **aiohttp 3.12.15+**: Async HTTP client for qBittorrent Web API
- **Pydantic v2.11.9+**: Data validation, settings, MCP response models
- **uv**: Fast Python package manager

## Architecture

### Components Implemented
```
src/mcp_qbittorrent/
   config.py                         ✅ Pydantic settings with env support (38 lines)
   clients/
      qbittorrent_client.py         ✅ Simplified async API client (120 lines)
   models/
      schemas.py                    ✅ Pydantic models + MCP responses (128 lines)
   server.py                        ✅ FastMCP entry point (37 lines)
   tools/
       qbittorrent_tools.py         ✅ 6 MCP tools w/ 2025 best practices (322 lines)
tests/
   test_qbittorrent_client.py       ✅ Unit tests (22/22 passing)
   test_integration.py              ✅ Integration tests (5 tests)
```

### MCP Tools (Enhanced for LLM Accuracy)

All 6 tools implement **2025 MCP Best Practices**:
- `Annotated[Type, Field(...)]` with detailed descriptions
- `Literal` types for enum values (states, actions)
- Regex patterns for validation (hashes, URLs)
- Structured Pydantic response models
- Enhanced docstrings with use case examples

**Available Tools:**

1. **qb_list_torrents** - List torrents with filtering (Literal filter states)
2. **qb_torrent_info** - Get detailed torrent info (hash validation)
3. **qb_add_torrent** - Add torrents by URL/magnet (URL pattern validation)
4. **qb_control_torrent** - Pause/resume/delete (Literal actions)
5. **qb_search_torrents** - Search via qBittorrent plugins (query constraints)
6. **qb_get_preferences** - Get qBittorrent application settings

## Configuration

**REQUIRED**: All qBittorrent connection settings must be configured via environment variables before running the server.

Configuration uses `QB_MCP_` prefix:

```bash
# .env file (REQUIRED)
QB_MCP_QBITTORRENT_URL=http://localhost:15080    # Required: qBittorrent Web UI URL
QB_MCP_QBITTORRENT_USERNAME=admin                # Required: Web UI username
QB_MCP_QBITTORRENT_PASSWORD=your_password        # Required: Web UI password
QB_MCP_REQUEST_TIMEOUT=30                        # Optional: Request timeout (default: 30s)
```

**Note**: The server will fail to start if required settings are missing. Copy `.env.example` to `.env` and configure your qBittorrent credentials.

Settings are managed in `src/mcp_qbittorrent/config.py` using Pydantic BaseSettings with strict validation.

## Quick Start

### Prerequisites

- **Python 3.11+**
- **uv** package manager
- **qBittorrent** with Web UI enabled
- **qBittorrent credentials** (username and password for Web UI)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd mcp-qbittorrent

# Create virtual environment and install dependencies
uv sync

# Configure environment (REQUIRED)
cp .env.example .env
nano .env  # Edit with your qBittorrent settings

# .env should contain:
#   QB_MCP_QBITTORRENT_URL=http://localhost:15080
#   QB_MCP_QBITTORRENT_USERNAME=admin
#   QB_MCP_QBITTORRENT_PASSWORD=your_password
```

### Running the MCP Server

```bash
# Run the MCP server
uv run python -m mcp_qbittorrent.server

# Or use the main test script to verify client works
uv run python main.py
```

Expected output when running main.py:
```
INFO:__main__:Connecting to qBittorrent at http://localhost:15080
INFO:mcp_qbittorrent.clients.qbittorrent_client:Successfully authenticated with qBittorrent
INFO:__main__:Number of torrents: 3
INFO:__main__:Default save path: /downloads
INFO:__main__:✅ Client test completed successfully!
```

### Working with the Environment

```bash
# Install/sync dependencies
uv sync

# Run scripts
uv run python main.py
uv run python -m mcp_qbittorrent.server

# Run tests
uv run pytest
uv run pytest -v
uv run pytest tests/test_qbittorrent_client.py

# Add dependencies
uv add fastmcp
uv add --dev pytest

# Recreate environment from scratch
rm -rf .venv
uv sync
```

### Testing

The project includes comprehensive unit and integration tests:

```bash
# Run all tests (22 tests)
uv run pytest -v

# Run specific test categories
uv run pytest tests/test_qbittorrent_client.py -v  # Client tests (17 tests)
uv run pytest tests/test_integration.py -v         # Integration tests (5 tests)

# Run with coverage report
uv run pytest --cov=src/mcp_qbittorrent --cov-report=term
```

**Test Coverage**: 22/22 tests passing ✅
- Authentication and session management
- All 6 torrent operations (list, info, add, control, search, preferences)
- Error handling (auth failures, API errors, timeouts)
- Integration tests with real qBittorrent instance

**Troubleshooting**:
- `ValidationError` → Check `.env` file has all required variables
- `AuthenticationError` → Verify qBittorrent credentials and URL
- `Connection refused` → Ensure qBittorrent Web UI is running and accessible
- `Module not found` → Run `uv sync` to install dependencies

## Project Structure

```
mcp-qbittorrent/
├── pyproject.toml              # uv project configuration ✅
├── uv.lock                     # Locked dependencies ✅
├── .env                        # Environment configuration (create from .env.example)
├── main.py                     # Client test script ✅
├── src/
│   └── mcp_qbittorrent/
│       ├── __init__.py
│       ├── config.py           # Pydantic settings ✅ (38 lines)
│       ├── server.py           # FastMCP entry point ✅ (37 lines)
│       ├── clients/
│       │   ├── __init__.py
│       │   └── qbittorrent_client.py  # Simplified API client ✅ (120 lines)
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py      # Pydantic models + MCP responses ✅ (128 lines)
│       └── tools/
│           ├── __init__.py
│           └── qbittorrent_tools.py  # 6 MCP tools ✅ (322 lines)
├── tests/
│   ├── __init__.py
│   ├── fixtures.py             # Test fixtures and mock data
│   ├── test_qbittorrent_client.py  # Unit tests ✅ (17 tests)
│   ├── test_integration.py         # Integration tests ✅ (5 tests)
│   └── test_qbittorrent_tools.py   # MCP tools tests (empty)
├── CLAUDE.md                   # Project instructions for Claude Code
├── qbittorrent-mcp-server-plan.md   # Detailed phase tracking
└── README.md                   # This file
```

## Using the MCP Server with Claude

Once the server is running, Claude can interact with your qBittorrent instance using natural language:

**Example interactions:**
- "Show me all my torrents"
- "What's currently downloading?"
- "Add this magnet link: magnet:?xt=..."
- "Pause the Ubuntu torrent"
- "Search for Ubuntu 24.04 torrents"
- "What's my download speed limit?"

The server uses **2025 MCP Best Practices** for maximum LLM accuracy with structured responses, type validation, and clear error messages.

## Error Handling

Comprehensive error handling with custom exceptions:

- **AuthenticationError**: Login fails or token expires
- **APIError**: API requests fail (with HTTP status codes)
- **QBittorrentClientError**: Base exception for all client errors

All methods include timeout handling, connection error recovery, and informative error messages with troubleshooting hints.

## Next Steps

### ✅ Phase 3: MCP Tools - COMPLETE
- All 6 tools implemented with 2025 best practices
- Enhanced type annotations and validation
- Structured Pydantic response models
- 22/22 tests passing

### ⏳ Phase 4: Containerization - NEXT

```bash
# Create Dockerfile
# Create docker-compose.yml for standalone deployment
# Build and test: docker-compose build && docker-compose up
```

### ⏳ Phase 5: Integration

```bash
# Update build/docker-compose.yml to include mcp-qbittorrent service
# Configure networking between containers
# Test full stack: cd build && docker-compose up -d
```

## Security Considerations

-  Credentials via environment variables only (never hardcoded)
-  Input validation with Pydantic models
-  Proper authentication token management
-  Timeout handling to prevent hanging requests
- � Container isolation (pending Phase 4)
- � Network isolation on internal docker network (pending Phase 4)

## Dependencies

Core dependencies (from pyproject.toml):
- **aiohttp** >= 3.12.15 - Async HTTP client
- **fastmcp** >= 2.12.4 - MCP server framework
- **pydantic** >= 2.11.9 - Data validation
- **pydantic-settings** >= 2.11.0 - Settings management

Dev dependencies:
- **pytest** >= 8.0.0 - Testing framework
- **pytest-asyncio** >= 0.23.0 - Async test support
- **pytest-cov** >= 4.1.0 - Coverage reporting
- **ruff** >= 0.3.0 - Linting
- **mypy** >= 1.8.0 - Type checking

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [qBittorrent Web API](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1))
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)

## License

See LICENSE file for details.

## Contributing

See CLAUDE.md for development guidelines and architecture decisions.
