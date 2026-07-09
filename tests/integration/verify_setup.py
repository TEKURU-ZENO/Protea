import sys
from pathlib import Path

# Setup pathing to resolve imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_config_loading():
    print("[TEST] Importing configurations...")
    from services.api.core.config import settings
    print(f"[TEST] Successfully loaded environment: {settings.ENVIRONMENT}")
    assert settings.ENVIRONMENT in ["development", "production", "docker", "gpu"]

def test_api_import():
    print("[TEST] Importing main API router...")
    from services.api.main import app
    print(f"[TEST] Successfully imported FastAPI app: {app.title}")
    assert app.title == "PROTEA Platform API"

def test_cypher_file():
    print("[TEST] Verifying Neo4j cypher script...")
    cypher_file = Path(__file__).resolve().parents[2] / "graph" / "knowledge_graph" / "seed_schema.cypher"
    assert cypher_file.exists()
    print(f"[TEST] Found cypher file: {cypher_file.name}")

if __name__ == "__main__":
    print("Running integration sanity checks...")
    test_config_loading()
    test_api_import()
    test_cypher_file()
    print("All sanity checks passed successfully!")
