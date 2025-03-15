import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, Optional

from logger import logger
from services.lidarr_services import LidarrService
from services.radarr_services import RadarrService
from services.readarr_services import ReadarrService
from services.sonarr_services import SonarrService

TASKS_CONFIG_FILE_NAME = "config/mediawolf_tasks.json"


@dataclass
class Task:
    id: int
    name: str
    cron: str
    description: str
    status: str = "Active"

    def to_dict(self):
        return asdict(self)


class Tasks:
    def __init__(
        self,
        lidarr_service: LidarrService,
        radarr_service: RadarrService,
        readarr_service: ReadarrService,
        sonarr_service: SonarrService,
    ):
        self.lidarr_service = lidarr_service
        self.radarr_service = radarr_service
        self.readarr_service = readarr_service
        self.sonarr_service = sonarr_service
        self.config_file = TASKS_CONFIG_FILE_NAME
        self.tasks: Dict[str, Task] = {}

        self.load_tasks()

    def load_tasks(self):
        """Load tasks from the configuration file or create default tasks."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    tasks_data = json.load(f)
                    self.tasks = {task_id: Task(**data) for task_id, data in tasks_data.items()}
                    logger.info("Tasks successfully loaded from file.")

            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading tasks: {e}")
                self.create_default_tasks()
        else:
            self.create_default_tasks()

    def create_default_tasks(self):
        """Create default tasks and save them."""
        default_tasks = [
            Task(1, "Lidarr Sync", "0 0 * * *", "Refreshes Lidarr artist list."),
            Task(2, "Readarr Sync", "0 3 * * *", "Updates Readarr book collection.", "Inactive"),
            Task(3, "Sonarr Sync", "0 6 * * *", "Syncs Sonarr series list."),
            Task(4, "Radarr Sync", "0 12 * * *", "Updates Radarr movie database."),
            Task(5, "Spotify Sync", "0 15 * * *", "Syncs Spotify playlists."),
            Task(6, "YouTube Sync", "0 18 * * *", "Syncs YouTube playlists and channels."),
        ]

        self.tasks = {f"task_{i+1}": task for i, task in enumerate(default_tasks)}
        self.save_tasks()
        logger.info("Default tasks created and saved.")

    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(
                    {task_id: task.to_dict() for task_id, task in self.tasks.items()}, f, indent=4
                )
            logger.info("Tasks successfully saved.")
        except IOError as e:
            logger.error(f"Failed to save tasks: {e}")

    def update_task(self, task_id: str, **updates):
        """Update task attributes dynamically."""
        task = self.tasks.get(task_id)
        if task:
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
            logger.info(f"Task '{task_id}' updated: {updates}")
        else:
            logger.warning(f"Task '{task_id}' not found.")

    def delete_task(self, task_id: str):
        """Delete a task by ID."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            logger.info(f"Task '{task_id}' deleted.")
        else:
            logger.warning(f"Task '{task_id}' not found.")

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self.tasks.get(task_id)

    def list_tasks(self) -> Dict[str, Task]:
        """Return all tasks."""
        return [task.to_dict() for task in self.tasks.values()]
