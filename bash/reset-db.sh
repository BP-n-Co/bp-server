
if docker-compose ps -q | grep -q .; then
  echo "Docker Compose is running — bringing it down and wiping volumes"
  docker-compose down -v
else
  echo "Docker Compose is not running"
fi

if [ -d ".db" ]; then
  echo "Removing current database"
  rm -rd ".db"
else
  echo "No previous db founded"
fi


echo "Grabing latest mock database"
cp -r .db_example .db

echo "Starting database docker and running migrations"
docker-compose up migrator --build