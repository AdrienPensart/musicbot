#!/bin/bash

set -e

my_dir="$(dirname "$0")"
musicbot=$my_dir/../musicbot
commands=$my_dir/COMMANDS.rst
>$commands
repeat (){
    seq  -f $1 -s '' $2; echo
}

echo -e "Commands\n--------" >> $commands
echo -e ".. code-block::\n" >> $commands
python3 $musicbot --help | sed -e 's/^/  /' >> $commands
echo -e "\n" >> $commands

for c in $(python3 $musicbot --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
do
    command="musicbot $c"
    echo "Generating doc for: musicbot $c"
    echo -e "$command" >> $commands
    perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
    echo -e ".. code-block::\n" >> $commands
    python3 $musicbot $c --help 2>&1 | sed 's/^/  /' >> $commands
    echo -e "\n" >> $commands
    for s in $(python3 $musicbot $c --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
    do
        command="musicbot $c $s"
        echo -e "$command" >> $commands
        perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
        echo -e ".. code-block::\n" >> $commands
        python3 $musicbot $c $s --help 2>&1 | sed 's/^/  /' >> $commands
        echo -e "\n" >> $commands
    done
done

cat $my_dir/help.rst $commands > $my_dir/../README.rst

rm $commands
