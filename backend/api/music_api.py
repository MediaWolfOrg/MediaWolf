from db.music_db_handler import MusicDBHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from logger import logger
from services.lidarr_services import LidarrService
from services.spotdl_download_services import SpotDLDownloadService
from services.spotify_services import SpotifyService

music_bp = Blueprint("music", __name__)


class MusicAPI:
    def __init__(
        self,
        db: MusicDBHandler,
        socketio: SocketIO,
        lidarr_service: LidarrService,
        spotify_service: SpotifyService,
        spotdl_download_service: SpotDLDownloadService,
    ):
        self.db = db
        self.socketio = socketio
        self.lidarr_service = lidarr_service
        self.spotify_service = spotify_service
        self.spotdl_download_service = spotdl_download_service

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @music_bp.route("/music")
        def serve_music_page():
            artists_for_selection = self.db.get_existing_db_artists()
            sorted_artists = [artist.title() for artist in sorted(artists_for_selection)]
            return render_template("music.html", artists=sorted_artists)

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("refresh_music_recommendations")
        def handle_refresh_music_recommendations(data):
            recommended_artists = self.db.refresh_recommendations(data)
            self.socketio.emit("music_recommendations", {"data": recommended_artists})

        @self.socketio.on("add_artist_to_lidarr")
        def handle_add_artist_to_lidarr(artist_name):
            return_result = self.lidarr_service.add_artist_to_lidarr(artist_name)
            if return_result.get("result") == "success":
                self.socketio.emit("refresh_artist", return_result.get("item"))
            else:
                self.socketio.emit(
                    "new_toast_msg",
                    {"title": "Failed to add Artist", "message": return_result.get("message")},
                )

        @self.socketio.on("dismiss_artist")
        def handle_dismiss_artist(artist_name):
            self.db.dismiss_artist(artist_name)

        @self.socketio.on("load_music_recommendations")
        def handle_load_recommendations():
            self.socketio.emit("music_recommendations", {"data": self.db.recommended_artists})

        @self.socketio.on("search_spotify")
        def handle_spotify_search(query_req):
            if not query_req:
                self.socketio.emit(
                    "toast", {"title": "Blank Search Query", "body": "Please enter search request"}
                )
                parsed_results = {}
            else:
                parsed_results = self.spotify_service.perform_spotify_search(query_req)
            self.socketio.emit("spotify_search_results", {"results": parsed_results})

        @self.socketio.on("spotify_download_item")
        def handle_spotify_download(requested_item):
            self.spotdl_download_service.add_item_to_queue(requested_item)

        @self.socketio.on("spotdl_cancel_all")
        def handle_spotdl_cancel_all():
            logger.info("Request to cancel all download recieved")
            self.spotdl_download_service.cancel_active_download()
            self.spotdl_download_service.cancel_pending_downloads()

        @self.socketio.on("spotdl_cancel_active")
        def handle_spotdl_cancel_active():
            logger.info("Request to cancel active download recieved")
            self.spotdl_download_service.cancel_active_download()

        @self.socketio.on("get_wanted_albums_from_lidarr")
        def handle_get_wanted_albums_from_lidarre():
            logger.info("Request to cancel active download recieved")
            self.lidarr_service.get_wanted_albums_from_lidarr()

    def get_blueprint(self):
        return music_bp
