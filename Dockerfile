# Offers service (FastAPI) - Alpine
FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Runtime deps
RUN apk add --no-cache build-base gcc musl-dev linux-headers libffi-dev mariadb-connector-c-dev

WORKDIR /app
COPY Offers/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY Offers/app /app/app
COPY Offers/.env /app/.env

EXPOSE 8001

# Use env OFFERS_PORT to set port
CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${OFFERS_PORT:-8001}"]
