#!/bin/bash
set -e

# Require DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is required."
  exit 1
fi

echo "Safety check on DATABASE_URL..."
python3 -c "
import os, sys
url = os.environ.get('DATABASE_URL', '')
low = url.lower()
if any(x in low for x in ('prod', 'production', 'amazonaws.com', 'azure.com', 'render.com')):
    print('DATABASE_URL looks production-like. Refusing to run migrations on it.')
    sys.exit(1)
print('DATABASE_URL safety check passed.')
"

# Run alembic current
echo "Checking current migration state..."
alembic current

# Run alembic upgrade head
echo "Upgrading database to head..."
alembic upgrade head

# Verify Content Factory tables/columns exist
echo "Verifying Content Factory tables and columns exist..."
python3 -c "
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect

async def verify():
    url = os.environ['DATABASE_URL']
    if 'postgresql' in url and '+asyncpg' not in url:
        url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    engine = create_async_engine(url)
    
    def check_schema(conn):
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        
        required_tables = [
            'content_generation_artifacts',
            'content_artifact_sources',
            'content_generation_runs',
            'content_generation_tasks',
            'content_seed_runs',
            'content_promotion_events',
            'assessment_blueprints',
            'study_plan_templates'
        ]
        
        for table in required_tables:
            if table not in tables:
                print(f'Error: Required table {table} does not exist!')
                sys.exit(1)
            print(f'Table verified: {table}')
            
        # Check specific columns in content_artifact_sources
        columns = inspector.get_columns('content_artifact_sources')
        col_names = [c['name'] for c in columns]
        required_source_cols = [
            'source_document_id', 
            'source_chunk_id', 
            'license_status', 
            'source_quality_score'
        ]
        for col in required_source_cols:
            if col not in col_names:
                print(f'Error: content_artifact_sources is missing column {col}!')
                sys.exit(1)
            print(f'Column verified: content_artifact_sources.{col}')
            
        # Check specific columns in content_generation_tasks
        task_columns = inspector.get_columns('content_generation_tasks')
        task_col_names = [c['name'] for c in task_columns]
        required_task_cols = [
            'idempotency_key', 
            'depends_on_task_ids', 
            'validation_failures', 
            'token_usage'
        ]
        for col in required_task_cols:
            if col not in task_col_names:
                print(f'Error: content_generation_tasks is missing column {col}!')
                sys.exit(1)
            print(f'Column verified: content_generation_tasks.{col}')
            
        print('All Content Factory table and column checks PASSED.')

    async with engine.connect() as conn:
        await conn.run_sync(check_schema)
    await engine.dispose()

asyncio.run(verify())
"

# Run alembic downgrade -1
echo "Testing rollback (downgrade -1)..."
alembic downgrade -1

# Run alembic upgrade head again
echo "Re-upgrading to head..."
alembic upgrade head

echo "Migration verification completed successfully."
