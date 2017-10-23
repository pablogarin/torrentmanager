#!/bin/bash
ID=false
ID_VALUE=
PROGRESS=false
PROGRESS_VALUE=
DATE=false
DATE_VALUE=
DATE_VALUE_C=0
function check {
    for line in $1; do
        if $ID; then
            ID_VALUE=$line
            ID=false
        fi
        if $PROGRESS; then
            PROGRESS_VALUE=$line
            PROGRESS=false
        fi
        if $DATE; then
            if [ $DATE_VALUE_C -lt 3 ]; then
                if [ -z "$DATE_VALUE" ]; then
                    DATE_VALUE=$line
                else
                    DATE_VALUE="$DATE_VALUE $line"
                fi
                let DATE_VALUE_C=DATE_VALUE_C+1
            else
                DATE_VALUE_C=0
                DATE=false
            fi
        fi
        if [ "$line" = "ID:" ]; then
            ID=true
        fi
        if [ "$line" = "Progress:" ]; then
            PROGRESS=true
        fi
        if [ "$line" = "Active:" ]; then
            DATE=true
        fi
        if [ "$PROGRESS_VALUE" = '100.00%' ]; then
            if [[ "$DATE_VALUE" =~ ([12] days) ]];then
                deluge-console del $ID_VALUE
                echo "$ID_VALUE"
                echo "$DATE_VALUE"
            fi
            DATE_VALUE=
            PROGRESS_VALUE=
            ID_VALUE=
        fi
    done
}

RES=$(deluge-console info -v -sQueued)
check "$RES"
RES=$(deluge-console info -v -sSeeding)
check "$RES"
