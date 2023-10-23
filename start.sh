alembic upgrade head
uvicorn --reload --host 0.0.0.0 --port 8000 src.main:app