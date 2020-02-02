#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "SELECT t.name, g.title
FROM team t, game g
WHERE t.id = g.team_id AND t.jam_id = ${JAM_ID};"
