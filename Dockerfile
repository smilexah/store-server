# Use the official Python image based on Ubuntu
FROM python:3.13.1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev netcat \
    && rm -rf /var/lib/apt/lists/*

# Copy the project requirements
COPY store/store/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .

# Expose the application port
EXPOSE 8000

# Start the application with Gunicorn
CMD ["gunicorn", "store.wsgi:application", "--bind", "0.0.0.0:8000"]
