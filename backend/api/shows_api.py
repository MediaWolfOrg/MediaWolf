from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.sonarr_services import SonarrService

shows_bp = Blueprint("shows", __name__)


class ShowsAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, sonarr_service: SonarrService):
        self.db = db
        self.socketio = socketio
        self.sonarr_service = sonarr_service
        self.recommended_shows = []

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @shows_bp.route("/shows")
        def serve_shows_page():
            return render_template("shows.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("refresh_recommendations")
        def handle_refresh_show_recommendations(data):
            pass

    def get_blueprint(self):
        return shows_bp
