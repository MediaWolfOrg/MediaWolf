from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.radarr_services import RadarrService

movies_bp = Blueprint("movies", __name__)


class MoviesAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, radarr_service: RadarrService):
        self.db = db
        self.socketio = socketio
        self.radarr_service = radarr_service
        self.recommended_movies = []

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @movies_bp.route("/movies")
        def serve_movies_page():
            return render_template("movies.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("refresh_movie_recommendations")
        def handle_refresh_movie_recommendations(data):
            pass

    def get_blueprint(self):
        return movies_bp
