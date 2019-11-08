#!/usr/bin/env bash

GAME_TITLE="$1"

mysql gamejam -e "SELECT  t.name, g.title,
    u.username,
    u.email
FROM
    team t,
    game g,
    user u,
    participation p
WHERE
    g.team_id = t.id
    AND g.jam_id = t.jam_id
    AND t.jam_id = p.jam_id AND t.id = p.team_id
    AND p.user_id = u.id
    AND g.title = '${GAME_TITLE}'
ORDER BY
    g.title ASC;"
