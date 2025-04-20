
if docker-compose ps -q | grep -q .; then
  echo "Docker Compose is running — bringing it down and wiping volumes"
  docker-compose down -v
else
  echo "Docker Compose is not running"
fi

echo "Starting database docker and running migrations"
docker-compose up migrator --build