import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)


# Fixtures pour les données de test
@pytest.fixture
def test_user():
    return {"id": "test_user", "name": "Test User", "gender": "M","age": 25,"orientation": {"name":"hetero"}}


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
    # Créer une playlist avec une chanson
    return {
        "id": test_playlist["id"],
        "name": test_playlist["name"],
        "public": test_playlist["public"],
        "created": test_playlist["created"],
        "songs": [test_song],
    }


# Tests pour les utilisateurs
def test_create_and_get_user(test_user):
    # --- Test création ---
    response = client.post("/users/", json=test_user)
    assert response.status_code == 200
    assert response.json()["id"] == test_user["id"]
    assert response.json()["name"] == test_user["name"]

    # --- Test récupération ---
    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["name"] == test_user["name"]
    assert data["gender"] == test_user["gender"]
    assert data["age"] == test_user["age"]


# Tests pour les artistes
def test_create_and_get_artist(test_artist):
    response = client.post("/artists/", json=test_artist)
    assert response.status_code == 200

    response = client.get(f"/artists/{test_artist['id']}")
    assert response.status_code == 200
    assert response.json()["followers"] == test_artist["followers"]


# Tests pour les playlists
def test_create_and_get_playlist(test_playlist, test_user):
    # Créer l'utilisateur d'abord
    client.post("/users/", json=test_user)

    # Créer la playlist
    response = client.post("/playlists/", json=test_playlist)
    assert response.status_code == 200

    # Tester la récupération
    response = client.get(f"/playlists/{test_playlist['id']}")
    assert response.status_code == 200


def test_song_relations(test_song, test_genre):
    # Setup
    client.post("/songs/", json=test_song)
    client.post("/genres/", json=test_genre)

    # Test
    response = client.post(f"/songs/{test_song['id']}/genres/{test_genre['name']}")
    assert response.status_code == 201  # Vérifie le code de statut
    assert response.json()["message"] == "Genre added to song successfully"
    assert response.json()["song_id"] == test_song["id"]
    assert response.json()["genre_name"] == test_genre["name"]



# Nettoyage après les tests
@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Supprimer toutes les données de test
    with db.get_session() as session:
        session.run("MATCH (n) WHERE n.id STARTS WITH 'test_' DETACH DELETE n")
        session.run("MATCH (g:Genre) WHERE g.name STARTS WITH 'Test' DELETE g")
