from .database import db
from .schemas import CompatibilityResponse

class CRUD:
    @staticmethod
    def get_user_compatibility(user1_id: str, user2_id: str):
        query = """
MATCH (u1:User {id: $user1_id}), (u2:User {id: $user2_id})

// Genres en commun
OPTIONAL MATCH (u1)-[:LIKES_GENRE]->(g:Genre)<-[:LIKES_GENRE]-(u2)
WITH u1, u2, COALESCE(collect(DISTINCT g.name), []) AS shared_genres

// Chansons likées en commun
OPTIONAL MATCH (u1)-[:LIKED]->(s:Song)<-[:LIKED]-(u2)
WITH u1, u2, shared_genres, COALESCE(count(s), 0) AS shared_songs

// Playlists publiques communes
OPTIONAL MATCH (u1)-[:FOLLOWS]->(p:Playlist {public: true})<-[:FOLLOWS]-(u2)
WITH u1, u2, shared_genres, shared_songs, COALESCE(count(p), 0) AS shared_playlists

// Playlists personnelles
OPTIONAL MATCH (u1)-[:OWNS]->(pl1:Playlist)-[:CONTAINS]->(ps:Song)<-[:CONTAINS]-(pl2:Playlist)<-[:OWNS]-(u2)
WITH u1, u2, shared_genres, shared_songs, shared_playlists, 
     COALESCE(count(DISTINCT ps), 0) AS personal_common_songs,
     [
       size([(u1)-[:OWNS]->(p)-[:CONTAINS]->() | p.id]),
       size([(u2)-[:OWNS]->(p)-[:CONTAINS]->() | p.id]),
       size([(u1)-[:OWNS]->(p)-[:CONTAINS]->() WHERE (u2)-[:OWNS]->(p)-[:CONTAINS]->() | p.id])
     ] AS similarity_data

// Calcul final avec plafonnement
WITH u1, u2, 
     shared_genres,
     shared_songs,
     shared_playlists,
     personal_common_songs,
     CASE 
       WHEN similarity_data[0] + similarity_data[1] > 0 
       THEN (similarity_data[2] * 1.0) / (similarity_data[0] + similarity_data[1] - similarity_data[2]) 
       ELSE 0 
     END AS playlist_similarity,
     size(shared_genres) AS genre_count

WITH u1, u2, 
     shared_genres,
     shared_songs,
     shared_playlists,
     personal_common_songs,
     playlist_similarity,
      (
       (CASE WHEN genre_count > 0 THEN 1 ELSE 0 END) * 25 +  // Max 25 points
       (CASE WHEN shared_songs > 20 THEN 20 ELSE shared_songs END) * 1.75 +  // 35 points max
       (CASE WHEN shared_playlists > 10 THEN 10 ELSE shared_playlists END) * 1.5 +  // 15 points max
       (CASE WHEN personal_common_songs > 50 THEN 50 ELSE personal_common_songs END) * 0.4 +  // 20 points max
       playlist_similarity * 5  // Max 5 points
     ) AS compatibility_score

RETURN {
  user1: u1 {.*},
  user2: u2 {.*},
  shared_genres: shared_genres,
  shared_songs: shared_songs,
  shared_playlists: shared_playlists,
  personal_playlist_common_songs: personal_common_songs,
  playlist_similarity: round(playlist_similarity, 4),
  compatibility_score: round(
    CASE WHEN compatibility_score > 100 THEN 100 ELSE compatibility_score END,
    2
  )
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

// Genres en commun
OPTIONAL MATCH (target)-[:LIKES_GENRE]->(g:Genre)<-[:LIKES_GENRE]-(other)
WITH target, other, count(DISTINCT g) AS shared_genres_count

// Chansons likées en commun
OPTIONAL MATCH (target)-[:LIKED]->(s:Song)<-[:LIKED]-(other)
WITH target, other, shared_genres_count, count(s) AS shared_songs

// Playlists publiques communes
OPTIONAL MATCH (target)-[:FOLLOWS]->(p:Playlist {public: true})<-[:FOLLOWS]-(other)
WITH target, other, shared_genres_count, shared_songs, count(p) AS shared_playlists

// Playlists personnelles
OPTIONAL MATCH (target)-[:OWNS]->(pl:Playlist)-[:CONTAINS]->(ps:Song)<-[:CONTAINS]-(other_pl:Playlist)<-[:OWNS]-(other)
WITH target, other, 
     shared_genres_count,
     shared_songs,
     shared_playlists,
     count(DISTINCT ps) AS personal_common_songs,
     [
       size([(target)-[:OWNS]->(p)-[:CONTAINS]->() WHERE p IS NOT NULL | p]),
       size([(other)-[:OWNS]->(p)-[:CONTAINS]->() WHERE p IS NOT NULL | p]),
       size([(target)-[:OWNS]->(p)-[:CONTAINS]->() WHERE (other)-[:OWNS]->(p)-[:CONTAINS]->() AND p IS NOT NULL | p])
     ] AS similarity_data

// Calcul de compatibilité
WITH other,
     COALESCE(shared_genres_count, 0) AS shared_genres_count,
     COALESCE(shared_songs, 0) AS shared_songs,
     COALESCE(shared_playlists, 0) AS shared_playlists,
     COALESCE(personal_common_songs, 0) AS personal_common_songs,
     CASE 
       WHEN size(similarity_data) = 3 AND similarity_data[0] + similarity_data[1] > 0 
       THEN (similarity_data[2] * 1.0) / (similarity_data[0] + similarity_data[1] - similarity_data[2]) 
       ELSE 0 
     END AS playlist_similarity

// Calcul du score final avec plafonnement
WITH other,
     shared_genres_count,
     shared_songs,
     shared_playlists,
     personal_common_songs,
     playlist_similarity,
     (
       (CASE WHEN shared_genres_count > 0 THEN 1 ELSE 0 END) * 25 +
       (CASE WHEN shared_songs > 20 THEN 20 ELSE shared_songs END) * 1.75 +
       (CASE WHEN shared_playlists > 10 THEN 10 ELSE shared_playlists END) * 1.5 +
       (CASE WHEN personal_common_songs > 50 THEN 50 ELSE personal_common_songs END) * 0.4 +
       playlist_similarity * 5
     ) AS raw_score

RETURN {
    user: other {.*},
    shared_genres: shared_genres_count,
    shared_songs: shared_songs,
    shared_playlists: shared_playlists,
    personal_playlist_matches: personal_common_songs,
    compatibility_score: round(
        CASE WHEN raw_score > 100 THEN 100 ELSE raw_score END,
        2
    )
} AS result
ORDER BY result.compatibility_score DESC
LIMIT $limit
"""
        with db.get_session() as session:
            return [record["result"] for record in session.run(query, user_id=user_id, limit=limit)]