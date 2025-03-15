from flask import Blueprint, render_template
from flask_socketio import SocketIO
from logger import logger

downloads_bp = Blueprint("downloads", __name__)


class DownloadsAPI:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @downloads_bp.route("/downloads")
        def serve_downloads_page():
            history = {}
            return render_template("downloads.html", history=history)

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("download_link")
        def handle_download_link():
            """Adds link to download queue."""
            try:
                pass
            except Exception as e:
                logger.error(f"Error with downloads: {str(e)}")

    def get_blueprint(self):
        return downloads_bp
