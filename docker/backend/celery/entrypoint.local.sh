#!/bin/bash

# if any of the commands fails for any reason, the entire script fails
set -o errexit

# fail exit if one of pipe command fails
set -o pipefail

# exits if any of variables is not set
set -o nounset

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery \
                        /var/log/celery \
                        /logs

cd /apps/ && python -m celery -A config worker \
                                -l debug \
                                --uid=nobody \
                                --gid=nogroup \
                                --concurrency=1
