# Сервис авторизации

Сервис авторизации позволяет регистироваться и логиниться пользователям, обновлять токены, делать полный выход, логиниться с помощью OAuth, меня пароль для входа. Также реализован функционал по созданию и выдаче ролей.  
Стек: Python, FastAPI, Postgres, Alembic, sqlalchemy, Redis, OAuth, Docker, Nginx.

## Гайд по запуску:
- заполнить env по env_example
- указать путь в docker-compose до проекта
- запуск докера: docker compose build && docker compose down && docker compose up -d

## Дополнительно:
- Сделать миграцию в контейнере: poetry run alembic revision --autogenerate -m "your-comment"
- Запустить тесты: poetry run pytest -s
