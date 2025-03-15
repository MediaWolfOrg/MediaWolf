import queue
import subprocess
import threading

from logger import logger
from services.config_services import Config


class SpotDLDownloadService:
    def __init__(self, config: Config, download_history: dict):
        self.config = config
        self.download_history = download_history
        self.download_queue = queue.Queue()
        self.spodtdl_subprocess = None
        download_thread = threading.Thread(target=self.process_downloads, daemon=True)
        download_thread.start()

    def add_item_to_queue(self, data):
        logger.info(f"Download Requested: {data}")

        spotify_url = data.get("url")
        item_type = data.get("type")
        item_name = data.get("name")
        item_artist = data.get("artist")

        download_info = {
            "name": item_name,
            "type": item_type,
            "artist": item_artist,
            "url": spotify_url,
            "status": "Pending...",
        }

        self.download_queue.put((spotify_url, download_info))
        self.download_history[spotify_url] = download_info

    def process_downloads(self):
        while True:
            url, download_info = self.download_queue.get()

            if download_info["status"] == "Cancelled":
                self.download_queue.task_done()
                continue

            if download_info["type"] == "track":
                download_path = self.config.track_output
            elif download_info["type"] == "playlist":
                download_path = self.config.playlist_output
            elif download_info["type"] == "album":
                download_path = self.config.album_output
            elif download_info["type"] == "artist":
                download_path = self.config.artist_output

            download_info["status"] = "Downloading..."
            self.download_history[url] = download_info

            try:
                logger.info(f"Downloading: {url}")

                command = ["spotdl", "--output", f"{download_path}", url]
                logger.info(f"SpotDL command: {command}")

                self.spodtdl_subprocess = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                stdout, stderr = self.spodtdl_subprocess.communicate()

                if download_info["status"] == "Cancelled":
                    self.download_queue.task_done()
                    continue

                if self.spodtdl_subprocess.returncode == 0:
                    download_info["status"] = "Complete"
                    logger.info("Finished Item")
                else:
                    download_info["status"] = "Failed"
                    logger.error(f"Error downloading: {stderr}")

                self.download_history[url] = download_info

            except Exception as e:
                logger.error(f"Process Downloads Error: {str(e)}")
                download_info["status"] = "Error"
                self.download_history[url] = download_info

            self.download_queue.task_done()

            if self.download_queue.empty():
                logger.info("Queue is empty")

    def cancel_active_download(self):
        try:
            if not self.spodtdl_subprocess:
                logger.info("No active download.")
                return

            logger.info("Cancelling active download.")
            self.spodtdl_subprocess.terminate()

            for url, info in self.download_history.items():
                if info["status"] == "Downloading...":
                    info["status"] = "Cancelled"
                    self.download_history[url] = info
                    break

            self.spodtdl_subprocess = None
            logger.info("Active download cancelled")

        except Exception as e:
            logger.error(f"Cancel Active Error: {str(e)}")

    def cancel_pending_downloads(self):
        try:
            logger.info("Request to cancel pending download recieved")

            temp_queue = []
            while not self.download_queue.empty():
                url, download_info = self.download_queue.get()
                download_info["status"] = "Cancelled"
                self.download_history[url] = download_info
                temp_queue.append((url, download_info))

            for item in temp_queue:
                self.download_queue.put(item)

            logger.info("Pending download cancelled")

        except Exception as e:
            logger.error(f"Cancel Pending Error: {str(e)}")
