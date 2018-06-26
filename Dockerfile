# https://hub.docker.com/_/python/
FROM python:3.6-slim

WORKDIR /opt/macbre/index-digest

# install dependencies
ADD setup.py ./
ADD indexdigest/__init__.py ./indexdigest/__init__.py

# installs mysql_config and pip dependencies
# https://github.com/gliderlabs/docker-alpine/issues/181
RUN apt-get update && apt-get install -y libmariadbclient-dev gcc \
    && pip install indexdigest \
    && rm -rf ~/.cache/pip \
    && apt-get remove -y gcc && apt-get autoremove -y

# install the remaining files
ADD . .

USER nobody

# docker run -t macbre/index-digest
ENTRYPOINT ["index_digest"]
