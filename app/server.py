from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
import datetime
from uuid import uuid4

from .schemas import DiaryCreate, DiaryOut, DiaryUpdate
from .db import CouchDBClient

app = FastAPI(
    title="DayTracker Diary API",
    description="A small REST API to create and manage diary entries stored in CouchDB.",
    version="0.1.0",
    contact={"name": "DayTracker", "email": "dev@example.com"},
    license_info={"name": "MIT"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# create a module-level db client (will initialize on first use)
_db_client = None


def get_db_client() -> CouchDBClient:
    global _db_client
    if _db_client is None:
        _db_client = CouchDBClient()
    return _db_client


@app.post(
    "/entries",
    response_model=DiaryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a diary entry",
    description="Create a new diary entry. Returns the created entry with id and revision.",
    tags=["entries"],
)
def create_entry(item: DiaryCreate, db: CouchDBClient = Depends(get_db_client)):
    payload = item.dict()
    payload["id"] = str(uuid4())
    # server-populated timestamp for the entry (UTC)
    payload["entry_date"] = datetime.datetime.utcnow()
    created = db.create_entry(payload)
    return created


@app.get(
    "/entries/{entry_id}",
    response_model=DiaryOut,
    summary="Get an entry",
    description="Retrieve a diary entry by its id.",
    tags=["entries"],
)
def read_entry(entry_id: str, db: CouchDBClient = Depends(get_db_client)):
    entry = db.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@app.get(
    "/entries",
    response_model=List[DiaryOut],
    summary="List entries",
    description="List diary entries. Use `skip` and `limit` for pagination.",
    tags=["entries"],
)
def list_entries(limit: int = 100, skip: int = 0, db: CouchDBClient = Depends(get_db_client)):
    return db.list_entries(start=skip, limit=limit)


@app.put(
    "/entries/{entry_id}",
    response_model=DiaryOut,
    summary="Update an entry",
    description="Update fields of a diary entry. Partial updates are supported.",
    tags=["entries"],
)
def update_entry(entry_id: str, update: DiaryUpdate, db: CouchDBClient = Depends(get_db_client)):
    data = {k: v for k, v in update.dict().items() if v is not None}
    try:
        updated = db.update_entry(entry_id, data)
    except KeyError:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated


@app.delete(
    "/entries/{entry_id}",
    summary="Delete an entry",
    description="Delete a diary entry by id.",
    tags=["entries"],
)
def delete_entry(entry_id: str, db: CouchDBClient = Depends(get_db_client)):
    ok = db.delete_entry(entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted": True}
