import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)


# Fixtures pour les données de test
@pytest.fixture
def test_user():
    return {"id": "test_user", "name": "Test User", "gender": "M", "age": 25, "orientation": {"name": "hetero"}}


@pytest.fixture
def test_artist():
    return {"id": "test_artist", "name": "Test Artist", "followers": 1000}


@pytest.fixture
def test_song():
    return {"id": "test_song", "title": "Test Song", "duration": 180, "explicit": False}


@pytest.fixture
def test_playlist():
    return {"id": "test_playlist", "name": "Test Playlist", "public": True, "created": "2023-01-01"}


@pytest.fixture
def test_genre():
    return {"name": "TestGenre"}


@pytest.fixture
def test_genre_with_id():
    return {"name": "TestGenreWithID", "id": "test_genre_with_id"}


@pytest.fixture
def test_playlist_with_songs(test_playlist, test_song):
    return {
        "id": test_playlist["id"],
        "name": test_playlist["name"],
        "public": test_playlist["public"],
        "created": test_playlist["created"],
        "songs": [test_song],
    }


# Tests pour les utilisateurs
def test_create_and_get_user(test_user):
    response = client.post("/users/", json=test_user)
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]

    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]


def test_delete_user(test_user):
    client.post("/users/", json=test_user)
    response = client.delete(f"/users/{test_user['id']}")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted"


# Tests pour les artistes
def test_create_and_get_artist(test_artist):
    response = client.post("/artists/", json=test_artist)
    assert response.status_code == 200

    response = client.get(f"/artists/{test_artist['id']}")
    assert response.status_code == 200
    assert response.json()["followers"] == test_artist["followers"]


def test_update_artist(test_artist):
    client.post("/artists/", json=test_artist)
    updated_artist = {"id": test_artist["id"], "name": "Updated Artist", "followers": 2000}
    response = client.put(f"/artists/{test_artist['id']}", json=updated_artist)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Artist"


def test_delete_artist(test_artist):
    client.post("/artists/", json=test_artist)
    response = client.delete(f"/artists/{test_artist['id']}")
    assert response.status_code == 200
    assert response.json()["message"] == "Artist deleted successfully"


# Tests pour les genres
def test_create_and_get_genre(test_genre):
    response = client.post("/genres/", json=test_genre)
    assert response.status_code == 200

    response = client.get(f"/genres/{test_genre['name']}")
    assert response.status_code == 200
    assert response.json()["name"] == test_genre["name"]


def test_update_genre(test_genre):
    client.post("/genres/", json=test_genre)
    updated_genre = {"name": "UpdatedGenre"}
    response = client.put(f"/genres/{test_genre['name']}", json=updated_genre)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedGenre"


def test_delete_genre(test_genre):
    client.post("/genres/", json=test_genre)
    response = client.delete(f"/genres/{test_genre['name']}")
    assert response.status_code == 200
    assert response.json()["message"] == "Genre deleted successfully"


# Tests pour les chansons
def test_create_and_get_song(test_song):
    response = client.post("/songs/", json=test_song)
    assert response.status_code == 200

    response = client.get("/songs/")
    assert response.status_code == 200
    assert any(song["id"] == test_song["id"] for song in response.json())


def test_update_song(test_song):
    client.post("/songs/", json=test_song)
    updated_song = {"id": test_song['id'], "title": "Updated Song", "duration": 200, "explicit": True}
    response = client.put(f"/songs/{test_song['id']}", json=updated_song)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Song"


def test_delete_song(test_song):
    client.post("/songs/", json=test_song)
    response = client.delete(f"/songs/{test_song['id']}")
    assert response.status_code == 200
    assert response.json()["message"] == "Song deleted successfully"


# Tests pour les playlists
def test_create_and_get_playlist(test_playlist, test_user):
    client.post("/users/", json=test_user)
    response = client.post("/playlists/", json=test_playlist)
    assert response.status_code == 200

    response = client.get(f"/playlists/{test_playlist['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == test_playlist["id"]


def test_update_playlist(test_playlist, test_user):
    client.post("/users/", json=test_user)
    client.post("/playlists/", json=test_playlist)
    updated_playlist = {"id": test_playlist['id'], "name": "Updated Playlist", "public": False, "created": "2023-02-01"}
    response = client.put(f"/playlists/{test_playlist['id']}", json=updated_playlist)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Playlist"


def test_delete_playlist(test_playlist, test_user):
    client.post("/users/", json=test_user)
    client.post("/playlists/", json=test_playlist)
    response = client.delete(f"/playlists/{test_playlist['id']}")
    assert response.status_code == 200
    assert response.json()["message"] == "Playlist deleted successfully"


# Nettoyage après les tests
@pytest.fixture(autouse=True)
def cleanup():
    yield
    with db.get_session() as session:
        session.run("MATCH (n) WHERE n.id STARTS WITH 'test_' DETACH DELETE n")
        session.run("MATCH (g:Genre) WHERE g.name STARTS WITH 'Test' DELETE g")
