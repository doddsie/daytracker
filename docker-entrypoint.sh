#!/usr/bin/env bash
set -euo pipefail

COUCH_URL=${COUCHDB_URL:-http://admin:password@couchdb:5984}

# extract host and port for health check
# remove protocol
no_proto=${COUCH_URL#*://}
# drop credentials if present
hostport=${no_proto#*@}
host=${hostport%%/*}

echo "Waiting for CouchDB at $host..."
# try for up to 30 seconds
for i in {1..30}; do
  if curl -sS "http://$host/_up" >/dev/null 2>&1; then
    echo "CouchDB is up"
    break
  fi
  echo "CouchDB not ready, sleeping... ($i)"
  sleep 1
done

# run the main process
exec "$@"
