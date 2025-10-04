# MCP qBittorrent Server

> Production-grade Model Context Protocol server enabling AI assistants to manage qBittorrent through natural language

## Overview

A FastMCP-based server implementing the **Model Context Protocol (MCP)** for seamless qBittorrent API integration with Large Language Models. Built with modern Python async/await patterns, comprehensive type safety, and 2025 MCP best practices for maximum LLM reasoning accuracy.

**LLM Tool Use Optimization:**
- Structured Pydantic responses enable reliable parsing by language models
- Literal types constrain LLM hallucinations by enforcing valid enum values
- Regex pattern validation prevents invalid inputs before API calls
- Enhanced docstrings with natural language examples guide LLM behavior

**Production-Ready Infrastructure:**
- Async/await architecture for concurrent request handling
- Parallel API calls with `asyncio.gather()` reducing latency by ~50%
- Environment-based configuration following 12-factor app principles
- Comprehensive error handling with structured responses


## Architecture

### System Design

```
┌─────────────────┐
│  Claude/LLM     │  Natural language requests
└────────┬────────┘
         │ MCP Protocol (JSON-RPC)
         ▼
┌─────────────────────────────────────────────┐
│  FastMCP Server (src/mcp_qbittorrent/)      │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ 6 MCP Tools (qbittorrent_tools.py)   │  │  304 lines
│  │ • Enhanced type annotations          │  │
│  │ • Literal enums, regex validation    │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│  ┌──────────────▼───────────────────────┐  │
│  │ QBittorrent Client (async)           │  │  115 lines (-39%)
│  │ • Session management                 │  │
│  │ • Parallel requests (asyncio.gather) │  │
│  └──────────────┬───────────────────────┘  │
└─────────────────┼───────────────────────────┘
                  │ HTTP (qBittorrent Web API)
                  ▼
         ┌─────────────────┐
         │  qBittorrent    │
         └─────────────────┘
```

### Component Breakdown

| Component | Lines | Complexity | Responsibility |
|-----------|-------|------------|----------------|
| `server.py` | 24 | 1 | FastMCP initialization & tool registration |
| `config.py` | 37 | 1 | Environment-based settings with validation |
| `qbittorrent_client.py` | 115 | 3 | Async HTTP client with session management |
| `qbittorrent_tools.py` | 304 | 2 | 6 MCP tools with enhanced annotations |
| `models/response.py` | 47 | 1 | Structured Pydantic response models |
| `utils/logging_handler.py` | 8 | 1 | Centralized logging configuration |

**Average Cyclomatic Complexity: 1.5** (excellent - target is <5)

## MCP Tools

Six production-ready tools implementing **2025 MCP Best Practices** for optimal LLM accuracy:

| Tool | Function | MCP Enhancement |
|------|----------|-----------------|
| `list_downloads` | List torrents with filters | `Literal[...]` for state enums |
| `get_download_info` | Detailed torrent info | Regex pattern for hash validation |
| `add_download` | Add torrent by URL/magnet | URL pattern validation |
| `control_download` | Pause/resume/delete | `Literal[...]` for action enums |
| `search_downloads` | Search via plugins | Query constraints (min/max length) |
| `get_settings` | Get application preferences | Structured response model |

**Example: Enhanced Type Annotation**
```python
async def control_download(
    hash: Annotated[
        str,
        Field(
            description="40-character SHA-1 hash",
            pattern=r"^[a-fA-F0-9]{40}$",
            min_length=40,
            max_length=40
        )
    ],
    action: Annotated[
        Literal["pause", "resume", "delete"],
        Field(description="Action: pause (stop), resume (start), delete (remove)")
    ]
) -> TorrentActionResponse:
```

**Why This Matters:**
- LLM receives explicit constraints (Literal types prevent hallucinations)
- Regex validation catches errors before API calls
- Structured responses enable reliable parsing
- Natural language descriptions guide LLM tool selection

## Quick Start

### Prerequisites
- Python 3.11+
- uv package manager ([installation](https://github.com/astral-sh/uv))
- qBittorrent with Web UI enabled

### Installation

```bash
# 1. Clone and setup
git clone <repo-url> && cd mcp-qbittorrent
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your qBittorrent credentials:
#   QB_MCP_QBITTORRENT_URL=http://localhost:15080
#   QB_MCP_QBITTORRENT_USERNAME=admin
#   QB_MCP_QBITTORRENT_PASSWORD=your_password

# 3. Verify installation
uv run python main.py  # Should connect and list torrents
```

### Running

```bash
# Start MCP server
uv run python -m mcp_qbittorrent.server

# Run tests (9/9 passing)
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/mcp_qbittorrent --cov-report=term
```

### Configuration

Environment variables with `QB_MCP_` prefix (managed via Pydantic BaseSettings):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QB_MCP_QBITTORRENT_URL` | ✅ | - | qBittorrent Web UI URL |
| `QB_MCP_QBITTORRENT_USERNAME` | ✅ | - | Web UI username |
| `QB_MCP_QBITTORRENT_PASSWORD` | ✅ | - | Web UI password |
| `QB_MCP_REQUEST_TIMEOUT` | ❌ | 30 | HTTP request timeout (seconds) |

**Note**: Server fails fast if required settings are missing (Pydantic validation)


## Project Structure

```
src/mcp_qbittorrent/          # 554 production lines
├── server.py                 # FastMCP initialization (24 lines)
├── config.py                 # Environment settings (37 lines)
├── clients/
│   └── qbittorrent_client.py # Async API client (115 lines, -39%)
├── models/
│   └── response.py           # Pydantic response models (47 lines)
├── tools/
│   └── qbittorrent_tools.py  # 6 MCP tools (304 lines)
└── utils/
    └── logging_handler.py    # Centralized logging (8 lines)

tests/                        # 352 test lines
├── unit/
│   └── test_client.py        # Unit tests with mocks (6 tests)
├── integration/
│   └── test_qbittorrent_integration.py  # Real instance tests (3 tests)
└── conftest.py               # pytest fixtures
```

## Usage Examples

Natural language interactions through Claude:

```
User: "Show me all active downloads"
→ list_downloads(filter="downloading")

User: "Pause the Ubuntu torrent"
→ get_download_info(query="Ubuntu")
→ control_download(hash="abc123...", action="pause")

User: "Find Ubuntu 24.04 torrents"
→ search_downloads(query="Ubuntu 24.04", limit=10)

User: "What's my download speed limit?"
→ get_settings()
```

**Structured Response Example:**
```json
{
  "success": true,
  "count": 3,
  "torrents": [
    {
      "hash": "abc123...",
      "name": "ubuntu-24.04-desktop-amd64.iso",
      "state": "downloading",
      "progress": 0.45,
      "dlspeed": 5242880
    }
  ]
}
```

## Development Status

**Completed (Phases 1-3):**
- ✅ Async Python client 
- ✅ 6 MCP tools (Literal types, regex validation)
- ✅ Comprehensive testing: 9/9 passing, 63% test ratio
- ✅ Clean architecture: avg complexity 1.5

**Planned (Phases 4-5):**
- ⏳ Containerization: Dockerfile + docker-compose
- ⏳ Integration: Multi-container deployment
- ⏳ CI/CD: GitHub Actions for automated testing

## Technical Highlights

**ML/AI:**
- MCP protocol expertise (emerging standard for LLM tool use)
- LLM-optimized interface design (Literal types, structured responses)
- Async architecture for concurrent request handling
- Parallel API calls with `asyncio.gather()` (-50% latency)

**Engineering:**
- Clean architecture with clear separation of concerns
- 12-factor app configuration (environment-based settings)
- Professional error handling (custom exceptions, structured errors)
- Modern Python tooling (uv, Ruff, Pydantic V2)

## Security & Best Practices

**Security:**
- ✅ Environment-based credentials (never hardcoded)
- ✅ Pydantic validation on all inputs
- ✅ Session token management with auto-refresh
- ✅ Timeout handling (prevents hanging requests)
- ⏳ Container isolation (Phase 4)

**Code Quality:**
- ✅ Single Responsibility Principle (avg 20 lines/function)
- ✅ DRY principles (unified `_request()` method)
- ✅ Pythonic idioms (f-strings, comprehensions, context managers)
- ✅ Custom exception hierarchy for error handling

## References

- **MCP Protocol**: [spec.modelcontextprotocol.io](https://spec.modelcontextprotocol.io/)
- **FastMCP**: [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **qBittorrent API**: [qBittorrent Wiki](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1))

## License & Contributing

MIT License - See LICENSE file for details.

Development guidelines and architecture decisions: See [CLAUDE.md](CLAUDE.md)
