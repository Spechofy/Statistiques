from pydantic import BaseModel
from typing import List, Optional


class Orientation(BaseModel):
    name: str


class UserBase(BaseModel):
    id: str
    name: str
    gender: str
    orientation: Orientation


class GenreBase(BaseModel):
    name: str


class CompatibilityRequest(BaseModel):
    user1_id: str
    user2_id: str


class UserWithOrientation(BaseModel):
    id: str
    name: str
    gender: str
    age: int
    orientation: Orientation


class CompatibilityResponse(BaseModel):
    user1: UserBase
    user2: UserBase
    shared_genres: List[str]
    shared_songs: int
    shared_playlists: int
    compatibility_score: float


class OrientationCompatibilityResponse(BaseModel):
    user1_id: str
    user2_id: str
    compatibility_score: float


class RelationResponse(BaseModel):
    message: str
    song_id: str
    genre_name: str


class Artist(BaseModel):
    id: str
    name: str
    followers: Optional[int] = None


class Song(BaseModel):
    id: str
    title: str
    duration: int
    explicit: bool


class User(BaseModel):
    id: str
    name: str
    gender: str
    age: int


class Playlist(BaseModel):
    id: str
    name: str
    public: bool
    created: str


class Genre(BaseModel):
    name: str
