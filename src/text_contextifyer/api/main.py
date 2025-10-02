from fastapi import FastAPI
from pydantic import BaseModel
from rdflib import URIRef

from text_contextifyer.core.matcher import Matcher
from text_contextifyer.transformers.markdown_transformer import MarkdownTransformer
from text_contextifyer.core.ontology_manager import OntologyManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Text Contextifyer API")

# Load ontology from GraphDB at startup
ontology_manager = OntologyManager()
ontology_manager.load_ontologies()

label_map = {
    label: URIRef(iri)
    for predicate_map in ontology_manager.get_predicate_label_map().values()
    for label, iri in predicate_map.items()
}
print("=== LABEL MAP ===")
for label, iri in label_map.items():
    print(f"{label} -> {iri}")
print("=================")

matcher = Matcher(label_map)
transformer = MarkdownTransformer(matcher)

class MarkdownRequest(BaseModel):
    markdown: str

class MarkdownResponse(BaseModel):
    markdown: str

@app.post("/contextify", response_model=MarkdownResponse)
def contextify_md(request: MarkdownRequest):
    """
    Accept markdown text and return hyperlinked markdown
    based on fuzzy matches to ontology terms.
    """
    output_md = transformer.transform(request.markdown)
    return MarkdownResponse(markdown=output_md)
