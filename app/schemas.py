from pydantic import BaseModel
from typing import List, Optional
from pydantic import ConfigDict
class UserBase(BaseModel):
    id: str
    name: str
    gender: str
    orientation: str

class GenreBase(BaseModel):
    name: str

class CompatibilityRequest(BaseModel):
    user1_id: str
    user2_id: str

class CompatibilityResponse(BaseModel):
    user1: UserBase
    user2: UserBase
    shared_genres: List[str]
    shared_songs: int
    shared_playlists: int
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
    orientation: str
    age: int

class Playlist(BaseModel):
    id: str
    name: str
    public: bool
    created: str


class Genre(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)