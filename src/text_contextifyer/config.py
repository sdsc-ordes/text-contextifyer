from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ONTOLOGY_SPARQL_ENDPOINT: str
    GRAPHDB_USERNAME: str
    GRAPHDB_PASSWORD: str
    NAMED_GRAPHS: str = ""  # <-- string for .env parsing

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_graph_iris(self) -> list[str]:
        return [g.strip() for g in self.NAMED_GRAPHS.split(",") if g.strip()]

settings = Settings()
