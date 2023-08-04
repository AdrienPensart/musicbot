#!/bin/sh

quit=0
for cmd in $(ls -1 musicbot/commands | grep -vE "(__init__|__pycache__|test)"); do # W: Don't use ls | grep. Use a glob or a for loop with a condition to allow non-alphanumeric filenames.
    cmds=$(grep -c cli.command musicbot/commands/$cmd) # I: Double quote to prevent globbing and word splitting.
    tests=$(grep -c '^def test_' tests/test_$cmd); # I: Double quote to prevent globbing and word splitting.
    if [ "$cmds" != "$tests" ]; then
        echo "Bad number of tests: $cmd = $cmds | $tests"
        quit=1
    fi
done

if [ "$quit" = "1" ]; then
    exit 1
fi

exit 0
