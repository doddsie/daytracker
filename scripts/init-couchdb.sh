#!/bin/bash
set -e

# Wait for CouchDB to be up
until curl -s "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/" > /dev/null; do
    echo "Waiting for CouchDB to be ready..."
    sleep 2
done

echo "CouchDB is up, initializing..."

# Initialize the cluster (required for single node setup)
curl -X POST "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/_cluster_setup" \
    -H "Content-Type: application/json" \
    -d "{\"action\": \"finish_cluster\"}"

# Create system databases
for db in _users _replicator _global_changes; do
    if curl -s "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/$db" | grep -q "not_found"; then
        echo "Creating system database: $db"
        curl -X PUT "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/$db"
    else
        echo "System database $db already exists"
    fi
done

# Create application database if it doesn't exist
if curl -s "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/${COUCHDB_DB}" | grep -q "not_found"; then
    echo "Creating application database: ${COUCHDB_DB}"
    curl -X PUT "http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@couchdb:5984/${COUCHDB_DB}"
else
    echo "Application database ${COUCHDB_DB} already exists"
fi

echo "CouchDB initialization completed successfully"