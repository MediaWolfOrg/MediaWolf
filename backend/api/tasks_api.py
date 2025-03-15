from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.lidarr_services import LidarrService
from services.radarr_services import RadarrService
from services.readarr_services import ReadarrService
from services.sonarr_services import SonarrService
from services.tasks import Tasks

tasks_bp = Blueprint("tasks", __name__)


class TasksAPI:
    def __init__(
        self,
        socketio: SocketIO,
        lidarr_service: LidarrService,
        radarr_services: RadarrService,
        readarr_services: ReadarrService,
        sonarr_services: SonarrService,
    ):
        self.socketio = socketio
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.tasks_manager = Tasks(
            lidarr_service, radarr_services, readarr_services, sonarr_services
        )
        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @tasks_bp.route("/tasks")
        def serve_page():
            return render_template("tasks.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        # NOT IMPLEMENTED -> REWORK NEEDED

        @self.socketio.on("task_manual_start")
        def handle_manual_start(task_id):
            task = self.tasks.get(task_id)
            if task:
                task["status"] = "Running"
                self.socketio.emit("update_task", task)

        @self.socketio.on("task_pause")
        def handle_pause(task_id):
            task = self.tasks.get(task_id)
            if task and task["job"]:
                task["job"].pause()
                task["status"] = "Paused"
                self.socketio.emit("update_task", task)

        @self.socketio.on("task_stop")
        def handle_stop(task_id):
            task = self.tasks.get(task_id)
            if task and task["job"]:
                task["job"].remove()
                task["status"] = "Stopped"
                self.socketio.emit("update_task", task)

        @self.socketio.on("task_cancel")
        def handle_cancel(task_id):
            task = self.tasks.get(task_id)
            if task and task["job"]:
                task["job"].remove()
                task["status"] = "Cancelled"
                self.socketio.emit("update_task", task)

        @self.socketio.on("task_disable")
        def handle_disable(task_id):
            task = self.tasks.get(task_id)
            if task and task["job"]:
                task["job"].pause()
                task["status"] = "Disabled"
                self.socketio.emit("update_task", task)

        @self.socketio.on("request_tasks")
        def handle_request_tasks():
            task_list = self.tasks_manager.list_tasks()
            self.socketio.emit("load_task_data", task_list)

    def get_blueprint(self):
        return tasks_bp
