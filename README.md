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
Make sure your SPARQL endpoint is running and configured in the .env file. Then run:
```bash
poetry install
pytest
```
to run tests or
```bash
 PYTHONPATH=src poetry run uvicorn text_contextifyer.api.main:app --reload
```
to start the microservice which can then be checked used interactively at http://127.0.0.1:8000/docs
