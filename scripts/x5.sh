#!/bin/sh

set -e

user="admin"
src="/home/$user/music"
dst="/home/$user/x5"
prefix="/mnt/external_sd1/"
filter="--no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro"

export MB_DB=musicbot_prod
musicbot $@ folder sync $filter --min-rating 4.0 "$dst"
musicbot $@ playlist bests --prefix $prefix --suffix '_4'   --relative --min-rating 4.0 $filter "$dst"
musicbot $@ playlist bests --prefix $prefix --suffix '_4.5' --relative --min-rating 4.5 $filter "$dst"
musicbot $@ playlist bests --prefix $prefix --suffix '_5'   --relative --min-rating 5.0 $filter "$dst"

for k in $(musicbot tag --artists Buckethead --keywords pike --min-rating 4.5 show --fields keywords | grep -o '[a-z]\+' | sort | uniq | grep -v pike); do
    musicbot playlist new $filter --artists Buckethead --keywords pike --keywords $k --min-rating 4.5 "$dst/Buckethead/Pikes/$k.m3u"
    sed -i "s|^$src/Buckethead/Pikes/||" "$dst/Buckethead/Pikes/$k.m3u"
done
