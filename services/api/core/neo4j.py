from neo4j import GraphDatabase, Driver
from typing import Optional
from services.api.core.config import settings
from services.api.core.logging import logger

class Neo4jManager:
    def __init__(self):
        self.driver: Optional[Driver] = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            self.driver.verify_connectivity()
            logger.info("Successfully established Neo4j connection and verified connectivity.")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            raise e

    def disconnect(self):
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection.")

    def check_health(self) -> bool:
        if not self.driver:
            return False
        try:
            # Run simple ping query
            with self.driver.session() as session:
                val = session.run("RETURN 1 AS val").single()
                return val["val"] == 1 if val else False
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False

neo4j_client = Neo4jManager()
