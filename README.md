# text-contextifyer

Turn plain Markdown into enriched Markdown with ontology-based hyperlinks.

## Features
- Load an RDF/OWL ontology into memory
- Extract labels (`rdfs:label`, `skos:prefLabel`)
- Match words in Markdown text against ontology terms (fuzzy or exact)
- Replace matches with hyperlinks

## Example

Input:
Computer science and Geology are fascinating fields.

Output:
[Computer science](someurl-about-computerscience.org) and [geology](some-otherurl-related-to-geology.org) are fascinating fields.

## Usage
```bash
poetry install
pytest

---

## 📄 `src/text_contextifyer/config.py`
```python
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Path or endpoint to ontology
    ontology_files: list[str] = ["tests/data/example.ttl"]

    class Config:
        env_prefix = "CTXFY_"
        case_sensitive = False
