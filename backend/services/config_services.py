import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

import logger

LOG_FILE_NAME = "config/mediawolf_log.log"
CONFIG_FILE_NAME = "config/mediawolf_settings.json"
DB_URL = "sqlite:///config/mediawolf_database.db"


@dataclass
class Config:
    """Configuration class for environment-based settings using dataclasses."""

    # General Settings
    log_level: str = "INFO"

    # Last FM Settings
    lastfm_api_key: str = ""
    lastfm_api_secret: str = ""
    lastfm_sleep_interval: int = 300

    # Lidarr settings
    lidarr_address: str = "http://localhost:8686"
    lidarr_api_key: str = ""
    lidarr_api_timeout: int = 10
    lidarr_root_folder_path: str = "/data/media/music"
    lidarr_metadata_profile_id: int = 1
    lidarr_quality_profile_id: int = 1
    lidarr_search_for_missing_albums: bool = False
    lidarr_fallback_to_top_result: bool = True

    # Readarr settings
    readarr_address: str = "http://localhost:8787"
    readarr_api_key: str = ""
    readarr_api_timeout: int = 10
    readarr_root_folder_path: str = "/data/media/books"
    readarr_metadata_profile_id: int = 1
    readarr_quality_profile_id: int = 1
    readarr_search_for_missing_albums: bool = False
    readarr_fallback_to_top_result: bool = True

    # Radarr settings
    radarr_address: str = "http://localhost:7878"
    radarr_api_key: str = ""
    radarr_api_timeout: int = 10
    radarr_root_folder_path: str = "/data/media/movies"
    radarr_metadata_profile_id: int = 1
    radarr_quality_profile_id: int = 1
    radarr_search_for_missing_movies: bool = False
    radarr_fallback_to_top_result: bool = True

    # Sonarr settings
    sonarr_address: str = "http://localhost:8989"
    sonarr_api_key: str = ""
    sonarr_api_timeout: int = 10
    sonarr_root_folder_path: str = "/data/media/shows"
    sonarr_metadata_profile_id: int = 1
    sonarr_quality_profile_id: int = 1
    sonarr_search_for_missing_shows: bool = False
    sonarr_fallback_to_top_result: bool = True

    # API keys
    tmdb_api_key: str = ""
    tvdb_api_key: str = ""

    # Spotify settings
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_search_limit: int = 10
    spotify_sleep_interval: int = 10

    # Output formatting
    track_output: str = "{artist}/{album} - ({year})/{artist} - {title}.{output-ext}"
    album_output: str = (
        "{artist}/{album} - ({year})/{artist} - {album} - {track-number} - {title}.{output-ext}"
    )
    playlist_output: str = "{list-name}/{artist} - {title}.{output-ext}"
    artist_output: str = "{artist}/{album} - ({year})/{artist} - {title}.{output-ext}"

    # SpotDL/YTDLP settings
    spotdl_ffmpeg_args: str = "-q:a 0"
    ytdlp_video_format_id: str = "bestvideo"
    ytdlp_audio_format_id: str = "bestaudio"
    ytdlp_defer_hours: int = 0
    ytdlp_include_id_in_filename: bool = False
    ytdlp_subtitles_settings: Dict[str, Any] = field(default_factory=dict)
    ytdlp_subtitle_languages: List[str] = field(default_factory=lambda: ["en"])

    # Internals
    config_file: str = CONFIG_FILE_NAME
    config_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Load configuration from JSON file or environment variables."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as file:
                    self.config_data = json.load(file)

        except Exception as e:
            logger.error(f"Error loading config from file: {str(e)}")
            self.config_data = {}

        self.load_config()

    def load_config(self):
        """Load configuration from environment variables or JSON file."""
        for key, default_value in asdict(self).items():
            env_value = os.getenv(key.upper())
            if env_value is not None:
                value = self.parse_value(env_value)
            else:
                value = self.config_data.get(key, default_value)

            setattr(self, key, value)

        self.save_config()

    def parse_value(self, value: str) -> Any:
        """Parse environment variable values to correct types."""
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.replace(".", "", 1).isdigit():
                return float(value) if "." in value else int(value)
        return value

    def save_config(self, settings_to_save={}):
        """Save the current configuration to the JSON file."""
        try:
            for key, value in settings_to_save.items():
                setattr(self, key, self.parse_value(value))

            with open(self.config_file, "w") as file:
                json.dump(asdict(self), file, indent=4)

        except Exception as e:
            logger.error(f"Error saving config file: {str(e)}")

    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary."""
        return asdict(self)
