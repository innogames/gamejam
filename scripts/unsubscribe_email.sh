#!/usr/bin/env bash

EMAIL="$1"

mysql gamejam -e "update user
set notify_new_jam = 0, notify_jam_start = 0, notify_jam_finish = 0, notify_game_comment = 0, notify_team_invitation = 0, notify_newsletter=0
where email = '${EMAIL}';"
