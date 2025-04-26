from app.database import db
import random
from faker import Faker

fake = Faker()

def populate_data():
    with db.get_session() as session:
        # Nettoyage
        session.run("MATCH (n) DETACH DELETE n")

        # Création des genres
        genres = ["Pop", "Rock", "Hip-Hop", "Electro", "Jazz"]
        for genre in genres:
            session.run("CREATE (:Genre {name: $name})", name=genre)

        # Création des artistes
        artists = [fake.name() for _ in range(20)]
        for i, artist in enumerate(artists):
            session.run(
                "CREATE (:Artist {id: $id, name: $name, followers: $followers})",
                id=f"a{i}", name=artist, followers=random.randint(1000, 1000000)
            )

        # Création des chansons
        songs = [fake.catch_phrase() for _ in range(50)]
        for i, song in enumerate(songs):
            session.run(
                """CREATE (:Song {
                    id: $id, 
                    title: $title, 
                    duration: $duration,
                    explicit: $explicit
                })""",
                id=f"s{i}", 
                title=song,
                duration=random.randint(120, 300),
                explicit=random.choice([True, False])
            )

        # Création des utilisateurs
        for i in range(10):
            session.run(
                """CREATE (:User {
                    id: $id,
                    name: $name,
                    gender: $gender,
                    orientation: $orientation,
                    age: $age
                })""",
                id=f"u{i}",
                name=fake.name(),
                gender=random.choice(["M", "F", "NB"]),
                orientation=random.choice(["hetero", "homo", "bi", "pan"]),
                age=random.randint(18, 60)
            )

        # Création des relations
        # Artistes -> Genres
        session.run("""
            MATCH (a:Artist), (g:Genre)
            WITH a, g, rand() AS r
            WHERE r < 0.3
            CREATE (a)-[:HAS_GENRE]->(g)
        """)

        # Chansons -> Artistes
        session.run("""
            MATCH (s:Song), (a:Artist)
            WITH s, a, rand() AS r
            WHERE r < 0.4
            CREATE (s)-[:BY_ARTIST]->(a)
        """)

        # Chansons -> Genres
        session.run("""
            MATCH (s:Song), (g:Genre)
            WITH s, g, rand() AS r
            WHERE r < 0.5
            CREATE (s)-[:HAS_GENRE]->(g)
        """)

        # Users -> Likes
        session.run("""
            MATCH (u:User), (s:Song)
            WITH u, s, rand() AS r
            WHERE r < 0.2
            CREATE (u)-[:LIKED {timestamp: datetime()}]->(s)
        """)

        # Playlists
        for i in range(15):
            owner = f"u{random.randint(0, 9)}"
            session.run("""
                MATCH (u:User {id: $owner})
                CREATE (u)-[:OWNS]->(:Playlist {
                    id: $id,
                    name: $name,
                    public: $public,
                    created: datetime()
                })
            """, 
            id=f"p{i}", 
            name=f"{fake.word()} Mix", 
            public=random.choice([True, False]),
            owner=owner)

        # Playlist -> Songs
        session.run("""
            MATCH (p:Playlist), (s:Song)
            WITH p, s, rand() AS r
            WHERE r < 0.3
            CREATE (p)-[:CONTAINS]->(s)
        """)

        print("Peuplement de la base terminé avec succès!")

if __name__ == "__main__":
    populate_data()