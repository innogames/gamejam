#!/usr/bin/env bash

JAM_ID="$1"
OUTFILE="$2"

mysql gamejam -e "SELECT email, real_name, username FROM user u
LEFT JOIN participation p
ON u.id = p.user_id
WHERE p.jam_id = ${JAM_ID}
INTO OUTFILE '${OUTFILE}'
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '\"'
LINES TERMINATED BY '\n';"
