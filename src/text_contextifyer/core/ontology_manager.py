from rdflib import Graph, URIRef, RDFS, SKOS
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.error
from text_contextifyer.config import settings

class OntologyManager:
    def __init__(self):
        self.sparql_endpoint = settings.ONTOLOGY_SPARQL_ENDPOINT
        self.username = settings.SPARQL_USERNAME
        self.password = settings.SPARQL_PASSWORD
        self.named_graphs = settings.get_graph_iris()
        self.use_default_graph = settings.USE_DEFAULT_GRAPH
        if not self.sparql_endpoint:
            raise ValueError(
                "No SPARQL endpoint provided in .env via ONTOLOGY_SPARQL_ENDPOINT"
            )
        self.graph = Graph()
        self.predicate_label_map: dict[str, dict[str, str]] = {}

    def load_ontologies(self):
        """
        Load ontology triples from any SPARQL endpoint.
        Supports named graphs, default graph, or querying all graphs.
        """
        sparql = SPARQLWrapper(self.sparql_endpoint)
        if self.username and self.password:
            sparql.setCredentials(self.username, self.password)

        try:
            if self.named_graphs:
                # Query specific named graphs
                for graph_uri in self.named_graphs:
                    sparql.setQuery(f"""
                    CONSTRUCT {{ ?s ?p ?o }}
                    WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}
                    """)
                    sparql.setReturnFormat("xml")
                    results_graph = sparql.query().convert()
                    self.graph += results_graph
                print(f"{len(self.graph)} triples loaded from {len(self.named_graphs)} named graph(s).")
            elif self.use_default_graph:
                # Query the default graph (works with Apache Jena, GraphDB, etc.)
                sparql.setQuery("""
                CONSTRUCT { ?s ?p ?o }
                WHERE { ?s ?p ?o }
                """)
                sparql.setReturnFormat("xml")
                results_graph = sparql.query().convert()
                self.graph += results_graph
                print(f"{len(self.graph)} triples loaded from default graph.")
            else:
                raise ValueError(
                    "No graph source specified. Set NAMED_GRAPHS or USE_DEFAULT_GRAPH=true in .env"
                )
        except (ConnectionRefusedError, urllib.error.URLError) as e:
            raise ConnectionError(
                f"\nERROR: Could not connect to SPARQL endpoint at {self.sparql_endpoint}\n"
                "Please ensure that:\n"
                "1. Your SPARQL endpoint is running and accessible\n"
                "2. The endpoint URL in your .env file is correct\n"
                "3. The specified port is not blocked by a firewall\n"
                "4. Authentication credentials (if required) are correct\n"
                f"\nOriginal error: {str(e)}"
            ) from None
        # Build predicate->label map
        self._build_predicate_label_map()


    def _build_predicate_label_map(self):
        self.predicate_label_map.clear()
        for s, p, o in self.graph.triples((None, SKOS.prefLabel, None)):
            pred_str = str(p)
            if pred_str not in self.predicate_label_map:
                self.predicate_label_map[pred_str] = {}
            self.predicate_label_map[pred_str][str(o)] = str(s)

    def get_predicate_label_map(self):
        return self.predicate_label_map
