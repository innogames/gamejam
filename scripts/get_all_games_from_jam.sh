#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "SELECT t.name
FROM team t
WHERE t.jam_id = ${JAM_ID} and t.id in (select g.team_id from game g where g.jam_id = ${JAM_ID});"
