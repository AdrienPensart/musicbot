#!/bin/sh

edgedb configure set listen_addresses "127.0.0.1" "::1" "$(wget http://ipinfo.io/ip -qO -)" "2607:5300:205:300::69c"
