from db.database_handler import DatabaseHandler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.readarr_services import ReadarrService

books_bp = Blueprint("books", __name__)


class BooksAPI:
    def __init__(self, db: DatabaseHandler, socketio: SocketIO, readarr_service: ReadarrService):
        self.db = db
        self.socketio = socketio
        self.readarr_service = readarr_service
        self.recommended_books = []

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @books_bp.route("/books")
        def serve_books_page():
            return render_template("books.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("refresh_book_recommendations")
        def handle_refresh_book_recommendations(data):
            pass

    def get_blueprint(self):
        return books_bp
