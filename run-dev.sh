#!/bin/bash

mkdir /etc/flamejam
cp /usr/src/myapp/doc/flamejam.cfg.docker /etc/flamejam/flamejam.cfg

make -C /usr/src/myapp setup
make -C /usr/src/myapp init-db user=admin pass=admin email=marco.behnke@innogames.com
make -C /usr/src/myapp seed-db
make -C /usr/src/myapp run-dev
