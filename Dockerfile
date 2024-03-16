# Use the latest official Python image as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install netcat, used for waiting for the database
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Add a startup script that waits for the db to be ready, initializes it, and starts the app
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Use the startup script as the entry point
ENTRYPOINT ["./entrypoint.sh"]