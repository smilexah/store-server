DOCKER_COMPOSE = docker-compose
IMAGE_NAME = django_app

build:
	$(DOCKER_COMPOSE) up --build

# Start the containers in detached mode
up:
	$(DOCKER_COMPOSE) up -d

# Stop the containers
down:
	$(DOCKER_COMPOSE) down

# Remove unused Docker images and volumes
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans

# Run Django migrations
migrate:
	$(DOCKER_COMPOSE) run --rm web python manage.py migrate

create-superuser:
	$(DOCKER_COMPOSE) run --rm web python manage.py createsuperuser

product-fixtures:
	$(DOCKER_COMPOSE) run --rm web python manage.py loaddata ./products/fixtures/categories.json ./products/fixtures/goods.json

# Collect static files
collectstatic:
	$(DOCKER_COMPOSE) run --rm web python manage.py collectstatic --noinput

# Build the Docker image and run it in production
prod:
	$(DOCKER_COMPOSE) -f docker-compose.prod.yml up --build
