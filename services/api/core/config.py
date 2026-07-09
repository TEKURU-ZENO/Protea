import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Settings overridden by Env if provided
    POSTGRES_URL: str = "postgresql://protea_user:protea_secure_password@localhost:5432/protea"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_secure_password"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minio_admin"
    MINIO_SECRET_KEY: str = "minio_secure_password"
    MINIO_SECURE: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def load_yaml_config(env: str) -> Dict[str, Any]:
    # Locate workspace root config file
    root_dir = Path(__file__).resolve().parents[3]
    config_file = root_dir / "configs" / f"{env}.yaml"
    
    if not config_file.exists():
        # Fallback to local configs directory if run differently
        config_file = Path("/app/configs") / f"{env}.yaml"
        if not config_file.exists():
            return {}

    with open(config_file, "r") as f:
        return yaml.safe_load(f) or {}

def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    yaml_data = load_yaml_config(env)
    
    # Extract DB configs from YAML
    db_config = yaml_data.get("database", {})
    pg_config = db_config.get("postgres", {})
    neo_config = db_config.get("neo4j", {})
    redis_config = db_config.get("redis", {})
    qdrant_config = db_config.get("qdrant", {})
    minio_config = db_config.get("minio", {})

    # Construct arguments mapping defaults from YAML
    init_args = {
        "ENVIRONMENT": env,
        "DEBUG": yaml_data.get("debug", True),
        "POSTGRES_URL": pg_config.get("url", "postgresql://protea_user:protea_secure_password@localhost:5432/protea"),
        "NEO4J_URI": neo_config.get("uri", "bolt://localhost:7687"),
        "NEO4J_USER": neo_config.get("user", "neo4j"),
        "NEO4J_PASSWORD": neo_config.get("password", "neo4j_secure_password"),
        "REDIS_HOST": redis_config.get("host", "localhost"),
        "REDIS_PORT": redis_config.get("port", 6379),
        "QDRANT_HOST": qdrant_config.get("host", "localhost"),
        "QDRANT_PORT": qdrant_config.get("port", 6333),
        "MINIO_ENDPOINT": minio_config.get("endpoint", "localhost:9000"),
        "MINIO_ACCESS_KEY": minio_config.get("access_key", "minio_admin"),
        "MINIO_SECRET_KEY": minio_config.get("secret_key", "minio_secure_password"),
        "MINIO_SECURE": minio_config.get("secure", False)
    }

    # Instantiating Settings will override constructor with actual environment variables
    return Settings(**init_args)

settings = get_settings()
