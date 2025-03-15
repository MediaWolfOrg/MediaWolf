from flask import Blueprint, render_template
from flask_socketio import SocketIO
from logger import logger
from services.subscription_services import Subscriptions

subscriptions_bp = Blueprint("subscriptions", __name__)


class SubscriptionsAPI:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.subscriptions = Subscriptions()
        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @subscriptions_bp.route("/subscriptions")
        def serve_subscriptions_page():
            history = {}
            return render_template("subscriptions.html", history=history)

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("add_sub")
        def handle_download_link():
            """Add Subscriptions."""
            try:
                pass
            except Exception as e:
                logger.error(f"Error with subscriptions: {str(e)}")

        @self.socketio.on("request_subs")
        def handle_request_subs():
            """Emit the subscriptions list to the client."""
            try:
                subs = self.subscriptions.get_all_subscriptions()
                self.socketio.emit("subs_list", {"subscriptions": subs})

            except Exception as e:
                logger.error(f"Error emitting subscriptions: {str(e)}")

    def get_blueprint(self):
        return subscriptions_bp
