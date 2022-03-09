FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV LOG_DIR /var/log/facial-auth-api/

# Set environment for the application
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install production dependencies.
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY . ./

ENV PORT 80
EXPOSE $PORT

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --pythonpath ./src/ api:socketio_app --worker-class uvicorn.workers.UvicornWorker