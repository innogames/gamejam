#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "SELECT count(*) FROM user u LEFT JOIN participation p ON u.id = p.user_id WHERE p.jam_id = ${JAM_ID};"
