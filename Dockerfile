# Use official Python image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy project files
COPY . /app/

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc curl

# Install dockerize
RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz | tar -xzv -C /usr/local/bin

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run migrations, collectstatic, and start the server, ensuring the database is ready
CMD ["sh", "-c", "dockerize -wait tcp://db:5432 -timeout 20s python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
