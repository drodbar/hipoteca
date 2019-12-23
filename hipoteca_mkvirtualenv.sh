#! /usr/bin/env bash

VIRTENV="${1:-hipoteca}"
PYTHON3="${2:-$(which python3)}"

# warranty thar mkvirtualenv exists in your path
source `which virtualenvwrapper.sh`

mkvirtualenv --python=${PYTHON4} -r requirements.txt ${VIRTENV}
