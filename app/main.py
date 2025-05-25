from fastapi import FastAPI, HTTPException
from typing import List
from .schemas import (
    CompatibilityRequest,
    CompatibilityResponse,
    Genre,
    Artist,
    Song,
    User,
    UserWithOrientation,
    Playlist,
    OrientationCompatibilityResponse,
)
from .crud import CRUD
from .database import db
from contextlib import asynccontextmanager

app = FastAPI()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    db.close()


@app.get("/")
async def root():
    return {"message": "Welcome to the Music Compatibility API"}


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
        return {"name": node["name"]}


@app.get("/genres/", response_model=List[Genre])
def get_genres():
    with db.get_session() as session:
        result = session.run("MATCH (g:Genre) RETURN g.name AS name")
        return [{"name": record["name"]} for record in result]


@app.get("/genres/{genre_name}", response_model=Genre)
def get_genre(genre_name: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (g:Genre {name: $name}) RETURN g {.*}",
            name=genre_name
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Genre not found")
        return data["g"]


@app.delete("/genres/{genre_name}")
def delete_genre(genre_name: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (g:Genre {name: $name})
            DETACH DELETE g RETURN count(g) AS count""",
            name=genre_name
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Genre not found")
        return {"message": "Genre deleted successfully"}


@app.put("/genres/{genre_name}", response_model=Genre)
def update_genre(genre_name: str, genre: Genre):
    with db.get_session() as session:
        result = session.run(
            """MATCH (g:Genre {name: $name})
            SET g.name = $new_name RETURN g {.*}""",
            name=genre_name,
            new_name=genre.name
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Genre not found")
        return data["g"]


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


@app.put("/artists/{artist_id}", response_model=Artist)
def update_artist(artist_id: str, artist: Artist):
    with db.get_session() as session:
        result = session.run(
            """MATCH (a:Artist {id: $id})
            SET a += {name: $name, followers: $followers}
            RETURN a {.*}""",
            id=artist_id,
            **artist.model_dump(exclude={"id"})
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Artist not found")
        return data["a"]


@app.delete("/artists/{artist_id}")
def delete_artist(artist_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (a:Artist {id: $id}) DETACH DELETE a RETURN count(a) AS count",
            id=artist_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Artist not found")
        return {"message": "Artist deleted successfully"}


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
            **song.model_dump(exclude={"id"})
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Song not found")
        return data["s"]


@app.get("/songs/", response_model=List[Song])
def get_songs():
    with db.get_session() as session:
        result = session.run("MATCH (s:Song) RETURN s {.*}")
        return [record["s"] for record in result]


@app.delete("/songs/{song_id}")
def delete_song(song_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (s:Song {id: $id}) DETACH DELETE s RETURN count(s) AS count",
            id=song_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Song not found")
        return {"message": "Song deleted successfully"}


# --- Endpoints pour Users ---
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (u:User {id: $id}) RETURN u {.*}",
            id=user_id
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Artist not found")
        return data["u"]


@app.post("/users/", response_model=UserWithOrientation)
def create_user(user: UserWithOrientation):
    with db.get_session() as session:
        result = session.run(
            """
            CREATE (u:User {id: $id, name: $name, gender: $gender, age: $age})
            WITH u
            MERGE (o:Orientation {name: $orientation_name})
            MERGE (u)-[:HAS_ORIENTATION]->(o)
            RETURN u.id AS id, u.name AS name, u.gender AS gender, u.age AS age, o.name AS orientation
            """,
            id=user.id,
            name=user.name,
            gender=user.gender,
            age=user.age,
            orientation_name=user.orientation.name  # Extract the name attribute
        )
        record = result.single()
        return {
            "id": record["id"],
            "name": record["name"],
            "gender": record["gender"],
            "age": record["age"],
            "orientation": {"name": record["orientation"]}
        }


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


@app.get("/playlists/", response_model=List[Playlist])
def get_playlists():
    with db.get_session() as session:
        result = session.run("MATCH (p:Playlist) RETURN p {.*}")
        return [record["p"] for record in result]


@app.put("/playlists/{playlist_id}", response_model=Playlist)
def update_playlist(playlist_id: str, playlist: Playlist):
    with db.get_session() as session:
        result = session.run(
            """MATCH (p:Playlist {id: $id})
            SET p += {name: $name, public: $public, created: $created}
            RETURN p {.*}""",
            id=playlist_id,
            **playlist.model_dump(exclude={"id"})
        )
        data = result.single()
        if not data:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return data["p"]


@app.delete("/playlists/{playlist_id}")
def delete_playlist(playlist_id: str):
    with db.get_session() as session:
        result = session.run(
            "MATCH (p:Playlist {id: $id}) DETACH DELETE p RETURN count(p) AS count",
            id=playlist_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return {"message": "Playlist deleted successfully"}


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


@app.get("/compatibility/orientation", response_model=OrientationCompatibilityResponse)
def check_orientation_compatibility(user1_id: str, user2_id: str):
    score = CRUD.get_orientation_compatibility(user1_id, user2_id)
    if score is None:
        raise HTTPException(status_code=404, detail="Compatibility not found")
    return OrientationCompatibilityResponse(
        user1_id=user1_id,
        user2_id=user2_id,
        compatibility_score=score
    )


# --- Endpoints pour Relations ---
@app.post("/users/{user_id}/likes_genre/{genre_name}", status_code=201)
def like_genre(user_id: str, genre_name: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (u:User {id: $user_id}), (g:Genre {name: $genre_name})
            MERGE (u)-[:LIKES_GENRE]->(g)
            RETURN g.name AS genre_name""",
            user_id=user_id,
            genre_name=genre_name
        )
        if not result.single():
            raise HTTPException(status_code=404, detail="User or Genre not found")
        return {"message": "Genre liked successfully"}


@app.delete("/users/{user_id}/likes_genre/{genre_name}")
def unlike_genre(user_id: str, genre_name: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (u:User {id: $user_id})-[r:LIKES_GENRE]->(g:Genre {name: $genre_name})
            DELETE r
            RETURN count(r) AS count""",
            user_id=user_id,
            genre_name=genre_name
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Like relationship not found")
        return {"message": "Genre unliked successfully"}


@app.post("/users/{user_id}/follows/{artist_id}", status_code=201)
def follow_artist(user_id: str, artist_id: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (u:User {id: $user_id}), (a:Artist {id: $artist_id})
            MERGE (u)-[:FOLLOWS]->(a)
            RETURN a.id AS artist_id""",
            user_id=user_id,
            artist_id=artist_id
        )
        if not result.single():
            raise HTTPException(status_code=404, detail="User or Artist not found")
        return {"message": "Artist followed successfully"}


@app.delete("/users/{user_id}/follows/{artist_id}")
def unfollow_artist(user_id: str, artist_id: str):
    with db.get_session() as session:
        result = session.run(
            """MATCH (u:User {id: $user_id})-[r:FOLLOWS]->(a:Artist {id: $artist_id})
            DELETE r
            RETURN count(r) AS count""",
            user_id=user_id,
            artist_id=artist_id
        )
        if result.single()["count"] == 0:
            raise HTTPException(status_code=404, detail="Follow relationship not found")
        return {"message": "Artist unfollowed successfully"}
