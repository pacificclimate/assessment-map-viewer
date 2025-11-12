# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12-slim

# Set up working directory
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the web service on container startup.
CMD ["python", "index.py"]