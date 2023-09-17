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
HASH=$(git rev-parse HEAD)
tarp 'curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'X-Rollbar-Access-Token: $HASH' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "production",
  "revision": "67a966bf87f1e6d35728e92c0580b88feb4234e3",
  "rollbar_username": "string",
  "local_username": "string",
  "comment": "deploy",
  "status": "string"
}
''
exec "$@"
