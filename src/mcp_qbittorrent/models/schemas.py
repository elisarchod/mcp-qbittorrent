"""Pydantic models for qBittorrent API responses."""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TorrentInfo(BaseModel):
    """Torrent information for list view."""
    model_config = ConfigDict(populate_by_name=True)

    hash: str
    name: str
    size: int
    progress: float
    dlspeed: int
    upspeed: int
    eta: int
    state: str
    category: str = ""
    save_path: str
    num_seeds: int
    num_leechs: int
    ratio: float


class TorrentProperties(BaseModel):
    """Detailed torrent properties."""
    model_config = ConfigDict(populate_by_name=True)

    save_path: str
    creation_date: int
    total_uploaded: int
    total_downloaded: int
    time_elapsed: int
    seeding_time: int
    share_ratio: float
    comment: str = ""


class TorrentFile(BaseModel):
    """Individual file within a torrent."""

    name: str
    size: int
    progress: float
    priority: int


class SearchResult(BaseModel):
    """Individual torrent search result."""

    fileName: str
    fileUrl: str
    fileSize: int
    nbSeeders: int
    nbLeechers: int
    siteUrl: str
    descrLink: Optional[str] = None


class SearchResults(BaseModel):
    """Container for search results."""

    results: List[SearchResult]
    status: str
    total: int


class Preferences(BaseModel):
    """qBittorrent application preferences."""

    save_path: str
    temp_path: str = ""
    dl_limit: int
    up_limit: int
    max_connec: int
    max_connec_per_torrent: int
    listen_port: int
    upnp: bool
    dht: bool
    max_active_downloads: int
    max_active_torrents: int
    max_active_uploads: int
