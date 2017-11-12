#!/bin/bash

find -name \*.py | entr python musicbot $@
