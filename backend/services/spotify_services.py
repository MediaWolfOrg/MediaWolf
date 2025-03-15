import spotipy
from logger import logger
from services.config_services import Config
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyService:
    def __init__(self, config: Config):
        self.config = config

    def perform_spotify_search(self, search_req):
        try:
            parsed_results = None
            query_type = search_req.get("type", "track")
            query = search_req.get("query")
            search_type = "album,artist,playlist,track" if query_type == "all" else query_type

            logger.info(f"Search query: {query}, Type: {search_type}")
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.config.spotify_client_id,
                client_secret=self.config.spotify_client_secret,
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

            results = self.sp.search(
                q=query, limit=self.config.spotify_search_limit, type=search_type
            )
            parsed_results = self.parse_spotify_data(results)

        except Exception as e:
            logger.error(f"Spotify Search Error: {str(e)}")

        finally:
            return parsed_results

    def parse_spotify_data(self, results):
        parsed_results = {"tracks": [], "albums": [], "artists": [], "playlists": []}

        # Parsing tracks from the search results
        if "tracks" in results:
            for item in results["tracks"]["items"]:
                parsed_results["tracks"].append(
                    {
                        "type": "track",
                        "name": item["name"],
                        "artist": item["artists"][0]["name"],
                        "album": item["album"]["name"],
                        "url": item["external_urls"]["spotify"],
                        "image": item["album"]["images"][0]["url"]
                        if item["album"]["images"]
                        else None,
                    }
                )

        # Parsing albums from the search results
        if "albums" in results:
            for item in results["albums"]["items"]:
                parsed_results["albums"].append(
                    {
                        "type": "album",
                        "name": item["name"],
                        "artist": item["artists"][0]["name"],
                        "release_date": item["release_date"],
                        "url": item["external_urls"]["spotify"],
                        "image": item["images"][0]["url"] if item["images"] else None,
                    }
                )

        # Parsing artists from the search results
        if "artists" in results:
            for item in results["artists"]["items"]:
                parsed_results["artists"].append(
                    {
                        "type": "artist",
                        "name": item["name"],
                        "followers": item["followers"]["total"],
                        "url": item["external_urls"]["spotify"],
                        "image": item["images"][0]["url"] if item["images"] else None,
                    }
                )

        # Parsing playlists from the search results
        if "playlists" in results:
            for item in results["playlists"]["items"]:
                if not item:
                    continue
                parsed_results["playlists"].append(
                    {
                        "type": "playlist",
                        "name": item["name"],
                        "owner": item["owner"]["display_name"],
                        "url": item["external_urls"]["spotify"],
                        "image": item["images"][0]["url"] if item["images"] else None,
                    }
                )

        return {key: value for key, value in parsed_results.items() if value}
