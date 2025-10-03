"""Test script for qBittorrent client."""

import asyncio
import logging
from src.mcp_qbittorrent.clients.qbittorrent_client import QBittorrentClient
from src.mcp_qbittorrent.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_client():
    """Test qBittorrent client connection and basic operations."""
    logger.info(f"Connecting to qBittorrent at {settings.qbittorrent_url}")

    async with QBittorrentClient(
        base_url=settings.qbittorrent_url,
        username=settings.qbittorrent_username,
        password=settings.qbittorrent_password,
        timeout=settings.request_timeout
    ) as client:
        # Test listing torrents
        torrents = await client.list_torrents()
        logger.info(f"Number of torrents: {len(torrents)}")

        if torrents:
            logger.info(f"First torrent: {torrents[0].get('name', 'Unknown')}")

        # Test getting preferences
        prefs = await client.get_preferences()
        logger.info(f"Default save path: {prefs.get('save_path', 'Unknown')}")

        logger.info("✅ Client test completed successfully!")


def main():
    """Run the test."""
    try:
        asyncio.run(test_client())
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
