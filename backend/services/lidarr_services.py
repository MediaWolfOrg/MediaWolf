import concurrent.futures
import json
import os
import urllib.parse
from datetime import datetime

import musicbrainzngs
import requests
from db.music_db_handler import MusicDBHandler
from logger import logger
from services.config_services import Config
from services.lastfm_services import LastFMService
from thefuzz import fuzz
from unidecode import unidecode


class LidarrService:
    def __init__(self, config: Config, db: MusicDBHandler):
        self.config = config
        self.db = db
        self.thread_limit = 4
        self.lastfm_service = LastFMService(
            self.config.lastfm_api_key,
            self.config.lastfm_api_secret,
            self.config.lastfm_sleep_interval,
        )
        self.app_name = "MediaWolf"
        self.app_rev = "0.0.0"
        self.app_url = "mediawolf.github.io"

    def generate_and_store_lastfm_recommendations(self):
        try:
            lidarr_artists = self.db.get_existing_db_artists()

            for artist_name in lidarr_artists:
                logger.info(f"Processing artist: {artist_name}")

                has_existing_recommendations = self.db._get_recommended_artists_for_lidarr_artist(
                    artist_name
                )

                if not has_existing_recommendations:
                    recommendations = self.lastfm_service.generate_recommendations(artist_name)

                    if recommendations:
                        self.db.store_recommended_artists_for_lidarr_artist(
                            artist_name, recommendations
                        )
                    else:
                        logger.warning(f"No recommendations found for artist: {artist_name}")
                else:
                    logger.info(
                        f"Artist {artist_name} already has recommendations in the database."
                    )

        except Exception as e:
            logger.error(f"Error generating and storing LastFM recommendations: {str(e)}")

    def refresh_lidarr_artists(self):
        try:
            updated_lidarr_artists = self._get_artists()
            self.db.add_lidarr_artists(updated_lidarr_artists)

        except Exception as e:
            logger.error(f"Error Refreshing Lidarr Artists: {str(e)}")

    def _get_artists(self):
        try:
            logger.info("Getting Artists from Lidarr")
            endpoint = f"{self.config.lidarr_address}/api/v1/artist"
            headers = {"X-Api-Key": self.config.lidarr_api_key}
            response = requests.get(
                endpoint, headers=headers, timeout=self.config.lidarr_api_timeout
            )

            if response.status_code == 200:
                return response.json() or []
            else:
                logger.error(f"Lidarr Error Code: {response.status_code}")
                logger.error(f"Lidarr Error Message: {response.text}")
                return []

        except requests.RequestException as e:
            logger.error(f"Lidarr API Request Failed: {str(e)}")
            return []

    def add_artist_to_lidarr(self, raw_artist_name):
        try:
            return_status = {}
            artist_name = urllib.parse.unquote(raw_artist_name)
            artist_folder = artist_name.replace("/", " ")
            musicbrainzngs.set_useragent(self.app_name, self.app_rev, self.app_url)
            mbid = self.get_mbid_from_musicbrainz(artist_name)
            if mbid:
                lidarr_url = f"{self.config.lidarr_address}/api/v1/artist"
                headers = {"X-Api-Key": self.config.lidarr_api_key}
                payload = {
                    "ArtistName": artist_name,
                    "qualityProfileId": self.config.lidarr_quality_profile_id,
                    "metadataProfileId": self.config.lidarr_metadata_profile_id,
                    "path": os.path.join(self.config.lidarr_root_folder_path, artist_folder, ""),
                    "rootFolderPath": self.config.lidarr_root_folder_path,
                    "foreignArtistId": mbid,
                    "monitored": True,
                    "addOptions": {
                        "searchForMissingAlbums": self.config.lidarr_search_for_missing_albums
                    },
                }
                response = requests.post(lidarr_url, headers=headers, json=payload)
                if response.status_code == 201:
                    logger.info(f"Artist '{artist_name}' added successfully to Lidarr.")
                    status = "Added"
                else:
                    logger.error(f"Failed to add artist '{artist_name}' to Lidarr.")
                    error_data = json.loads(response.content)
                    error_message = (
                        error_data[0].get("errorMessage", "No Error Message Returned")
                        if error_data
                        else "Error Unknown"
                    )
                    logger.error(error_message)
                    if "already been added" in error_message:
                        status = "Already in Lidarr"
                        logger.info(f"Artist '{artist_name}' is already in Lidarr.")
                    elif "configured for an existing artist" in error_message:
                        status = "Already in Lidarr"
                        logger.info(
                            f"'{artist_folder}' folder already configured for an existing artist."
                        )
                    elif "Invalid Path" in error_message:
                        status = "Invalid Path"
                        logger.info(
                            f"Path: {os.path.join(self.root_folder_path, artist_folder, '')} not valid."
                        )
                    else:
                        status = "Failed to Add"

            else:
                status = "Failed to Add"
                logger.info(f"No Matching Artist for: '{artist_name}' in MusicBrainz.")
                return_status = {
                    "result": "fail",
                    "message": f"No Matching Artist for: '{artist_name}' in MusicBrainz.",
                }

            self.db.update_status_for_recommended_artist(artist_name, status)
            item = {"name": artist_name, "status": status}
            return_status = {"result": "success", "item": item}

        except Exception as e:
            logger.error(f"Adding Artist Error: {str(e)}")

        finally:
            return return_status

    def get_mbid_from_musicbrainz(self, artist_name):
        result = musicbrainzngs.search_artists(artist=artist_name)
        mbid = None

        if "artist-list" in result:
            artists = result["artist-list"]

            for artist in artists:
                match_ratio = fuzz.ratio(artist_name.lower(), artist["name"].lower())
                decoded_match_ratio = fuzz.ratio(
                    unidecode(artist_name.lower()), unidecode(artist["name"].lower())
                )
                if match_ratio > 90 or decoded_match_ratio > 90:
                    mbid = artist["id"]
                    logger.info(
                        f"Artist '{artist_name}' matched '{artist['name']}' with MBID: {mbid}  Match Ratio: {max(match_ratio, decoded_match_ratio)}"
                    )
                    break
            else:
                if self.config.lidarr_fallback_to_top_result and artists:
                    mbid = artists[0]["id"]
                    logger.info(
                        f"Artist '{artist_name}' matched '{artists[0]['name']}' with MBID: {mbid} "
                        f"Match Ratio: {max(match_ratio, decoded_match_ratio)}"
                    )

        return mbid

    def get_wanted_albums_from_lidarr(self):
        try:
            logger.warning("Accessing Lidarr API")
            self.lidarr_status = "busy"
            self.lidarr_items = []
            page = 1
            while True:
                endpoint = f"{self.config.lidarr_address}/api/v1/wanted/missing?includeArtist=true"
                params = {"apikey": self.config.lidarr_api_key, "page": page}
                response = requests.get(
                    endpoint, params=params, timeout=self.config.lidarr_api_timeout
                )
                if response.status_code == 200:
                    wanted_missing_albums = response.json()
                    if not wanted_missing_albums["records"]:
                        break
                    for album in wanted_missing_albums["records"]:
                        if self.lidarr_stop_event.is_set():
                            break
                        parsed_date = datetime.fromisoformat(
                            album["releaseDate"].replace("Z", "+00:00")
                        )
                        album_year = parsed_date.year
                        album_name = self.convert_to_lidarr_format(album["title"])
                        album_folder = f"{album_name} ({album_year})"
                        album_full_path = os.path.join(album["artist"]["path"], album_folder)
                        album_release_id = album["releases"][0]["id"]
                        new_item = {
                            "artist_id": album["artistId"],
                            "artist_path": album["artist"]["path"],
                            "artist": album["artist"]["artistName"],
                            "album_name": album_name,
                            "album_folder": album_folder,
                            "album_full_path": album_full_path,
                            "album_year": album_year,
                            "album_id": album["id"],
                            "album_release_id": album_release_id,
                            "album_genres": ", ".join(album["genres"]),
                            "track_count": 0,
                            "missing_count": 0,
                            "missing_tracks": [],
                            "checked": True,
                            "status": "",
                        }
                        self.lidarr_items.append(new_item)

                    page += 1
                else:
                    logger.error(f"Lidarr Wanted API Error Code: {response.status_code}")
                    logger.error(f"Lidarr Wanted API Error Text: {response.text}")
                    break

            self.lidarr_items.sort(key=lambda x: (x["artist"], x["album_name"]))

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_limit) as executor:
                self.lidarr_futures = [
                    executor.submit(self.get_missing_tracks_for_album, album)
                    for album in self.lidarr_items
                ]
                concurrent.futures.wait(self.lidarr_futures)

            self.lidarr_status = "complete"

        except Exception as e:
            logger.error(f"Error Getting Missing Albums: {str(e)}")
            self.lidarr_status = "error"

        finally:
            return {"status": self.lidarr_status, "data": self.lidarr_items}

    def get_missing_tracks_for_album(self, req_album):
        logger.warning(
            f'Reading Missing Track list of {req_album["artist"]} - {req_album["album_name"]} from Lidarr API'
        )
        endpoint = f"{self.config.lidarr_address}/api/v1/track"
        params = {"apikey": self.config.lidarr_api_key, "albumId": req_album["album_id"]}
        try:
            response = requests.get(endpoint, params=params, timeout=self.config.lidarr_api_timeout)
            if response.status_code == 200:
                tracks = response.json()
                track_count = len(tracks)
                for track in tracks:
                    if not track.get("hasFile", False):
                        new_item = {
                            "artist": req_album["artist"],
                            "track_title": track["title"],
                            "track_number": track["trackNumber"],
                            "absolute_track_number": track["absoluteTrackNumber"],
                            "track_id": track["id"],
                            "link": "",
                            "title_of_link": "",
                        }
                        req_album["missing_tracks"].append(new_item)

                req_album["track_count"] = track_count
                req_album["missing_count"] = len(req_album["missing_tracks"])

            else:
                logger.error(req_album["album_name"])
                logger.error(f"Lidarr Track API Error Code: {response.status_code}")
                logger.error(f"Lidarr Track API Error Text: {response.text}")

        except Exception as e:
            logger.error(req_album["album_name"])
            logger.error(f"Error Getting Missing Tracks: {str(e)}")

    def attempt_lidarr_song_import(self, req_album, song, filename):
        try:
            logger.warning("Attempting import of song via Lidarr API")
            endpoint = f"{self.config.lidarr_address}/api/v1/manualimport"
            headers = {"X-Api-Key": self.config.lidarr_api_key, "Content-Type": "application/json"}
            full_file_path = os.path.join(req_album["album_full_path"], filename)
            data = {
                "id": song["track_id"],
                "path": full_file_path,
                "name": song["track_title"],
                "artistId": req_album["artist_id"],
                "albumId": req_album["album_id"],
                "albumReleaseId": req_album["album_release_id"],
                "quality": {},
                "releaseGroup": "",
                "indexerFlags": 0,
                "downloadId": "",
                "additionalFile": False,
                "replaceExistingFiles": False,
                "disableReleaseSwitching": False,
                "rejections": [],
            }
            response = requests.post(endpoint, json=[data], headers=headers)
            if response.status_code == 202:
                logger.warning("Song import initiated")
            else:
                logger.error(
                    f"Import Attempt - Failed to initiate song import: {response.status_code}"
                )
                logger.error(f"Import Attempt - Error message: {response.text}")

        except Exception as e:
            logger.error(f"Error occurred while attempting import of song: {str(e)}")

    def trigger_lidarr_scan(self):
        try:
            endpoint = "/api/v1/rootfolder"
            headers = {"X-Api-Key": self.config.lidarr_api_key}
            root_folder_list = []
            response = requests.get(f"{self.config.lidarr_address}{endpoint}", headers=headers)
            endpoint = "/api/v1/command"
            if response.status_code == 200:
                root_folders = response.json()
                for folder in root_folders:
                    root_folder_list.append(folder["path"])
            else:
                logger.warning("No Lidarr root folders found")

            if root_folder_list:
                data = {"name": "RescanFolders", "folders": root_folder_list}
                headers = {
                    "X-Api-Key": self.config.lidarr_api_key,
                    "Content-Type": "application/json",
                }
                response = requests.post(
                    f"{self.config.lidarr_address}{endpoint}", json=data, headers=headers
                )
                if response.status_code != 201:
                    logger.warning("Failed to start lidarr library scan")

        except Exception as e:
            logger.error(f"Lidarr library scan failed: {str(e)}")

        else:
            logger.warning("Lidarr library scan started")

    def convert_to_lidarr_format(self, input_string):
        bad_characters = r'\/<>?*:|"'
        good_characters = "++  !--  "
        translation_table = str.maketrans(bad_characters, good_characters)
        result = input_string.translate(translation_table)
        return result.strip()
