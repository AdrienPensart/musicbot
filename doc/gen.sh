#!/bin/bash

set -e

my_dir="$(dirname "$0")"
commands=$my_dir/COMMANDS.rst
>$commands
repeat (){
    seq  -f $1 -s '' $2; echo
}

echo -e "Commands\n--------" >> $commands
echo -e ".. code-block::\n" >> $commands
musicbot --help | sed -e 's/^/  /' >> $commands
echo -e "\n" >> $commands

for c in $(musicbot --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
do
    command="musicbot $c"
    echo "musicbot $c"
    echo -e "$command" >> $commands
    perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
    echo -e ".. code-block::\n" >> $commands
    musicbot $c --help | sed 's/^/  /' >> $commands
    echo -e "\n" >> $commands
    for s in $(musicbot $c --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
    do
        command="musicbot $c $s"
        echo "    musicbot $c $s"
        echo -e "$command" >> $commands
        perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
        echo -e ".. code-block::\n" >> $commands
        musicbot $c $s --help | sed 's/^/  /' >> $commands
        echo -e "\n" >> $commands
    done
done

cat $my_dir/help.rst $commands > $my_dir/../README.rst

rm $commands
