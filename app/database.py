from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        return self

    def close(self):
        if self.driver:
            self.driver.close()

    def get_session(self):
        return self.driver.session()

# Singleton pour la connexion
db = Neo4jConnection().connect()