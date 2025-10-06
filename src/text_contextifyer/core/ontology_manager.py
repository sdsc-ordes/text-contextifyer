from rdflib import Graph, URIRef, RDFS, SKOS
from SPARQLWrapper import SPARQLWrapper, JSON
from text_contextifyer.config import settings

class OntologyManager:
    def __init__(self):
        self.sparql_endpoint = settings.ONTOLOGY_SPARQL_ENDPOINT
        self.username = settings.GRAPHDB_USERNAME
        self.password = settings.GRAPHDB_PASSWORD
        self.named_graphs = settings.get_graph_iris()
        if not self.sparql_endpoint:
            raise ValueError(
                "No SPARQL endpoint provided in .env via ONTOLOGY_SPARQL_ENDPOINT"
            )
        self.graph = Graph()
        self.predicate_label_map: dict[str, dict[str, str]] = {}

    def load_ontologies(self):
        """
        Load ontology triples from GraphDB (from named graphs).
        """
        sparql = SPARQLWrapper(self.sparql_endpoint)
        if self.username and self.password:
            sparql.setCredentials(self.username, self.password)

        for graph_uri in self.named_graphs:
            sparql.setQuery(f"""
            CONSTRUCT {{ ?s ?p ?o }}
            WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}
            """)
            sparql.setReturnFormat("xml")
            results_graph = sparql.query().convert()  # This is already an rdflib.Graph
            self.graph += results_graph  # merge graphs instead of parse(data=...)
        print(len(self.graph), "triples loaded from", len(self.named_graphs), "graphs.")
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
