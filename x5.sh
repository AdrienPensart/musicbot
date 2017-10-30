#!/bin/sh

user="admin"
src="/home/$user/music"
dst="/home/$user/x5"
alias musicbot="env/bin/python musicbot"

musicbot $@ folder scan "$src"
musicbot $@ db clean
musicbot $@ folder sync --min-rating 4.0 --no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro "$dst"
musicbot $@ playlist bests --relative --min-rating 4.0 --no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro "$dst"

#for k in `musicbot tags show --fields keywords --artists Buckethead --keywords pike --filter $filter --output list | sort | uniq | grep -v pike`; do
#    musicbot playlist --path "$dst/Buckethead/Pikes/$k.m3u" --artists Buckethead --keywords pike,$k --filter $filter $@
#    sed -i "s|^$src/Buckethead/Pikes/||" "$dst/Buckethead/Pikes/$k.m3u"
#done
