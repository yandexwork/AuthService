#AuthService

Гайд по запуску:
- заполнить env по env_example
- указать путь в docker-compose до проекта
- запуск докера: docker compose build && docker compose down && docker compose up -d

Сделать миграцию в контейнере: poetry run alembic revision --autogenerate -m "your-comment"
Запустить тесты: poetry run pytest -s
