from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.user_service import UserService

users_bp = Blueprint("users", __name__)


class UsersAPI:
    def __init__(self, user_service: UserService, socketio: SocketIO):
        self.socketio = socketio
        self.users = user_service

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask Routes."""

        @users_bp.route("/users")
        def serve_user_page():
            return render_template("users.html")

    def setup_socket_events(self):
        @self.socketio.on("get_users")
        def get_users():
            """Send all users to the client (in case they manually refresh the list)."""
            users = self.users.get_all_users()
            self.socketio.emit("users_list", {"users": users})

        @self.socketio.on("save_user")
        def save_user(data):
            """Update user role or password and notify all clients."""
            user_id = data.get("id")

            user = self.users.get_user_by_id(user_id)
            if not user:
                self.socketio.emit("user_update_failed", {"error": "User not found"})
                return

            self.users.update_user(data)
            self.socketio.emit("user_updated")

        @self.socketio.on("create_user")
        def create_user(data):
            self.users.create_user(data)
            self.socketio.emit("user_created")

        @self.socketio.on("delete_user")
        def delete_user(user):
            user_id = user.get("id")
            self.users.delete_user(user_id)
            self.socketio.emit("user_deleted")

    def get_blueprint(self):
        return users_bp
