# text-contextifyer

Turn plain Markdown into enriched Markdown with ontology-based hyperlinks. This tool supports small-medium sized ontologies only right now, as they need to be loaded into memory. 

## Features
- Load an RDF/OWL ontology into memory from a SPARQL endpoint.
- Extract labels (`rdfs:label`, `skos:prefLabel`)
- Match words in Markdown text against ontology terms (fuzzy or exact)
- Replace matches with hyperlinks in the markdown file supplied

## Example

Input:
```markdown
Computer science and Geology are fascinating fields.
```
Output:
```markdown
[Computer science](someurl-about-computerscience.org) and [geology](some-otherurl-related-to-geology.org) are fascinating fields.
```

## Usage

First, make sure your GraphDB SPARQL endpoint is running and create a `.env` file based on `.env.dist` with your configuration.

### Running Locally

To run tests:
```bash
poetry install
pytest
```

To start the microservice locally:
```bash
PYTHONPATH=src poetry run uvicorn text_contextifyer.api.main:app --reload
```

### Running with Docker

1. Build the Docker image:
```bash
docker build -t text-contextifyer .
```

2. Run the container (choose one of the following methods):

   a. If GraphDB is running on your host machine:
   ```bash
   docker run --rm --network=host --env-file .env text-contextifyer
   ```

   b. Or using port mapping and Docker's host resolution:
   ```bash
   # First, modify your .env file to use host.docker.internal instead of localhost:
   # ONTOLOGY_SPARQL_ENDPOINT=http://host.docker.internal:7200/repositories/your-repo
   docker run --rm -p 8000:8000 --env-file .env text-contextifyer
   ```

The API documentation will be available at http://localhost:8000/docs

### Testing the API

Once the service is running, you can test it with curl (make the ontology you point to contains labels that appear in the text you are contextifying):
```bash
curl -X POST http://localhost:8000/contextify \
  -H "Content-Type: application/json" \
  -d '{"markdown":"Computer science and Geology are fascinating fields."}'
```