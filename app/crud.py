from .database import db
from .schemas import CompatibilityResponse

class CRUD:
    @staticmethod
    def get_user_compatibility(user1_id: str, user2_id: str):
        query = """
    MATCH (u1:User {id: $user1_id}), (u2:User {id: $user2_id})
    
    // Genres en commun (avec COALESCE pour gérer les null)
    OPTIONAL MATCH (u1)-[:LIKES_GENRE]->(g:Genre)<-[:LIKES_GENRE]-(u2)
    WITH u1, u2, COALESCE(collect(DISTINCT g.name), []) AS common_genres
    
    // Chansons likées en commun
    OPTIONAL MATCH (u1)-[:LIKED_SONG]->(s:Song)<-[:LIKED_SONG]-(u2)
    WITH u1, u2, common_genres, COALESCE(count(s), 0) AS shared_songs
    
    // Playlists suivies en commun (publiques)
    OPTIONAL MATCH (u1)-[:FOLLOWS_PLAYLIST]->(p:Playlist {public: true})<-[:FOLLOWS_PLAYLIST]-(u2)
    WITH u1, u2, common_genres, shared_songs, COALESCE(count(p), 0) AS shared_playlists
    
    // Playlists personnelles avec chansons en commun
    OPTIONAL MATCH (u1)-[:OWNS]->(pl1:Playlist)-[:CONTAINS]->(ps:Song)<-[:CONTAINS]-(pl2:Playlist)<-[:OWNS]-(u2)
    WITH u1, u2, common_genres, shared_songs, shared_playlists, 
         COALESCE(count(DISTINCT ps), 0) AS personal_playlist_common_songs
    
    // Calcul du score total
    WITH u1, u2, common_genres, shared_songs, shared_playlists, personal_playlist_common_songs,
         size(common_genres) AS common_genres_count,
         (size(common_genres) + shared_songs + shared_playlists + personal_playlist_common_songs) AS total_common
    
    // Construction du résultat avec toutes les clés requises
    RETURN {
      user1: u1 {.*},
      user2: u2 {.*},
      shared_genres: common_genres,
      shared_songs: shared_songs,
      shared_playlists: shared_playlists, // Maintenant toujours présent
      shared_public_playlists: shared_playlists, // Alias pour compatibilité
      personal_playlist_common_songs: personal_playlist_common_songs,
      compatibility_score: CASE 
        WHEN total_common > 0 
        THEN round(
          (common_genres_count*0.35 + shared_songs*0.3 + shared_playlists*0.2 + personal_playlist_common_songs*0.15) / 
          total_common * 100, 
          2
        )
        ELSE 0.0
      END
    } AS result
    """
    
        with db.get_session() as session:
            result = session.run(query, user1_id=user1_id, user2_id=user2_id)
            return result.single()["result"]

    
    @staticmethod
    def get_top_compatible_users(user_id: str, limit: int = 5):
        query = """
    MATCH (target:User {id: $user_id})
MATCH (other:User)
WHERE other.id <> $user_id

// Calcul des composants séparément
OPTIONAL MATCH (target)-[:LIKED]->(s:Song)<-[:LIKED]-(other)
WITH target, other, count(s) AS common_songs

OPTIONAL MATCH (target)-[:FOLLOWS]->(p:Playlist {public: true})<-[:FOLLOWS]-(other)
WITH target, other, common_songs, count(p) AS public_playlists

OPTIONAL MATCH (target)-[:OWNS]->(pl:Playlist)-[:CONTAINS]->(ps:Song)<-[:CONTAINS]-(other_pl:Playlist)<-[:OWNS]-(other)
WITH other, common_songs, public_playlists, count(DISTINCT ps) AS personal_matches,
     (common_songs + public_playlists + count(DISTINCT ps)) AS total_common

WHERE total_common > 0
RETURN {
    user: other {.*},
    common_songs: common_songs,
    public_playlists: public_playlists,
    personal_playlist_matches: personal_matches,
    compatibility_score: CASE 
        WHEN total_common > 0 THEN 
            round(
                (common_songs * 0.4 + public_playlists * 0.3 + personal_matches * 0.3) / 
                (common_songs + public_playlists + personal_matches) * 100,
                2
            )
        ELSE 0
    END
} AS result
ORDER BY result.compatibility_score DESC
LIMIT $limit
    """
        with db.get_session() as session:
            return [record["result"] for record in session.run(query, user_id=user_id, limit=limit)]