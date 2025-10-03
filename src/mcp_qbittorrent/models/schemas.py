"""Pydantic models for qBittorrent API responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class TorrentInfo(BaseModel):
    """Torrent information model."""

    hash: str = Field(..., description="Torrent hash")
    name: str = Field(..., description="Torrent name")
    size: int = Field(..., description="Total size in bytes")
    progress: float = Field(..., description="Download progress (0-1)")
    dlspeed: int = Field(..., description="Download speed in bytes/s")
    upspeed: int = Field(..., description="Upload speed in bytes/s")
    downloaded: int = Field(..., description="Downloaded bytes")
    uploaded: int = Field(..., description="Uploaded bytes")
    eta: int = Field(..., description="ETA in seconds")
    state: str = Field(..., description="Torrent state")
    category: str = Field(default="", description="Torrent category")
    save_path: str = Field(..., description="Save path")
    num_seeds: int = Field(..., description="Number of seeds")
    num_leechs: int = Field(..., description="Number of leechers")
    ratio: float = Field(..., description="Upload/download ratio")
    added_on: int = Field(..., description="Unix timestamp of when added")
    completion_on: int = Field(..., description="Unix timestamp of completion")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True


class TorrentProperties(BaseModel):
    """Detailed torrent properties model."""

    save_path: str = Field(..., description="Save path")
    creation_date: int = Field(..., description="Creation date timestamp")
    piece_size: int = Field(..., description="Piece size in bytes")
    comment: str = Field(default="", description="Torrent comment")
    total_wasted: int = Field(..., description="Total wasted bytes")
    total_uploaded: int = Field(..., description="Total uploaded bytes")
    total_downloaded: int = Field(..., description="Total downloaded bytes")
    up_limit: int = Field(..., description="Upload limit in bytes/s")
    dl_limit: int = Field(..., description="Download limit in bytes/s")
    time_elapsed: int = Field(..., description="Time elapsed in seconds")
    seeding_time: int = Field(..., description="Seeding time in seconds")
    nb_connections: int = Field(..., description="Number of connections")
    share_ratio: float = Field(..., description="Share ratio")


class TorrentFile(BaseModel):
    """Torrent file model."""

    name: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    progress: float = Field(..., description="File download progress (0-1)")
    priority: int = Field(..., description="File priority")
    is_seed: bool = Field(..., description="Whether file is seeded")
    availability: float = Field(..., description="File availability")


class SearchResult(BaseModel):
    """Search result model."""

    fileName: str = Field(..., description="Torrent name")
    fileUrl: str = Field(..., description="Torrent download URL")
    fileSize: int = Field(..., description="File size in bytes")
    nbSeeders: int = Field(..., description="Number of seeders")
    nbLeechers: int = Field(..., description="Number of leechers")
    siteUrl: str = Field(..., description="Site URL")
    descrLink: Optional[str] = Field(default=None, description="Description link")


class SearchStatus(BaseModel):
    """Search job status model."""

    id: int = Field(..., description="Search job ID")
    status: str = Field(..., description="Search status (Running/Stopped)")
    total: int = Field(..., description="Total results found")


class SearchResults(BaseModel):
    """Search results container."""

    results: List[SearchResult] = Field(..., description="Search results")
    status: str = Field(..., description="Search status")
    total: int = Field(..., description="Total results")


class Preferences(BaseModel):
    """qBittorrent preferences model."""

    locale: str = Field(..., description="Locale")
    save_path: str = Field(..., description="Default save path")
    temp_path_enabled: bool = Field(..., description="Temp path enabled")
    temp_path: str = Field(default="", description="Temp path")
    preallocate_all: bool = Field(..., description="Preallocate disk space")
    incomplete_files_ext: bool = Field(..., description="Append .!qB extension")
    dl_limit: int = Field(..., description="Global download limit bytes/s")
    up_limit: int = Field(..., description="Global upload limit bytes/s")
    max_connec: int = Field(..., description="Max global connections")
    max_connec_per_torrent: int = Field(..., description="Max connections per torrent")
    max_uploads: int = Field(..., description="Max upload slots")
    max_uploads_per_torrent: int = Field(..., description="Max upload slots per torrent")
    listen_port: int = Field(..., description="Listen port")
    upnp: bool = Field(..., description="UPnP enabled")
    dht: bool = Field(..., description="DHT enabled")
    pex: bool = Field(..., description="PeX enabled")
    lsd: bool = Field(..., description="LSD enabled")
    encryption: int = Field(..., description="Encryption mode")
    anonymous_mode: bool = Field(..., description="Anonymous mode")
    queueing_enabled: bool = Field(..., description="Queueing enabled")
    max_active_downloads: int = Field(..., description="Max active downloads")
    max_active_torrents: int = Field(..., description="Max active torrents")
    max_active_uploads: int = Field(..., description="Max active uploads")


class AddTorrentResponse(BaseModel):
    """Response from adding a torrent."""

    success: bool = Field(..., description="Whether torrent was added successfully")
    message: Optional[str] = Field(default=None, description="Response message")


class ControlTorrentResponse(BaseModel):
    """Response from controlling a torrent."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: Optional[str] = Field(default=None, description="Response message")
