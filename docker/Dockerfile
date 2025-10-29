# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12-slim

# Copy local code to the container image.
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY . .

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
CMD ["panel", "serve", "Map_and_Tables_App.py", "--address", "0.0.0.0", "--port", "8080", "--allow-websocket-origin=*"]