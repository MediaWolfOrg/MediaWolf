from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship
from db.base import Base


class DismissedArtist(Base):
    __tablename__ = "dismissed_artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class RecommendedArtist(Base):
    __tablename__ = "recommended_artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    genre = Column(String)
    listeners = Column(Integer)
    play_count = Column(Integer)
    image = Column(String)
    overview = Column(String)
    status = Column(String, default="")

    lidarr_artist_id = Column(Integer, ForeignKey("lidarr_artists.id"))

    lidarr_artist = relationship("LidarrArtist", back_populates="recommended_artists")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "listeners": f"Listeners: {self._format_numbers(self.listeners)}",
            "play_count": f"Play Count: {self._format_numbers(self.play_count)}",
            "image": self.image,
            "overview": self.overview,
            "status": self.status,
        }

    @staticmethod
    def _format_numbers(count):
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)


class LidarrArtist(Base):
    __tablename__ = "lidarr_artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    genres = Column(String)
    mbid = Column(String)

    recommended_artists = relationship("RecommendedArtist", back_populates="lidarr_artist")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "mbid": self.mbid,
        }
