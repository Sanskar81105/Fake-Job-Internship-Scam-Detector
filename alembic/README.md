Alembic usage (quick):

1. Install alembic:
   pip install alembic

2. Initialize repository (if not present):
   alembic init alembic

3. Configure alembic.ini:
   - Set sqlalchemy.url = <your DATABASE_URL> or set env var in env.py

4. Create revision:
   alembic revision --autogenerate -m "create analyses table"

5. Apply migration:
   alembic upgrade head

Notes:
- The repository includes models.py; autogenerate will inspect models to build migrations.
- Alternatively, run the provided create_tables.sql manually.
