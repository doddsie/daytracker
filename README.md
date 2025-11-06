# daytracker# DayTracker Diary API

A small FastAPI application providing a REST API to track diary entries stored in CouchDB. This repository includes a Dockerfile for containerizing the API and a docker-compose file to run CouchDB and the API locally for development.

Features
- Create, read, update, delete diary entries
- Search entries by date range and tags
- Uses CouchDB as persistent storage

Quick start (requires Docker & Docker Compose)

1. Start CouchDB and the API (run these commands on your host machine — do not run Docker inside containers):

```bash
# use the host's Docker CLI
docker compose up --build
```

2. Open the API docs: http://localhost:8000/docs

Environment variables (can be set in `.env` or docker-compose):
- COUCHDB_URL - CouchDB URL, e.g. http://couchdb:5984
- COUCHDB_DB - Database name (default: diary)
- COUCHDB_USER - Admin username (for initial CouchDB setup)
- COUCHDB_PASSWORD - Admin password

Development (without Docker)
1. Create a venv and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Development using Docker (recommended)

Run CouchDB and the API together from the host. The API container will wait until CouchDB is healthy before starting.

```bash
# build and start both services (host command)
docker compose up --build
```

The API will be available at http://localhost:8000 and CouchDB at http://localhost:5984

Running tests in the container (no Docker-in-Docker)

If you want to run the test suite from inside the API container, run pytest in the container by invoking the test command via `docker compose run` (the API container image must be built first):

```bash
# build the image then run pytest inside the api service container
docker compose build api
docker compose run --rm api pytest -q
```

Or use the `tester` service (recommended) which reuses the API image and waits for CouchDB to be healthy:

```bash
# build services
docker compose build
# run tests (this runs pytest inside the `api` image)
docker compose run --rm tester
```

These commands run pytest inside the API container; they do not run Docker from inside a container.

Running tests

```bash
pytest -q
```

License: MIT
