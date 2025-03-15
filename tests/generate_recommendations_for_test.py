from backend.db.music_db_handler import MusicDBHandler
from backend.services.config_services import Config
from backend.services.lidarr_services import LidarrService

db = MusicDBHandler()
lidarr = LidarrService(Config(), db)

lidarr.generate_and_store_lastfm_recommendations()
