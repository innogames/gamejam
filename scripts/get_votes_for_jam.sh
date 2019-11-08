#!/usr/bin/env bash

JAM_ID="$1"

mysql gamejam -e "select count(*),g.title
from vote v left join game g on g.id = v.game_id
where v.jam_id = ${JAM_id}
group by v.game_id
order by 1 desc;"
