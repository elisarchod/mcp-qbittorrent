# Docker Compose Setup for MCP qBittorrent Server

Simple Docker setup to run both qBittorrent and the MCP server together.

## Quick Start

### 1. Create docker-compose.yml

do it in build dir

```yaml
name: turtle-media

services:
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - QBITTORRENT_PASSWORD=$QBITTORRENT_PASSWORD
    volumes:
      - qbittorrent-config:/config
      - qbittorrent-downloads:/downloads
    ports:
      - 6881:6881
      - 6881:6881/udp
      - 15080:8080
    restart: unless-stopped
    networks:
      - media-network

  mcp-qbittorrent:
    image: python:3.11-slim
    container_name: mcp-qbittorrent
    environment:
      - QB_MCP_QBITTORRENT_URL=http://qbittorrent:8080
      - QB_MCP_QBITTORRENT_USERNAME=admin
      - QB_MCP_QBITTORRENT_PASSWORD=$QBITTORRENT_PASSWORD
    volumes:
      - .:/app
    working_dir: /app
    command: >
      sh -c "pip install uv --break-system-packages && 
             uv sync --frozen && 
             uv run python -m mcp_qbittorrent.server"
    depends_on:
      - qbittorrent
    restart: unless-stopped
    networks:
      - media-network

networks:
  media-network:
    driver: bridge

volumes:
  qbittorrent-config:
  qbittorrent-downloads:
```

### 2. Create .env file

```bash
QBITTORRENT_PASSWORD=your_secure_password_here
```

## Usage

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access

- **qBittorrent Web UI**: http://localhost:15080 (admin / your_password)
- **MCP Server**: Internal network only (connects to qBittorrent automatically)

## Connect AI Assistant

```json
{
  "mcpServers": {
    "qbittorrent": {
      "command": "docker",
      "args": ["exec", "mcp-qbittorrent", "uv", "run", "python", "-m", "mcp_qbittorrent.server"]
    }
  }
}
```

## Troubleshooting

**MCP server can't connect to qBittorrent:**
```bash
docker-compose exec mcp-qbittorrent ping qbittorrent
```

**View logs:**
```bash
docker-compose logs mcp-qbittorrent
```
