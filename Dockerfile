# Use the official Python image as the base image
FROM python:3.9-slim

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python packages from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Download the NLTK punkt resource
RUN python -c "import nltk; nltk.download('punkt')"
