#!/usr/bin/env bash

JAM_ID="$1"
OUTFILE="$2"

mysql gamejam -e "select u.email
from participation p left join user u on u.id = p.user_id
where p.jam_id = ${JAM_ID} and p.user_id in (select user_id from participation where jam_id = ${JAM_ID} and team_id in (select team_id from game where jam_id = ${JAM_ID}))
INTO OUTFILE '${OUTFILE}'
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '\"'
LINES TERMINATED BY '\n';"
