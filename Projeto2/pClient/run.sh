#!/bin/bash

challenge="4"
host="127.0.0.1"
robname="mainC4"
pos="0"
outfile="challenge4"

while getopts "c:h:r:p:f:" op
do
    case $op in
        "c")
            challenge=$OPTARG
            ;;
        "h")
            host=$OPTARG
            ;;
        "r")
            robname=$OPTARG
            ;;
        "p")
            pos=$OPTARG
            ;;
        "f")
            outfile=$OPTARG
            ;;
        default)
            echo "ERROR in parameters"
            ;;
    esac
done

shift $(($OPTIND-1))

case $challenge in
    4)
        # how to call agent for challenge 3
        python mainC4_v2.py -h "$host" -p "$pos" -r "$robname" -f "$outfile" # assuming -f is the option for the path
        ;;
esac

