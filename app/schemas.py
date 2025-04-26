from pydantic import BaseModel
from typing import List, Optional

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