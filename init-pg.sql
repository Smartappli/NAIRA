-- Enhanced PostgreSQL initialization script
-- Create databases with proper configuration

-- Enable pgvector extension in template1 to make it available for all new databases
\c template1;
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users with specific privileges
CREATE USER airflow_user WITH PASSWORD 'airflow_secure_pass_2024';
CREATE USER sentry_user WITH PASSWORD 'sentry_secure_pass_2024';
CREATE USER vectordb_user WITH PASSWORD 'vectordb_secure_pass_2024';

-- Create databases with specific owners
CREATE DATABASE airflow
    WITH OWNER airflow_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

CREATE DATABASE sentry
    WITH OWNER sentry_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

CREATE DATABASE vectordb
    WITH OWNER vectordb_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow_user;
GRANT ALL PRIVILEGES ON DATABASE sentry TO sentry_user;
GRANT ALL PRIVILEGES ON DATABASE vectordb TO vectordb_user;

-- Connect to each database and ensure extensions are available
\c airflow;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO airflow_user;

\c sentry;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS citext;
GRANT ALL ON SCHEMA public TO sentry_user;

\c vectordb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO vectordb_user;

-- Create schema for different namespaces in vectordb
CREATE SCHEMA IF NOT EXISTS embeddings;
CREATE SCHEMA IF NOT EXISTS documents;
GRANT ALL ON SCHEMA embeddings TO vectordb_user;
GRANT ALL ON SCHEMA documents TO vectordb_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO airflow_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO airflow_user;

\c postgres;
-- Log completion
SELECT 'Database initialization completed successfully' as status;