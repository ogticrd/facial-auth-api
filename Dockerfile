FROM python:3.9-slim

ENV PORT=80
ENV HOST="0.0.0.0"
ENV REDIS_HOST='redis'
ENV REDIS_PORT=6379

WORKDIR /code

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

COPY ./requirements.txt /code/requirements.txt
COPY ./static /code/static

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

EXPOSE 80

CMD ["python", "src/api.py"]