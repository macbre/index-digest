# https://hub.docker.com/_/python/
FROM python:3.9-alpine

WORKDIR /opt/macbre/index-digest

# install dependencies
ADD setup.py ./
ADD indexdigest/__init__.py ./indexdigest/__init__.py

# installs mysql_config and pip dependencies
# https://github.com/gliderlabs/docker-alpine/issues/181
RUN apk upgrade \
    && apk add --virtual build-deps gcc musl-dev \
    && apk add mariadb-dev \
    && pip install indexdigest \
    && rm -rf ~/.cache/pip \
    && apk del build-deps

ARG COMMIT="dev"
ENV COMMIT_SHA=${COMMIT}

# label the image with branch name and commit hash
LABEL maintainer="maciej.brencz@gmail.com"
LABEL org.opencontainers.image.source="https://github.com/macbre/index-digest"
LABEL org.opencontainers.image.revision=${COMMIT}

# install the remaining files
ADD . .

USER nobody

# docker run -t macbre/index-digest
ENTRYPOINT ["index_digest"]
