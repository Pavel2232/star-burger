#!/bin/bash

cd /app/star-burger/
trap 'git pull https://github.com/Pavel2232/star-burger' ERR
echo 'Already up to date.'
trap 'poetry shell' ERR
trap 'poetry install' ERR
echo 'Зависимости установленны'
trap 'python3 manage.py collectstatic --noinput' ERR
trap 'python3 manage.py migrate --noinput' ERR
echo 'миграции накатили, статику собрали'
trap 'npm ci --dev' ERR
trap './node_modules/.bin/parcel bundles-src/index.js --dist-dir bundles --public-url="./"' ERR
echo 'Node.js run'
trap 'systemctl daemon-reload' ERR
source .env
HASH=$(git rev-parse HEAD)
curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_TOKEN \
  -F environment="deployment" \
  -F revision=$HASH \
  -F local_username=$USER \
  -F comment="Deployed new version" \
  -F status=succeeded
exec "$@"
