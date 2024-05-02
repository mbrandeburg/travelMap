# docker build -t travelmap:v1 .
# docker run -p 5001:5001 <image>
FROM --platform=$BUILDPLATFORM python:3.11-alpine AS build
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

# Will be mounted in for persistence as a PV
VOLUME /mnt
COPY *Tracker* /mnt

RUN adduser -D worker
RUN chown -R worker:worker /mnt/

USER worker
WORKDIR /app

COPY --chown=worker:worker . .

ENTRYPOINT ["python3"]
CMD ["runApp.py"]