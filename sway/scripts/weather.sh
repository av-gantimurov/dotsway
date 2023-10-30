#!/usr/bin/env sh

set -x
# toggles the help wrapper state

VISIBILITY_SIGNAL=40
QUIT_SIGNAL=41

if [ "$1" = "--toggle" ]; then
    pkill -f -${VISIBILITY_SIGNAL} nwg-wrapper
else
    pkill -f -${QUIT_SIGNAL} nwg-wrapper
    for output in $(swaymsg -t get_outputs --raw | jq -r '.[].name'); do
        nwg-wrapper -o "$output" -sv ${VISIBILITY_SIGNAL} -sq ${QUIT_SIGNAL} -s date-wttr.sh -r 1800000 -c date-wttr.css -p right -mr 20 -a start -j right &
    done
fi
