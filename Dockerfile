FROM python:3.11-slim

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app
CMD ["fastapi", "run", "main.py",--port", "80"]