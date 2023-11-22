# docker build -t travelmap:v1 .
# docker run -p 5001:5001 <image>
FROM --platform=$BUILDPLATFORM python:3.11-alpine AS builder
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

RUN adduser -D worker
USER worker
WORKDIR /app

COPY --chown=worker:worker . .

ENTRYPOINT ["python3"]
CMD ["runApp.py"]