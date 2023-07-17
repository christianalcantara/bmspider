# define an alias for the specific python version used in this file.
FROM python:3.11.4-slim-bullseye as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=base
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./script/start-scrapyd.sh /start-scrapyd.sh
RUN sed -i 's/\r$//g' /start-scrapyd.sh
RUN chmod +x /start-scrapyd.sh

COPY ./script/start-webserver.sh /start-webserver.sh
RUN sed -i 's/\r$//g' /start-webserver.sh
RUN chmod +x /start-webserver.sh



# copy application code to WORKDIR
COPY . ${APP_HOME}

RUN python bmspider/models.py
