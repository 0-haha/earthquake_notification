FROM python:3.8-alpine

RUN apk add --no-cache libnotify dbus gcc musl-dev

COPY . ./app
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt
