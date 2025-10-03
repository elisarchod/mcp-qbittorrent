"""qBittorrent Web API client."""

import logging
from typing import Any, Dict, List, Optional
import aiohttp


logger = logging.getLogger(__name__)


class QBittorrentClientError(Exception):
    """Base exception for qBittorrent client errors."""
    pass


class AuthenticationError(QBittorrentClientError):
    """Raised when authentication fails."""
    pass


class APIError(QBittorrentClientError):
    """Raised when API request fails."""
    pass


class QBittorrentClient:
    """Async client for qBittorrent Web API."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30
    ):
        """Initialize qBittorrent client.

        Args:
            base_url: qBittorrent Web API URL
            username: Web UI username
            password: Web UI password
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        self._authenticated = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def login(self) -> None:
        """Authenticate with qBittorrent Web API.

        Raises:
            AuthenticationError: If authentication fails
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

        try:
            async with self.session.post(
                f"{self.base_url}/api/v2/auth/login",
                data={"username": self.username, "password": self.password}
            ) as resp:
                text = await resp.text()
                if resp.status != 200 or text != "Ok.":
                    raise AuthenticationError(
                        f"Authentication failed: {resp.status} - {text}"
                    )
                self._authenticated = True
                logger.info("Successfully authenticated with qBittorrent")
        except aiohttp.ClientError as e:
            raise AuthenticationError(f"Connection error during authentication: {e}")

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            self._authenticated = False

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Form data for POST requests
            params: URL query parameters

        Returns:
            Response data (parsed JSON or text)

        Raises:
            APIError: If request fails
            AuthenticationError: If not authenticated
        """
        if not self._authenticated:
            raise AuthenticationError("Not authenticated. Call login() first.")

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(
                method,
                url,
                data=data,
                params=params
            ) as resp:
                if resp.status == 403:
                    raise AuthenticationError("Authentication token expired or invalid")
                if resp.status >= 400:
                    text = await resp.text()
                    raise APIError(f"API request failed: {resp.status} - {text}")

                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await resp.json()
                else:
                    return await resp.text()

        except aiohttp.ClientError as e:
            raise APIError(f"Request error: {e}")

    # Core Methods (6 methods for MCP tools)

    async def list_torrents(
        self,
        filter: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List torrents with optional filtering."""
        params = {}
        if filter:
            params["filter"] = filter
        if category:
            params["category"] = category
        return await self._request("GET", "/api/v2/torrents/info", params=params)

    async def get_torrent_info(self, hash: str) -> Dict[str, Any]:
        """Get detailed info for a specific torrent (properties + files)."""
        properties = await self._request(
            "GET",
            "/api/v2/torrents/properties",
            params={"hash": hash}
        )
        files = await self._request(
            "GET",
            "/api/v2/torrents/files",
            params={"hash": hash}
        )
        return {**properties, "files": files}

    async def add_torrent(
        self,
        urls: str,
        savepath: Optional[str] = None,
        category: Optional[str] = None,
        paused: bool = False
    ) -> str:
        """Add torrent by URL or magnet link."""
        data = {"urls": urls}
        if savepath:
            data["savepath"] = savepath
        if category:
            data["category"] = category
        if paused:
            data["paused"] = "true"
        return await self._request("POST", "/api/v2/torrents/add", data=data)

    async def control_torrent(
        self,
        hashes: str,
        action: str,
        delete_files: bool = False
    ) -> str:
        """Control torrent: pause, resume, or delete."""
        actions = {
            "pause": "/api/v2/torrents/pause",
            "resume": "/api/v2/torrents/resume",
            "delete": "/api/v2/torrents/delete"
        }
        if action not in actions:
            raise APIError(f"Invalid action: {action}. Must be pause, resume, or delete")

        endpoint = actions[action]
        data = {"hashes": hashes}
        if action == "delete":
            data["deleteFiles"] = "true" if delete_files else "false"

        return await self._request("POST", endpoint, data=data)

    async def search_torrents(
        self,
        query: str,
        plugins: str = "all",
        category: str = "all",
        limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """Search for torrents and return results."""
        import asyncio

        # Start search
        search_job = await self._request(
            "POST",
            "/api/v2/search/start",
            data={"pattern": query, "plugins": plugins, "category": category}
        )
        search_id = search_job.get("id")

        # Wait for results (poll up to 30 seconds)
        for _ in range(30):
            await asyncio.sleep(1)
            status = await self._request(
                "GET",
                "/api/v2/search/status",
                params={"id": search_id}
            )
            if status[0]["status"] == "Stopped":
                break

        # Get results
        results = await self._request(
            "GET",
            "/api/v2/search/results",
            params={"id": search_id, "limit": limit}
        )

        # Cleanup
        await self._request("POST", "/api/v2/search/delete", data={"id": search_id})

        return results

    async def get_preferences(self) -> Dict[str, Any]:
        """Get qBittorrent application preferences."""
        return await self._request("GET", "/api/v2/app/preferences")
