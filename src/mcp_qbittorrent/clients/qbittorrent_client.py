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

    # Torrent Management Methods

    async def get_torrent_list(
        self,
        filter: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of torrents.

        Args:
            filter: Filter torrents by status (all, downloading, completed, paused, etc.)
            category: Filter by category

        Returns:
            List of torrent dictionaries
        """
        params = {}
        if filter:
            params["filter"] = filter
        if category:
            params["category"] = category

        return await self._request("GET", "/api/v2/torrents/info", params=params)

    async def get_torrent_properties(self, hash: str) -> Dict[str, Any]:
        """Get properties of a specific torrent.

        Args:
            hash: Torrent hash

        Returns:
            Torrent properties dictionary
        """
        return await self._request(
            "GET",
            "/api/v2/torrents/properties",
            params={"hash": hash}
        )

    async def get_torrent_files(self, hash: str) -> List[Dict[str, Any]]:
        """Get list of files in a torrent.

        Args:
            hash: Torrent hash

        Returns:
            List of file dictionaries
        """
        return await self._request(
            "GET",
            "/api/v2/torrents/files",
            params={"hash": hash}
        )

    async def add_torrent(
        self,
        urls: Optional[str] = None,
        torrents: Optional[bytes] = None,
        savepath: Optional[str] = None,
        category: Optional[str] = None,
        paused: bool = False
    ) -> str:
        """Add torrent by URL or file.

        Args:
            urls: Torrent URL or magnet link
            torrents: Torrent file content
            savepath: Download save path
            category: Torrent category
            paused: Add torrent in paused state

        Returns:
            Response text
        """
        data = {}
        if urls:
            data["urls"] = urls
        if savepath:
            data["savepath"] = savepath
        if category:
            data["category"] = category
        if paused:
            data["paused"] = "true"

        return await self._request("POST", "/api/v2/torrents/add", data=data)

    async def pause_torrent(self, hashes: str) -> str:
        """Pause torrents.

        Args:
            hashes: Torrent hash(es), separated by |

        Returns:
            Response text
        """
        return await self._request(
            "POST",
            "/api/v2/torrents/pause",
            data={"hashes": hashes}
        )

    async def resume_torrent(self, hashes: str) -> str:
        """Resume torrents.

        Args:
            hashes: Torrent hash(es), separated by |

        Returns:
            Response text
        """
        return await self._request(
            "POST",
            "/api/v2/torrents/resume",
            data={"hashes": hashes}
        )

    async def delete_torrent(
        self,
        hashes: str,
        delete_files: bool = False
    ) -> str:
        """Delete torrents.

        Args:
            hashes: Torrent hash(es), separated by |
            delete_files: Also delete downloaded files

        Returns:
            Response text
        """
        return await self._request(
            "POST",
            "/api/v2/torrents/delete",
            data={
                "hashes": hashes,
                "deleteFiles": "true" if delete_files else "false"
            }
        )

    # Search Methods

    async def start_search(
        self,
        pattern: str,
        plugins: str = "all",
        category: str = "all"
    ) -> Dict[str, Any]:
        """Start a search job.

        Args:
            pattern: Search query
            plugins: Plugins to use (all, enabled, plugin_name)
            category: Category filter (all, movies, tv, music, etc.)

        Returns:
            Search job info with 'id' field
        """
        return await self._request(
            "POST",
            "/api/v2/search/start",
            data={
                "pattern": pattern,
                "plugins": plugins,
                "category": category
            }
        )

    async def get_search_status(self, id: int) -> Dict[str, Any]:
        """Get status of a search job.

        Args:
            id: Search job ID

        Returns:
            Search status dictionary
        """
        return await self._request(
            "GET",
            "/api/v2/search/status",
            params={"id": id}
        )

    async def get_search_results(
        self,
        id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get results of a search job.

        Args:
            id: Search job ID
            limit: Maximum number of results
            offset: Result offset

        Returns:
            Search results dictionary
        """
        params = {"id": id}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        return await self._request("GET", "/api/v2/search/results", params=params)

    async def stop_search(self, id: int) -> str:
        """Stop a search job.

        Args:
            id: Search job ID

        Returns:
            Response text
        """
        return await self._request(
            "POST",
            "/api/v2/search/stop",
            data={"id": id}
        )

    async def delete_search(self, id: int) -> str:
        """Delete a search job.

        Args:
            id: Search job ID

        Returns:
            Response text
        """
        return await self._request(
            "POST",
            "/api/v2/search/delete",
            data={"id": id}
        )

    # Application Methods

    async def get_preferences(self) -> Dict[str, Any]:
        """Get application preferences.

        Returns:
            Preferences dictionary
        """
        return await self._request("GET", "/api/v2/app/preferences")

    async def get_version(self) -> str:
        """Get qBittorrent version.

        Returns:
            Version string
        """
        return await self._request("GET", "/api/v2/app/version")
