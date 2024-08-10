#!/bin/bash
set -e

# Start PostgreSQL in the background
docker-entrypoint.sh postgres &

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
  until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER"; do
    >&2 echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done

  >&2 echo "PostgreSQL is up - executing commands"
}

# Function to create the user and database if they do not exist
create_user_and_db() {
  PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d postgres <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$POSTGRES_USER') THEN
            CREATE ROLE $POSTGRES_USER WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';
            ALTER ROLE $POSTGRES_USER CREATEDB;
        END IF;
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB') THEN
            CREATE DATABASE $POSTGRES_DB;
            GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
        END IF;
    END
    \$\$;
EOSQL
}


# Wait for PostgreSQL to be ready
wait_for_postgres

# Create user and database if they do not exist
create_user_and_db

# Check if the geo_features table exists
TABLE_EXISTS=$(psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'geo_features');")

if [ "$TABLE_EXISTS" = " f" ]; then
  echo "Initializing database with GeoJSON data..."
  python3 /usr/local/bin/upload_geojson.py
else
  echo "GeoJSON data already loaded."
fi

# Wait for PostgreSQL process to terminate (so the container doesn't exit)
wait
