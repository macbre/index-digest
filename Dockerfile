# https://hub.docker.com/_/python/
FROM python:3.9-alpine

WORKDIR /opt/macbre/index-digest

# copy files required to run "pip install"
ADD setup.py README.md ./
ADD ./indexdigest/__init__.py ./indexdigest/__init__.py

# installs mysql_config and pip dependencies
# https://github.com/gliderlabs/docker-alpine/issues/181
RUN apk upgrade \
    && apk add --virtual build-deps gcc musl-dev \
    && apk add mariadb-dev \
    && pip install . \
    && rm -rf ~/.cache/pip /root/.cache/ \
    && apk del build-deps

ARG COMMIT_SHA="dev"
ENV COMMIT_SHA ${COMMIT_SHA}

# label the image with branch name and commit hash
LABEL maintainer="maciej.brencz@gmail.com"
LABEL org.opencontainers.image.source="https://github.com/macbre/index-digest"
LABEL org.opencontainers.image.revision="${COMMIT_SHA}"

# install the remaining files
ADD . .

# install the entire package
ENV HOME /opt/macbre/index-digest
RUN chown -R nobody .
USER nobody
RUN pip install --user .

RUN index_digest --version

# docker run -t macbre/index-digest
ENTRYPOINT ["index_digest"]
