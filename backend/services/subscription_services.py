import json
import os

from logger import logger
from services import spotdl_download_services
from services.config_services import Config

example_subscriptions = [
    {"name": "Tech News Playlist", "lastSync": "2025-03-12 08:30", "items": 25, "type": "YouTube Playlist"},
    {"name": "Jazz Music Collection", "lastSync": "2025-03-10 15:00", "items": 40, "type": "Spotify Playlist"},
    {"name": "Top Hits Playlist", "lastSync": "2025-03-11 12:00", "items": 58, "type": "YouTube Playlist"},
    {"name": "Fitness & Health Playlist", "lastSync": "2025-03-09 09:45", "items": 22, "type": "Spotify Playlist"},
    {"name": "Science Video Collection", "lastSync": "2025-03-08 18:21", "items": 15, "type": "YouTube Playlist"},
]


class Subscriptions:
    def __init__(self, config: Config):
        self.config = config
        self.subscriptions = self.load_subscriptions()

    def load_subscriptions(self):
        """Load subscriptions from a JSON file."""
        if os.path.exists(self.config.SUBSCRIPTION_CONFIG_FILE_PATH):
            try:
                with open(self.config.SUBSCRIPTION_CONFIG_FILE_PATH, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading subscriptions from file: {str(e)}")
                return []
        else:
            return example_subscriptions

    def save_subscriptions(self):
        """Save subscriptions to a JSON file."""
        try:
            with open(self.config.SUBSCRIPTION_CONFIG_FILE_PATH, "w") as f:
                json.dump(self.subscriptions, f, indent=4)

        except Exception as e:
            logger.error(f"Error saving subscriptions to file: {str(e)}")

    def add_subscription(self, subscription):
        """Add a new subscription and save the list."""
        self.subscriptions.append(subscription)
        self.save_subscriptions()

    def get_all_subscriptions(self):
        """Return all subscriptions."""
        return self.subscriptions
