import click
import logging
from musicbot.lib import helpers, database, user

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.coro
@helpers.add_options(database.options)
async def cli(ctx, **kwargs):
    '''User management'''
    ctx.obj.db = await database.Database.make(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(database.options)
async def list(ctx, **kwargs):
    '''List users'''
    users = await ctx.obj.db.fetch('''select * from musicbot_public.user''')
    for u in users:
        print(u)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(database.options + user.options)
async def new(ctx, email, password, first_name, last_name, **kwargs):
    '''Register a new user'''
    user = await ctx.obj.db.register_user(email=email, password=password, first_name=first_name, last_name=last_name)
    print(user)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(database.options + user.email_argument)
async def remove(ctx, email, **kwargs):
    deleted = await ctx.obj.db.remove_user(email=email)
    print('User deleted?', deleted)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(database.options + user.email_argument + user.password_argument)
async def login(ctx, email, password, **kwargs):
    '''Authenticate user'''
    auth = await ctx.obj.db.authenticate_user(email=email, password=password)
    print(auth)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(database.options + user.email_argument + user.password_argument + user.secret_argument)
async def token(ctx, email, password, secret, **kwargs):
    '''Emit a new token'''
    token = await ctx.obj.db.new_token(email=email, password=password, secret=secret)
    print(token)
