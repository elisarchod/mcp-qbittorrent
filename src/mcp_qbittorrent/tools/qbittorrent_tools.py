"""FastMCP tools for qBittorrent Web API."""

import logging
from typing import Optional
from fastmcp import FastMCP
from mcp_qbittorrent.clients.qbittorrent_client import QBittorrentClient


logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, qb_client: QBittorrentClient) -> None:
    """Register all qBittorrent tools with the FastMCP server."""

    @mcp.tool()
    async def qb_list_torrents(
        filter: Optional[str] = None,
        category: Optional[str] = None
    ) -> dict:
        """List all torrents with optional filtering.

        Args:
            filter: Filter torrents by state (all/downloading/completed/paused/active/inactive/resumed)
            category: Filter torrents by category name

        Returns:
            List of torrents with details including hash, name, size, progress, speeds, state, etc.
        """
        try:
            torrents = await qb_client.list_torrents(filter=filter, category=category)
            return {
                "success": True,
                "count": len(torrents),
                "torrents": torrents
            }
        except Exception as e:
            logger.error(f"Error listing torrents: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    async def qb_torrent_info(hash: str) -> dict:
        """Get detailed information for a specific torrent.

        Args:
            hash: The hash of the torrent to get info for

        Returns:
            Detailed torrent properties including files, trackers, peers, and download info
        """
        try:
            info = await qb_client.get_torrent_info(hash=hash)
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            logger.error(f"Error getting torrent info for {hash}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    async def qb_add_torrent(
        url: str,
        save_path: Optional[str] = None,
        category: Optional[str] = None,
        paused: bool = False
    ) -> dict:
        """Add a torrent by URL or magnet link.

        Args:
            url: Torrent URL or magnet link
            save_path: Path to save the torrent files (uses default if not specified)
            category: Category to assign to the torrent
            paused: If True, add torrent in paused state

        Returns:
            Success status and message
        """
        try:
            result = await qb_client.add_torrent(
                urls=url,
                savepath=save_path,
                category=category,
                paused=paused
            )
            return {
                "success": True,
                "message": "Torrent added successfully",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error adding torrent {url}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    async def qb_control_torrent(
        hash: str,
        action: str,
        delete_files: bool = False
    ) -> dict:
        """Control a torrent: pause, resume, or delete.

        Args:
            hash: The hash of the torrent to control
            action: Action to perform (pause/resume/delete)
            delete_files: If True and action is 'delete', also delete downloaded files

        Returns:
            Success status and message
        """
        try:
            result = await qb_client.control_torrent(
                hashes=hash,
                action=action,
                delete_files=delete_files
            )
            return {
                "success": True,
                "message": f"Torrent {action} action completed successfully",
                "result": result
            }
        except Exception as e:
            logger.error(f"Error controlling torrent {hash} with action {action}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    async def qb_search_torrents(
        query: str,
        plugins: str = "all",
        category: str = "all",
        limit: Optional[int] = 100
    ) -> dict:
        """Search for torrents using qBittorrent's search plugins.

        Args:
            query: Search query string
            plugins: Search plugins to use (default: "all" for all enabled plugins)
            category: Search category (default: "all")
            limit: Maximum number of results to return (default: 100)

        Returns:
            Search results with name, size, seeders, leechers, and download link
        """
        try:
            results = await qb_client.search_torrents(
                query=query,
                plugins=plugins,
                category=category,
                limit=limit
            )
            return {
                "success": True,
                "query": query,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error searching torrents with query '{query}': {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @mcp.tool()
    async def qb_get_preferences() -> dict:
        """Get qBittorrent application preferences and settings.

        Returns:
            Application preferences including download limits, paths, connection settings, etc.
        """
        try:
            prefs = await qb_client.get_preferences()
            return {
                "success": True,
                "preferences": prefs
            }
        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            return {
                "success": False,
                "error": str(e)
            }
