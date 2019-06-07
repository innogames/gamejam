#!/bin/bash

SETUP_DONE=/root/setup-done

echo 'Waiting for database on port 3306'
while ! nc -q 1 db 3306 </dev/null; do
    printf '*'
    sleep 2
done

echo "Database is up and running"

if [ ! -f ${SETUP_DONE} ];
then
    echo "First run, setup system"
    mkdir /etc/flamejam
    cp /usr/src/myapp/doc/flamejam.cfg.docker /etc/flamejam/flamejam.cfg

    make -C /usr/src/myapp setup
    make -C /usr/src/myapp init-db user=admin pass=admin email=marco.behnke@innogames.com
    make -C /usr/src/myapp seed-db

    touch ${SETUP_DONE}
fi

echo "Starting service"
make -C /usr/src/myapp run-dev
