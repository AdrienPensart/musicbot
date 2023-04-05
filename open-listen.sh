#!/bin/sh

edgedb configure set listen_addresses 127.0.0.1 ::1 $(wget http://ipinfo.io/ip -qO -)
