from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    ONTOLOGY_SPARQL_ENDPOINT: str
    SPARQL_USERNAME: Optional[str] = None
    SPARQL_PASSWORD: Optional[str] = None
    NAMED_GRAPHS: str = ""  # Comma-separated list of named graph URIs (optional)
    USE_DEFAULT_GRAPH: bool = True  # If true and NAMED_GRAPHS is empty, query the default graph

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_graph_iris(self) -> list[str]:
        return [g.strip() for g in self.NAMED_GRAPHS.split(",") if g.strip()]

settings = Settings()
