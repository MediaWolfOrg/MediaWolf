from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.config_services import Config

settings_bp = Blueprint("settings", __name__)


class SettingsAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, config: Config):
        self.db = db
        self.socketio = socketio
        self.config = config

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @settings_bp.route("/settings")
        def serve_settings_page():
            return render_template("settings.html", settings_data=self.config.as_dict())

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("get_settings")
        def get_settings():
            """Endpoint to get settings."""
            self.socketio.emit("settings_data", self.config.as_dict())

        @self.socketio.on("save_settings")
        def save_settings(data):
            """Endpoint to save settings."""
            self.config.save_config(data)

    def get_blueprint(self):
        return settings_bp
