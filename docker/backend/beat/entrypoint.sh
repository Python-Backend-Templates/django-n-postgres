#!/bin/bash

# if any of the commands fails for any reason, the entire script fails
set -o errexit

# fail exit if one of pipe command fails
set -o pipefail

# exits if any of variables is not set
set -o nounset

mkdir -p /var/run/celery /var/log/celery
touch /tmp/celerybeat-schedule

chown -R nobody:nogroup /var/run/celery \
                        /var/log/celery \
                        /logs \
                        /tmp/celerybeat-schedule

python -m celery -A config beat \
                    -l info \
                    --uid=nobody \
                    --gid=nogroup \
                    --schedule=/tmp/celerybeat-schedule
