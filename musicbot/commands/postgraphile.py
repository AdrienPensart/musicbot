import click
import os
import logging
from musicbot.lib import postgraphile, helpers, database
from musicbot.lib.config import config

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.coro
@click.pass_context
@helpers.add_options(database.options)
async def cli(ctx, **kwargs):
    '''Postgraphile management'''
    ctx.obj.db = await database.Database.make(**kwargs)


@cli.command()
@helpers.add_options(postgraphile.secret_argument)
@click.pass_context
def public(ctx, secret):
    '''Start public backend'''
    base_cmd_fmt = """npx postgraphile --no-setof-functions-contain-nulls --no-ignore-rbac --no-ignore-indexes --dynamic-json -c {} -n 0.0.0.0 -p 5000 --schema musicbot_public --default-role musicbot_anonymous --jwt-token-identifier musicbot_public.jwt_token --jwt-secret {} -l 10MB --append-plugins postgraphile-plugin-connection-filter --simple-collections both"""
    base_cmd = base_cmd_fmt.format(ctx.obj.db.connection_string, secret)

    if config.debug:
        cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --enhance-graphiql --show-error-stack --watch""".format(base_cmd)
    else:
        cmd = """{} --disable-graphiql --disable-query-log """.format(base_cmd)
    os.system(cmd)


@cli.command()
@click.pass_context
def private(ctx):
    '''Start private backend'''
    base_cmd = """npx postgraphile --include-extension-resources --no-setof-functions-contain-nulls --no-ignore-indexes --dynamic-json -c {} -n localhost -p 5001 --schema musicbot_public,musicbot_private --default-role postgres --append-plugins postgraphile-plugin-connection-filter --enhance-graphiql --simple-collections both""".format(ctx.obj.db.connection_string)

    if config.debug:
        cmd = """DEBUG="postgraphile:graphql,graphile-build-pg,postgraphile:postgres:notice,postgraphile:postgres:error" {} --show-error-stack --watch""".format(base_cmd)
    else:
        cmd = """{} --disable-graphiql --disable-query-log""".format(base_cmd)
    os.system(cmd)
