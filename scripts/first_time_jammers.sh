#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "SELECT u.email
FROM participation p left join user u on u.id = p.user_id
WHERE p.jam_id = ${JAM_ID} and p.user_id in (select user_id from participation where jam_id = ${JAM_ID} and team_id in (select team_id from game where jam_id = ${JAM_ID}))
GROUP by p.user_id limit 1;"
