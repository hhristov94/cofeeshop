FROM python:3.11-slim-bullseye
RUN mkdir /cofeeshop
COPY /. /cofeeshop
COPY pyproject.toml /cofeeshop
WORKDIR /cofeeshop
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
EXPOSE 8000