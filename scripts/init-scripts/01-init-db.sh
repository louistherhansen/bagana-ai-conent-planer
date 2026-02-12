#!/bin/bash
# Database initialization script
# This script runs automatically when PostgreSQL container starts for the first time

set -e

echo "Initializing BAGANA AI database..."

# Create extensions if needed
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Set timezone
    SET timezone = 'UTC';
    
    -- Create schemas if needed
    CREATE SCHEMA IF NOT EXISTS public;
    
    -- Grant permissions
    GRANT ALL ON SCHEMA public TO $POSTGRES_USER;
    
    -- Log initialization
    SELECT 'Database initialized successfully' AS status;
EOSQL

echo "Database initialization completed!"
