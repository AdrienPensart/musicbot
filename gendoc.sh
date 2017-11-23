#!/bin/bash

commands=COMMANDS.rst
>$commands
repeat (){
    seq  -f $1 -s '' $2; echo
}

echo -e "Commands\n--------" >> $commands
echo -e ".. code-block::\n" >> $commands
python3 musicbot --help >> $commands
echo -e "\n" >> $commands

for c in $(python3 musicbot --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
do
    command="musicbot $c"
    echo -e "$command" >> $commands
    perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
    echo -e ".. code-block::\n" >> $commands
    python3 musicbot $c --help 2>&1 | sed 's/^/  /' >> $commands
    echo -e "\n" >> $commands
    for s in $(python3 musicbot $c --help | awk '/Commands/{y=1;next}y' | awk '{print $1}');
    do
        command="musicbot $c $s"
        echo -e "$command" >> $commands
        perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
        echo -e ".. code-block::\n" >> $commands
        python3 musicbot $c $s --help 2>&1 | sed 's/^/  /' >> $commands
        echo -e "\n" >> $commands
    done
done

cat HELP.rst TODO.rst $commands > README.rst

rm $commands

