#!/bin/bash

set -e

my_dir="$(dirname "$0")"
commands=$(mktemp $my_dir/commands_$$.XXXXXX)
trap "rm -rf $my_dir/commands_*" EXIT
repeat (){
    seq  -f $1 -s '' $2; echo
}

cmd="musicbot"
echo -e "Commands\n--------" >> $commands
echo -e ".. code-block::\n" >> $commands
$cmd --help | sed -e 's/^/  /' >> $commands
echo -e "\n" >> $commands

IFS=$'\n'
command_list=$($cmd --help | awk '/Commands/{y=1;next}y')
for c in $command_list;
do
    command_name=$(echo "$c" | awk '{print $1}')
    command_help=$(echo "$c" | awk '{print $2}')
    if [ -z "$command_help" ]; then
        echo "Command \"$cmd $command_name\" does not have help string, please add one"
        exit -1
    fi

    command="$cmd $command_name"
    echo "$cmd $command_name"
    echo -e "$command" >> $commands
    perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
    echo -e ".. code-block::\n" >> $commands
    $cmd $command_name --help | sed 's/^/  /' >> $commands
    echo -e "\n" >> $commands
    subcommand_list=$($cmd $command_name --help | awk '/Commands/{y=1;next}y')
    for s in $subcommand_list;
    do
        subcommand_name=$(echo "$s" | awk '{print $1}')
        subcommand_help=$(echo "$s" | awk '{print $2}')
        if [ -z "$subcommand_help" ]; then
            echo "Command \"$cmd $command_name $subcommand_name\" does not have help string, please add one"
            exit -1
        fi

        command="$cmd $command_name $subcommand_name"
        echo "    $cmd $command_name $subcommand_name"
        echo -e "$command" >> $commands
        perl -e "print '*' x ${#command}; print \"\n\";" >> $commands
        echo -e ".. code-block::\n" >> $commands
        $cmd $command_name $subcommand_name --help | sed 's/^/  /' >> $commands
        echo -e "\n" >> $commands
    done
done

cat $my_dir/help.rst $commands > $my_dir/../README.rst
