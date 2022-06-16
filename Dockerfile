FROM nginx/unit:1.27.0-python3.10

RUN set -ex \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y \
    libpq-dev build-essential jq

WORKDIR /app

RUN python -m pip install django psycopg2

COPY proj /app

RUN python -m generate_routes | jq "." > /app/routes.json

RUN jq -s '.[0] * .[1]' /app/config.json /app/routes.json > /app/all.json

RUN cp /app/all.json /docker-entrypoint.d/config.json