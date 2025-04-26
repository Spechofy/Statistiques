from fastapi import FastAPI, HTTPException
from .schemas import *
from .crud import CRUD
from .database import db
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()

@app.get("/users/{user_id}/compatibility/top")
async def get_top_compatible_users(user_id: str, limit: int = 5):
    try:
        return CRUD.get_top_compatible_users(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/compatibility/", response_model=CompatibilityResponse)
async def calculate_compatibility(pair: CompatibilityRequest):
    try:
        result = CRUD.get_user_compatibility(pair.user1_id, pair.user2_id)
        if not result:
            raise HTTPException(status_code=404, detail="Users not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/genres/", response_model=Genre)
def create_genre(genre: Genre):
    with db.get_session() as session:
        result = session.run(
            "CREATE (g:Genre {name: $name}) RETURN g",
            name=genre.name
        )
        node = result.single()["g"]
        return {"name": node["name"]}  # Retourne un dict conforme au modèle Genre
@app.get("/genres/", response_model=List[Genre])
def get_genres():
    with db.get_session() as session:
        result = session.run("MATCH (g:Genre) RETURN g.name AS name")
        return [{"name": record["name"]} for record in result]

# --- Endpoints pour Artists ---
@app.post("/artists/", response_model=Artist)
def create_artist(artist: Artist):
    with db.get_session() as session:
        result = session.run(
            """CREATE (a:Artist {id: $id, name: $name, followers: $followers})
            RETURN a {.*}""",
            **artist.model_dump()
        )
        return result.single()["a"]

@app.get("/artists/{artist_id}", response_model=Artist)
def get_artist(artist_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (a:Artist {id: $id}) RETURN a {.*}",
            id=artist_id
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Artist not found")
        return data["a"]

# --- Endpoints pour Songs ---
@app.post("/songs/", response_model=Song)
def create_song(song: Song):
    with db.get_session() as session:
        result = session.run(
            """CREATE (s:Song {id: $id, title: $title, 
                duration: $duration, explicit: $explicit})
            RETURN s {.*}""",
            **song.model_dump()
        )
        return result.single()["s"]

@app.put("/songs/{song_id}", response_model=Song)
def update_song(song_id: str, song: Song):
    with db.get_session() as session:
        result = session.run(
            """MATCH (s:Song {id: $id})
            SET s += {title: $title, duration: $duration, explicit: $explicit}
            RETURN s {.*}""",
            id=song_id,
            **song.dict(exclude={"id"})
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Song not found")
        return data["s"]

# --- Endpoints pour Users ---
@app.get("/users/{user_id}", response_model=User)
def get_artist(user_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (u:User {id: $id}) RETURN u {.*}",
            id=user_id
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Artist not found")
        return data["u"]
@app.post("/users/", response_model=User)
def create_user(user: User):
    with db.get_session() as session:
        result = session.run(
            """CREATE (u:User {id: $id, name: $name, gender: $gender,
                orientation: $orientation, age: $age})
            RETURN u {.*}""",
            **user.model_dump()
        )
        return result.single()["u"]

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (u:User {id: $id}) DETACH DELETE u RETURN count(u) AS count",
            id=user_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted"}

# --- Endpoints pour Playlists ---
@app.post("/playlists/", response_model=Playlist)
def create_playlist(playlist: Playlist):
    with db.get_session() as session:
        result = session.run(
            """CREATE (p:Playlist {id: $id, name: $name, 
                public: $public, created: $created})
            RETURN p {.*}""",
            **playlist.model_dump()
        )
        return result.single()["p"]

@app.get("/playlists/{playlist_id}", response_model=Playlist)
def get_playlist(playlist_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (p:Playlist {id: $id}) RETURN p {.*}",
            id=playlist_id
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return data["p"]

@app.post("/songs/{song_id}/genres/{genre_name}", status_code=201)
def add_genre_to_song(song_id: str, genre_name: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (s:Song {id: $song_id}), (g:Genre {name: $genre_name})
            MERGE (s)-[:HAS_GENRE]->(g)
            RETURN s.id AS song_id, g.name AS genre_name""",
            song_id=song_id,
            genre_name=genre_name
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Song or Genre not found")
        return {
            "message": "Genre added to song successfully",
            "song_id": data["song_id"],
            "genre_name": data["genre_name"]
        }
    
@app.post("/users/{user_id}/liked_songs/{song_id}", status_code=201)
def like_song(user_id: str, song_id: str):
    """
    Ajoute une relation LIKED entre un utilisateur et une chanson
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id}), (s:Song {id: $song_id})
            MERGE (u)-[r:LIKED]->(s)
            RETURN r
            """,
            user_id=user_id,
            song_id=song_id
        )
        if not result.single():
            raise HTTPException(status_code=404, detail="User or Song not found")
        return {"message": "Song liked successfully"}

@app.delete("/users/{user_id}/liked_songs/{song_id}")
def unlike_song(user_id: str, song_id: str):
    """
    Supprime une relation LIKED
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[r:LIKED]->(s:Song {id: $song_id})
            DELETE r
            RETURN count(r) AS count
            """,
            user_id=user_id,
            song_id=song_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Like relationship not found")
        return {"message": "Song unliked successfully"}
@app.post("/users/{user_id}/owned_playlists/{playlist_id}", status_code=201)
def assign_playlist_owner(user_id: str, playlist_id: str):
    """
    Crée une relation OWNS entre un utilisateur et une playlist
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id}), (p:Playlist {id: $playlist_id})
            MERGE (u)-[r:OWNS]->(p)
            RETURN r
            """,
            user_id=user_id,
            playlist_id=playlist_id
        )
        if not result.single():
            raise HTTPException(status_code=404, detail="User or Playlist not found")
        return {"message": "Ownership assigned successfully"}

@app.delete("/users/{user_id}/owned_playlists/{playlist_id}")
def remove_playlist_owner(user_id: str, playlist_id: str):
    """
    Supprime une relation OWNS
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[r:OWNS]->(p:Playlist {id: $playlist_id})
            DELETE r
            RETURN count(r) AS count
            """,
            user_id=user_id,
            playlist_id=playlist_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Ownership not found")
        return {"message": "Ownership removed successfully"}
    
@app.post("/playlists/{playlist_id}/songs/{song_id}", status_code=201)
def add_song_to_playlist(playlist_id: str, song_id: str):
    """
    Ajoute une chanson à une playlist
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (p:Playlist {id: $playlist_id}), (s:Song {id: $song_id})
            MERGE (p)-[r:CONTAINS]->(s)
            RETURN r
            """,
            playlist_id=playlist_id,
            song_id=song_id
        )
        if not result.single():
            raise HTTPException(status_code=404, detail="Playlist or Song not found")
        return {"message": "Song added to playlist successfully"}

@app.delete("/playlists/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(playlist_id: str, song_id: str):
    """
    Supprime une chanson d'une playlist
    """
    with db.get_session() as session:
        result = session.run(
            """
            MATCH (p:Playlist {id: $playlist_id})-[r:CONTAINS]->(s:Song {id: $song_id})
            DELETE r
            RETURN count(r) AS count
            """,
            playlist_id=playlist_id,
            song_id=song_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Song not found in playlist")
        return {"message": "Song removed from playlist successfully"}