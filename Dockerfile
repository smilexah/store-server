# Use official Python image
FROM python:3.10

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy project files
COPY . /app/

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run migrations, collectstatic, and start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
