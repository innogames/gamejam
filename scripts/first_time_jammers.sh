#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "SELECT u.email FROM user u LEFT JOIN participation p ON u.id = p.user_id WHERE p.jam_id = ${JAM_ID}
    AND u.id NOT IN (SELECT u.id FROM user u LEFT JOIN participation p ON u.id = p.user_id WHERE p.jam_id != ${JAM_ID})"
