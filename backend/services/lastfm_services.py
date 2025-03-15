import time

import pylast
import requests
from logger import logger


class LastFMService:
    def __init__(self, api_key, api_secret, rate_limit):
        self.lastfm_network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)
        self.rate_limit = rate_limit

    def generate_recommendations(self, artist_name):
        logger.info(f"Searching for new recommendations via LastFM for {artist_name}")
        try:
            artist_obj = self.lastfm_network.get_artist(artist_name)
            related_artists = artist_obj.get_similar()
            return self._process_related_artists(related_artists)

        except Exception as e:
            logger.error(f"Error with LastFM on artist '{artist_name}': {str(e)}")
            return []

    def _process_related_artists(self, related_artists):
        recommended_list = []
        for related_artist in related_artists:
            try:
                artist_obj = self.lastfm_network.get_artist(related_artist.item.name)
                genres = (
                    ", ".join(
                        [tag.item.get_name().title() for tag in artist_obj.get_top_tags()[:5]]
                    )
                    or "Unknown Genre"
                )
                listeners = artist_obj.get_listener_count() or 0
                play_count = artist_obj.get_playcount() or 0
                image_link = self._get_artist_image(related_artist.item.name)
                overview = (
                    artist_obj.get_bio_content()
                    or f"No Biography available for: {related_artist.item.name}"
                )

                new_artist = {
                    "name": related_artist.item.name,
                    "genre": genres,
                    "status": "",
                    "image": image_link if image_link else "https://placehold.co/300x200",
                    "play_count": play_count,
                    "listeners": listeners,
                    "overview": overview,
                }
                recommended_list.append(new_artist)
                logger.info(f"Sleeping for {self.rate_limit} seconds to prevent API Blocking")
                time.sleep(self.rate_limit)

            except Exception as e:
                logger.error(f"LastFM Error processing related artist: {str(e)}")

        return recommended_list

    def _get_artist_image(self, artist_name):
        try:
            endpoint = "https://api.deezer.com/search/artist"
            response = requests.get(endpoint, params={"q": artist_name})
            data = response.json()

            if "data" in data and data["data"]:
                artist_info = data["data"][0]
                return (
                    artist_info.get("picture_xl")
                    or artist_info.get("picture_large")
                    or artist_info.get("picture_medium")
                    or artist_info.get("picture", "")
                )

        except Exception as e:
            logger.error(f"Deezer Error: {str(e)}")

        return None

    def _format_numbers(self, count):
        if count >= 1000000:
            return f"{count / 1000000:.1f}M"
        elif count >= 1000:
            return f"{count / 1000:.1f}K"
        else:
            return count
