import urllib.parse

from db.database_handler import DatabaseHandler
from db.music_models import DismissedArtist, LidarrArtist, RecommendedArtist
from logger import logger
from sqlalchemy import func


class MusicDBHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.recommended_artists = []

    def get_existing_db_artists(self):
        """Retrieve all artist names from the database (lowercase for case-insensitive matching)."""
        artists = {}
        try:
            session = self.SessionLocal()
            artists = {artist.name.lower() for artist in session.query(LidarrArtist.name).all()}
            session.close()

        except Exception as e:
            logger.error(f"Error Getting Existing DB Artists: {str(e)}")

        finally:
            return artists

    def add_lidarr_artists(self, lidarr_artists):
        try:
            """Add new artists from Lidarr if they are not already in the database."""
            artists_in_db = self.get_existing_db_artists()
            new_artists_count = 0

            for artist in lidarr_artists:
                artist_name = artist["artistName"].strip().lower()
                if artist_name not in artists_in_db:
                    artist_data = {
                        "name": artist["artistName"].strip(),
                        "genres": ", ".join(str(item) for item in artist.get("genres", [])),
                        "mbid": artist.get("foreignArtistId", ""),
                    }
                    self.store_artist(artist_data)
                    new_artists_count += 1
                else:
                    logger.debug(f"Skipping existing artist: {artist['artistName']}")

            logger.debug(f"Added {new_artists_count} new artists.")

        except Exception as e:
            logger.error(f"Error Adding Lidarr Artist to DB: {str(e)}")

    def store_artist(self, artist_data):
        """Add a new artist to the database."""
        session = self.SessionLocal()
        try:
            artist = LidarrArtist(**artist_data)
            session.add(artist)
            session.commit()
            logger.info(f"Added artist: {artist_data['name']}")

        except Exception as e:
            logger.error(f"Error Storing Artist: {str(e)}")
            session.rollback()

        finally:
            session.close()

    def store_recommended_artists_for_lidarr_artist(self, lidarr_artist_name, recommended_artists):
        """Store recommended artists for a given Lidarr artist."""
        try:
            session = self.SessionLocal()

            lidarr_artist = (
                session.query(LidarrArtist)
                .filter(func.lower(LidarrArtist.name) == lidarr_artist_name.lower())
                .first()
            )

            if lidarr_artist:
                new_recommended_count = 0
                for recommended in recommended_artists:
                    try:
                        recommended_name = recommended["name"].strip()

                        artists_in_db = self.get_existing_db_artists()

                        if recommended_name.lower() in artists_in_db:
                            logger.info(f"Artist: {recommended_name} already in Lidarr")
                        else:
                            recommended_artist_data = {
                                "name": recommended["name"],
                                "genre": recommended["genre"],
                                "listeners": recommended["listeners"],
                                "play_count": recommended["play_count"],
                                "image": recommended["image"],
                                "overview": recommended["overview"],
                                "lidarr_artist_id": lidarr_artist.id,
                                "status": "",
                            }

                            recommended_artist = RecommendedArtist(**recommended_artist_data)
                            session.add(recommended_artist)
                            new_recommended_count += 1
                            logger.info(f"Added recommended artist: {recommended_name}")

                            lidarr_artist.recommended_artists.append(recommended_artist)

                    except Exception as e:
                        logger.error(f"Error Processing Recomendation: {recommended_name} {str(e)}")

                session.commit()
                logger.debug(
                    f"Added {new_recommended_count} new recommended artists for {lidarr_artist_name}."
                )
            else:
                logger.error(f"LidarrArtist {lidarr_artist_name} not found in the database.")

        except Exception as e:
            logger.error(f"Error Getting Recommended Artists: {str(e)}")

        finally:
            session.close()

    def refresh_recommendations(self, data):
        """Main entry function to get recommendations."""
        selected_artist = data.get("selected_artist", "").lower()
        min_play_count = data.get("min_play_count", None)
        min_listeners = data.get("min_listeners", None)
        sort_by = data.get("sort_by", "play_count")
        num_results = data.get("num_results", 5)
        page = data.get("page", None)

        if selected_artist == "all":
            db_results = self._get_random_artists(
                min_play_count, min_listeners, sort_by, num_results, page
            )
        else:
            db_results = self._get_recommended_artists_for_lidarr_artist(
                selected_artist, min_play_count, min_listeners, sort_by
            )

        json_results = [artist.as_dict() for artist in db_results]
        self.recommended_artists = json_results
        return json_results

    def _get_recommended_artists_for_lidarr_artist(
        self, lidarr_artist_name, min_play_count=None, min_listeners=None, sort_by="play_count"
    ):
        """Retrieve all recommended artists for a given Lidarr artist, with optional filtering."""
        session = self.SessionLocal()
        try:
            logger.debug(f"Getting recommended artists for: {lidarr_artist_name}")
            lidarr_artist = (
                session.query(LidarrArtist)
                .filter(func.lower(LidarrArtist.name) == lidarr_artist_name.lower())
                .first()
            )

            if lidarr_artist:
                recommended_artists = lidarr_artist.recommended_artists

                if min_play_count:
                    recommended_artists = [
                        artist
                        for artist in recommended_artists
                        if artist.play_count >= min_play_count
                    ]
                if min_listeners:
                    recommended_artists = [
                        artist
                        for artist in recommended_artists
                        if artist.listeners >= min_listeners
                    ]

                if sort_by == "plays-desc":
                    recommended_artists = sorted(
                        recommended_artists, key=lambda x: x.play_count, reverse=True
                    )
                elif sort_by == "plays-asc":
                    recommended_artists = sorted(recommended_artists, key=lambda x: x.play_count)
                elif sort_by == "listeners-desc":
                    recommended_artists = sorted(
                        recommended_artists, key=lambda x: x.listeners, reverse=True
                    )
                elif sort_by == "listeners-asc":
                    recommended_artists = sorted(recommended_artists, key=lambda x: x.listeners)

                logger.debug(
                    f"Found {len(recommended_artists)} recommended artists for: {lidarr_artist_name}"
                )
                return recommended_artists
            else:
                logger.error(f"LidarrArtist {lidarr_artist_name} not found.")
                return []

        except Exception as e:
            logger.error(
                f"Error retrieving recommended artists for: {lidarr_artist_name} -> {str(e)}"
            )
            return []

        finally:
            session.close()

    def _get_random_artists(
        self, min_play_count=None, min_listeners=None, sort_by="play_count", num_results=10, page=1
    ):
        """Retrieve random recommended artists with filters and sorting."""
        session = self.SessionLocal()
        try:
            query = session.query(RecommendedArtist)

            if min_play_count:
                query = query.filter(RecommendedArtist.play_count >= min_play_count)
            if min_listeners:
                query = query.filter(RecommendedArtist.listeners >= min_listeners)

            if sort_by == "random":
                query = query.order_by(func.random()).limit(num_results)
            elif sort_by == "plays-desc":
                query = query.order_by(RecommendedArtist.play_count.desc()).limit(num_results)
            elif sort_by == "plays-asc":
                query = query.order_by(RecommendedArtist.play_count.asc()).limit(num_results)
            elif sort_by == "listeners-desc":
                query = query.order_by(RecommendedArtist.listeners.desc()).limit(num_results)
            elif sort_by == "listeners-asc":
                query = query.order_by(RecommendedArtist.listeners.asc()).limit(num_results)

            query = query.distinct()
            artists = query.all()

            if not artists:
                logger.error("No artists found matching the criteria.")
                return []

            logger.debug(f"Artists retrieved (sorted by {sort_by}): {len(artists)} artists.")
            return artists

        except Exception as e:
            logger.error(f"Error retrieving random artists: {str(e)}")
            return []

        finally:
            session.close()

    def update_status_for_recommended_artist(self, artist_name, status):
        """Update the status of all recommended artists for a given artist name."""
        try:
            session = self.SessionLocal()

            recommended_artists = (
                session.query(RecommendedArtist)
                .filter(func.lower(RecommendedArtist.name) == artist_name.lower())
                .all()
            )

            if recommended_artists:
                for recommended_artist in recommended_artists:
                    recommended_artist.status = status

                session.commit()
                logger.info(
                    f"Updated status for {len(recommended_artists)} recommended artists "
                    f"with name '{artist_name}' to '{status}'."
                )

            for rec in self.recommended_artists:
                if rec.get("name", "").lower() == artist_name.lower():
                    rec["status"] = status

            else:
                logger.error(f"No recommended artists found for name '{artist_name}'.")

        except Exception as e:
            logger.error(f"Error updating status for recommended artist '{artist_name}': {str(e)}")

        finally:
            session.close()

    def dismiss_artist(self, raw_artist_name):
        """Mark an artist as dismissed by adding to the dismissed table."""
        session = self.get_session()
        try:
            artist_name = urllib.parse.unquote(raw_artist_name)
            dismissed_artist = DismissedArtist(name=artist_name)
            session.add(dismissed_artist)
            session.commit()
            logger.info(f"Dismissed artist: {artist_name}")

        except Exception as e:
            logger.error(f"Error dismissing artist: {str(e)}")
            session.rollback()

        finally:
            session.close()
