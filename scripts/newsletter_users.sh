#!/usr/bin/env bash

JAM_ID="$1"
OUTFILE="$2"

mysql gamejam -e "SELECT email
FROM user u
WHERE u.notify_new_jam = 1 OR u.notify_newsletter = 1
INTO OUTFILE '${OUTFILE}'
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '\"'
LINES TERMINATED BY '\n';"
