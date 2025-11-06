import os
from typing import Dict, Any, List, Optional

import httpx

COUCHDB_URL = os.getenv("COUCHDB_URL", "http://admin:password@localhost:5984")
COUCHDB_DB = os.getenv("COUCHDB_DB", "diary")


class CouchDBClient:
    """Simple CouchDB client using httpx with an in-memory fallback for tests/dev."""

    def __init__(self, url: str = COUCHDB_URL, db_name: str = COUCHDB_DB):
        self.url = url.rstrip("/")
        self.db_name = db_name
        self._use_memory = False
        self._memory: Dict[str, Dict[str, Any]] = {}

        try:
            self.client = httpx.Client(base_url=self.url, timeout=5.0)
            # ensure DB exists
            r = self.client.get(f"/{self.db_name}")
            if r.status_code == 404:
                # create DB
                self.client.put(f"/{self.db_name}")
            elif r.is_error:
                raise RuntimeError("CouchDB unreachable")
        except Exception:
            # fallback to memory store
            self._use_memory = True

    def create_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if self._use_memory:
            _id = data.get("id") or str(len(self._memory) + 1)
            doc = dict(data)
            doc["_id"] = _id
            doc["_rev"] = "1"
            self._memory[_id] = doc
            return {"id": _id, "rev": "1", **{k: v for k, v in doc.items() if not k.startswith("_")}}

        # POST to DB creates a doc with an auto-generated id
        r = self.client.post(f"/{self.db_name}", json=data)
        r.raise_for_status()
        resp = r.json()
        return {"id": resp.get("id"), "rev": resp.get("rev"), **data}

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        if self._use_memory:
            doc = self._memory.get(entry_id)
            if not doc:
                return None
            return {"id": doc.get("_id"), "rev": doc.get("_rev"), **{k: v for k, v in doc.items() if not k.startswith("_")}}

        r = self.client.get(f"/{self.db_name}/{entry_id}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        doc = r.json()
        return {"id": doc.get("_id"), "rev": doc.get("_rev"), **{k: v for k, v in doc.items() if not k.startswith("_")}}

    def update_entry(self, entry_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if self._use_memory:
            if entry_id not in self._memory:
                raise KeyError("not found")
            doc = self._memory[entry_id]
            doc.update(data)
            doc["_rev"] = str(int(doc.get("_rev", "1")) + 1)
            self._memory[entry_id] = doc
            return {"id": doc["_id"], "rev": doc["_rev"], **{k: v for k, v in doc.items() if not k.startswith("_")}}

        # fetch current doc to get _rev
        cur = self.client.get(f"/{self.db_name}/{entry_id}")
        if cur.status_code == 404:
            raise KeyError("not found")
        cur.raise_for_status()
        doc = cur.json()
        rev = doc.get("_rev")
        # merge and PUT
        payload = {**doc, **data, "_rev": rev}
        r = self.client.put(f"/{self.db_name}/{entry_id}", json=payload)
        r.raise_for_status()
        resp = r.json()
        return {"id": resp.get("id") or entry_id, "rev": resp.get("rev"), **data}

    def delete_entry(self, entry_id: str) -> bool:
        if self._use_memory:
            if entry_id not in self._memory:
                return False
            del self._memory[entry_id]
            return True

        cur = self.client.get(f"/{self.db_name}/{entry_id}")
        if cur.status_code == 404:
            return False
        cur.raise_for_status()
        rev = cur.json().get("_rev")
        r = self.client.delete(f"/{self.db_name}/{entry_id}", params={"rev": rev})
        r.raise_for_status()
        return True

    def list_entries(self, start: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        if self._use_memory:
            keys = list(self._memory.keys())[start:start + limit]
            out: List[Dict[str, Any]] = []
            for k in keys:
                d = self._memory[k]
                out.append({"id": d.get("_id"), "rev": d.get("_rev"), **{kk: vv for kk, vv in d.items() if not kk.startswith("_")}})
            return out

        r = self.client.get(f"/{self.db_name}/_all_docs", params={"include_docs": "true", "limit": limit, "skip": start})
        r.raise_for_status()
        rows = r.json().get("rows", [])
        out = []
        for row in rows:
            doc = row.get("doc", {})
            out.append({"id": doc.get("_id"), "rev": doc.get("_rev"), **{kk: vv for kk, vv in doc.items() if not kk.startswith("_")}})
        return out
