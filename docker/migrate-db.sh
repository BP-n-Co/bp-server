#!/bin/bash
echo "Waiting for MySQL to be available..."
until mysqladmin ping -h"$MYSQL_HOST" -P"$MYSQL_PORT" --silent; do
  echo "MySQL not ready, retrying in 2 seconds. $MYSQL_HOST:$MYSQL_PORT"
  sleep 2
done
echo "Connected to MySql on $MYSQL_HOST:$MYSQL_PORT"

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations applied"
