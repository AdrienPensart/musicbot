#!/bin/bash

set -e

my_dir="$(dirname "$0")"
export MB_DB=${MB_DB:-'postgresql://postgres:musicbot@localhost:5432/musicbot_test'}
export MB_EMAIL=${MB_EMAIL:-'test_test@test.com'}
export MB_PASSWORD=${MB_PASSWORD:-'test_test'}

export MB_GRAPHQL=${MB_GRAPHQL:-'http://127.0.0.1:15000/graphql'}
export MB_GRAPHQL_ADMIN=${MB_GRAPHQL_ADMIN:-'http://127.0.0.1:15001/graphql'}

musicbot db drop --yes
musicbot db create
musicbot db clear --yes

function pidofport {
    netstat -ltnp 2>/dev/null| grep -w "$1" | awk '{print $7}' | cut -f1 -d"/"
}

musicbot postgraphile public test_secret --graphql-public-port 15000 &
function finish_public {
    kill $(pidofport 15000)
}
trap finish_public EXIT

musicbot postgraphile private --graphql-private-port 15001 &
function finish_public_private {
	finish_public
    kill $(pidofport 15001)
}
trap finish_public_private EXIT

sleep 2

musicbot user register
token=$(musicbot user login)
musicbot user login --token $token
musicbot user list

musicbot folder scan $my_dir/fixtures/*
musicbot folder find $my_dir/fixtures/*
musicbot folder scan
# musicbot db clean
# musicbot youtube musics
# musicbot youtube albums
musicbot folder sync tests2
rm -rf tests2

musicbot folder watch &
sleep 1
touch "$(find $my_dir/fixtures -type f | head -n1)"
sleep 1
kill %%

musicbot stats show
# musicbot tag show
musicbot playlist new
musicbot playlist bests $my_dir/fixtures
rm -f $my_dir/fixtures/*.m3u
