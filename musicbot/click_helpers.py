import os
import logging
import traceback
import itertools
from textwrap import indent
import click
import click_completion
from click_help_colors import HelpColorsGroup
from click_didyoumean import DYMGroup
from click_aliases import ClickAliasedGroup

logger = logging.getLogger(__name__)

class ExpandedPath(click.Path):
    def convert(self, value, *args, **kwargs):
        value = os.path.expanduser(value)
        return super().convert(value, *args, **kwargs)


class AdvancedGroup(DYMGroup, ClickAliasedGroup, HelpColorsGroup):
    def __init__(self, *args, **kwargs):
        kwargs['help_headers_color'] = 'yellow'
        kwargs['help_options_color'] = 'green'
        super().__init__(*args, **kwargs)

        @click.command('help')
        @click.argument('command', required=False)
        @click.pass_context
        def _help(ctx, command):
            '''Print help'''
            if command:
                argument = command[0]
                c = self.get_command(ctx, argument)
                print(c.get_help(ctx))
            else:
                print(ctx.parent.get_help())
        self.add_command(_help)


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def run_cli(cli_runner, called_cli, *args):
    result = cli_runner.invoke(called_cli, *args)
    logger.debug(result.output)
    if result.exception:
        traceback.print_exception(*result.exc_info)
    if result.exit_code != 0:
        elems = ' '.join(itertools.chain.from_iterable(args))
        logger.critical(f'Failed : {cli_runner.get_default_prog_name()} {elems}')
    assert result.exit_code == 0
    return result.output.rstrip()


def gen_doc(main_cli, prog_name, CONTEXT_SETTINGS):
    click.echo("Commands\n--------")
    click.echo(".. code-block::\n")
    with click.Context(main_cli, info_name=prog_name, **CONTEXT_SETTINGS) as base_ctx:
        cli_help = main_cli.get_help(base_ctx)
        cli_help = indent(cli_help, '  ')
        click.echo(cli_help)
        for command_name, command in sorted(main_cli.commands.items()):
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

            if not isinstance(command, AdvancedGroup):
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


completion_options = [
    click.option('-i', '--case-insensitive/--no-case-insensitive', help="Case insensitive completion"),
    click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.core.shells)),
]

@click.group(help="Shell completion", cls=AdvancedGroup)
def completion():
    pass


@completion.command(help='Show the click-completion-command completion code')
@add_options(completion_options)
def show(shell, case_insensitive):
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    click.echo(click_completion.core.get_code(shell, extra_env=extra_env))


@completion.command(help='Install the click-completion-command completion')
@click.option('--append/--overwrite', help="Append the completion code to the file", default=None)
@add_options(completion_options)
@click.argument('path', required=False)
def install(append, case_insensitive, shell, path):
    extra_env = {'_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON'} if case_insensitive else {}
    shell, path = click_completion.core.install(shell=shell, path=path, append=append, extra_env=extra_env)
    click.echo(f'{shell} completion installed in {path}')


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get('_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


click_completion.core.startswith = custom_startswith
click_completion.init()
