# text-contextifyer

Turn plain Markdown into enriched Markdown with ontology-based hyperlinks. This tool supports small-medium sized ontologies only right now, as they need to be loaded into memory. 

## Features
- Load an RDF/OWL ontology from any SPARQL 1.1 compliant endpoint (Apache Jena, GraphDB, Virtuoso, etc.)
- Extract labels (`rdfs:label`, `skos:prefLabel`)
- Match words in Markdown text against ontology terms (fuzzy or exact)
- Replace matches with hyperlinks in the markdown file supplied
- Support for both named graphs and default graph queries

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

First, make sure your SPARQL endpoint is running and create a `.env` file based on `.env.dist` with your configuration.

### Configuration

The application supports any SPARQL 1.1 compliant endpoint. Configure your `.env` file:

```bash
# Required: Your SPARQL endpoint URL
ONTOLOGY_SPARQL_ENDPOINT=http://localhost:3030/myDataset/sparql  # Apache Jena example
# or
ONTOLOGY_SPARQL_ENDPOINT=http://localhost:7200/repositories/myRepo  # GraphDB example

# Optional: Authentication (if required)
SPARQL_USERNAME=admin
SPARQL_PASSWORD=password

# Graph selection (choose one):
# Option 1: Query specific named graphs
NAMED_GRAPHS=http://example.org/graph1,http://example.org/graph2

# Option 2: Query the default graph (leave NAMED_GRAPHS empty)
USE_DEFAULT_GRAPH=true
```

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
docker build -t text-contextifyer:latest .
```

2. Run the container (choose one of the following methods):

   **Option A: Using host network mode (Linux - Recommended)**
   
   If your SPARQL endpoint is running on your host machine (e.g., `localhost:3030`), use host network mode:
   ```bash
   docker run --rm --network host --env-file .env -e PORT=8001 text-contextifyer:latest
   ```
   
   The service will be available at `http://localhost:8001`
   
   Note: With `--network host`, you need to specify a custom `PORT` if 8000 is already in use.

   **Option B: Using port mapping (Mac/Windows)**
   
   For Mac/Windows, use `host.docker.internal` to access host services:
   ```bash
   docker run --rm -p 8001:8000 --env-file .env \
     -e ONTOLOGY_SPARQL_ENDPOINT=http://host.docker.internal:3030/arema/sparql \
     text-contextifyer:latest
   ```
   
   The service will be available at `http://localhost:8001`

The API documentation will be available at the URL shown above with `/docs` appended (e.g., `http://localhost:8001/docs`)

### Testing the API

Once the service is running, you can test it with curl (make sure the ontology you point to contains labels that appear in the text you are contextifying):
```bash
# Adjust port number if you used a different port
curl -X POST http://localhost:8001/contextify \
  -H "Content-Type: application/json" \
  -d '{"markdown":"Computer science and Geology are fascinating fields."}'
```