#!/bin/sh

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
user="admin"
src="/home/$user/music"
dst="/home/$user/x5"
prefix="/mnt/external_sd1/"
filter="default.filter"

python3 $musicbot $@ folder scan "$src"
python3 $musicbot $@ db clean
python3 $musicbot $@ folder sync --filter $my_dir/x5.filter "$dst"
python3 $musicbot $@ playlist bests --suffix '_4'   --relative --min-rating 4.0 --filter $my_dir/$filter --prefix $prefix "$dst"
python3 $musicbot $@ playlist bests --suffix '_4.5' --relative --min-rating 4.5 --filter $my_dir/$filter --prefix $prefix "$dst"
python3 $musicbot $@ playlist bests --suffix '_5'   --relative --min-rating 5.0 --filter $my_dir/$filter --prefix $prefix "$dst"

for k in `python3 $musicbot tag show --fields keywords --artists Buckethead --keywords pike --min-rating 4.5 | grep -o '[a-z]\+' | sort | uniq | grep -v pike`; do
    python3 $musicbot playlist new --artists Buckethead --keywords pike --keywords $k --min-rating 4.5 "$dst/Buckethead/Pikes/$k.m3u"
    sed -i "s|^$src/Buckethead/Pikes/||" "$dst/Buckethead/Pikes/$k.m3u"
done
