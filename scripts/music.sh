#!/bin/sh

dst="/home/admin/music"

alias musicbot="env/bin/python musicbot"
musicbot folder scan "$dst"
musicbot db clean
find "$dst" -name \*.m3u -delete
musicbot $@ playlist bests --suffix '_4' --min-rating 4.0 --no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro "$dst"
musicbot $@ playlist bests --suffix '_4.5' --min-rating 4.5 --no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro "$dst"
musicbot $@ playlist bests --min-rating 5.0 --no-keywords cutoff --no-keywords bad --no-keywords demo --no-keywords intro "$dst"

#for k in `musicbot tags show --fields keywords --artists Buckethead --keywords pike --filter $filter --output list | sort | uniq | grep -v pike`; do
#    musicbot playlist --path "$dst/Buckethead/Pikes/$k.m3u" --filter $filter --artists Buckethead --keywords pike,$k $@
#done
