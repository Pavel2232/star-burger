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
exec "$@"
