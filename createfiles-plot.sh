#!/bin/sh
#
# A small script to generate graphs from createfiles.py output. There will
# be one createfiles-$SIZE.png file for each size of output, graphing the
# various algorithms at various sizes.

set -e

input="$1"

algos=$(awk '$2 == "files/s" { print $3 }' "$input" | sort -u)
sizes=$(awk '/^Measuring/ { print $(NF-1) }' "$input" | sort -un)

for size in $sizes
do
    plot=""
    
    for x in $algos
    do
        awk -vx=$x -vsize=$size '
            /^Measuring/ {
                if ($(NF-1) == size) {
                    n = $6
                    ok = 1
                } else {
                    ok = 0
                }
            }
            ok && $3 == x { 
                print n, $1 >> x ".dat" 
            }' "$input"
        if [ "$plot" = "" ]
        then
            plot="plot \"$x.dat\" with lines"
        else
            plot="$plot, \"$x.dat\" with lines"
        fi
    done

    gnuplot <<eof > "createfiles-$size.png"
set terminal png
set title "Size $size"
$plot
eof

    for x in $algos
    do
        rm "$x.dat"
    done

done
