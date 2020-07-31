#!/usr/bin/env python3
from textwrap import indent
import click
from musicbot.helpers import GroupWithHelp
from musicbot.cli import cli, CONTEXT_SETTINGS, prog_name


def gen_doc(main_cli):
    click.echo("Commands\n--------")
    click.echo(".. code-block::\n")
    with click.Context(main_cli, info_name=prog_name, **CONTEXT_SETTINGS) as base_ctx:
        cli_help = main_cli.get_help(base_ctx)
        cli_help = indent(cli_help, '  ')
        click.echo(cli_help)
        for command_name, command in sorted(cli.commands.items()):
            if command.hidden:
                continue

            command_title = f"{prog_name} {command_name}"
            click.echo('\n')
            click.echo(command_title)
            click.echo('*' * len(command_title))
            click.echo(".. code-block::\n")

            with click.Context(command, info_name=command_name, parent=base_ctx) as command_ctx:
                command_help = command.get_help(command_ctx)
                command_help = indent(command_help, '  ')
                click.echo(command_help)

            if not isinstance(command, GroupWithHelp):
                continue

            for subcommand_name, subcommand in sorted(command.commands.items()):
                if subcommand_name == 'help' or subcommand.hidden:
                    continue

                subcommand_title = f"{prog_name} {command_name} {subcommand_name}"
                click.echo('\n')
                click.echo(subcommand_title)
                click.echo('*' * len(subcommand_title))
                click.echo(".. code-block::\n")
                with click.Context(subcommand, info_name=subcommand_name, parent=command_ctx) as subcommand_ctx:
                    subcommand_help = subcommand.get_help(subcommand_ctx)
                    subcommand_help = indent(subcommand_help, '  ')
                    click.echo(subcommand_help)


if __name__ == '__main__':
    with open("doc/help.rst", "r") as main_doc:
        print(main_doc.read())
    gen_doc(cli)
