# src/text_contextifyer/cli.py
import argparse
from pathlib import Path
from text_contextifyer.core.ontology_manager import OntologyManager
from text_contextifyer.core.matcher import Matcher
from text_contextifyer.transformers.markdown_transformer import MarkdownTransformer
from rdflib import URIRef
from text_contextifyer.config import settings
print("✅ CLI loaded endpoint:", settings.ONTOLOGY_SPARQL_ENDPOINT)


def build_label_map(ontology_manager: OntologyManager):
    """
    Replicates the label map creation logic from main.py:19–23.
    Converts ontology labels into a flat lookup table for Matcher.
    """
    label_map = {
    label: URIRef(iri)
    for predicate_map in ontology_manager.get_predicate_label_map().values()
    for label, iri in predicate_map.items()}

    return label_map


def process_file(input_path: Path, output_path: Path, transformer: MarkdownTransformer):
    """Read, transform, and write a single markdown file."""
    text = input_path.read_text(encoding="utf-8")
    enriched = transformer.transform(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(enriched, encoding="utf-8")
    print(f"✅ Processed {input_path} → {output_path}")


def process_path(input_path: Path, output_path: Path, transformer: MarkdownTransformer):
    """Handle either a single file or a directory."""
    if input_path.is_file():
        out_file = output_path if output_path.suffix else output_path / input_path.name
        process_file(input_path, out_file, transformer)
    else:
        for file in input_path.rglob("*.md"):
            relative = file.relative_to(input_path)
            target = output_path / relative
            process_file(file, target, transformer)


def main():
    parser = argparse.ArgumentParser(description="Batch process markdown files with text-contextifyer")
    parser.add_argument("input", help="Input markdown file or directory")
    parser.add_argument("-o", "--output", required=True, help="Output file or directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # 🔹 Reuse existing logic from main.py
    ontology_manager = OntologyManager()
    ontology_manager.load_ontologies()
    label_map = build_label_map(ontology_manager)
    matcher = Matcher(label_map)
    transformer = MarkdownTransformer(matcher)
    

    process_path(input_path, output_path, transformer)
