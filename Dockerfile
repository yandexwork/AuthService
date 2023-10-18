version: '3.9'

services:

  redis:
    image: redis:7.0.10
    container_name: auth-redis
    <<: *app
    volumes:
      - auth-redis-data:/data
      - ./config/redis.conf:/usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 60s
      timeout: 30s
      retries: 10
      start_period: 30s
    restart: unless-stopped
    expose:
      - 6379
    networks:
      - auth_network

  postgres:
    image: postgres:13
    container_name: auth-postgres
    <<: *app
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - auth-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
    ports:
      - "5432:5432"
    networks:
      - auth_network

volumes:
  auth-redis-data:
  auth-db-data:

networks:
  auth_network:
    external: true
