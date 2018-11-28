import click
import logging
import requests
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
async def list(ctx):
    '''List users (admin)'''
    users = await ctx.obj.db.fetch('''select * from musicbot_public.user u inner join musicbot_private.account a on u.id=a.user_id''')
    for u in users:
        print(u)


@cli.command()
@click.pass_context
@helpers.add_options(user.options)
def new(ctx, graphql, **kwargs):
    '''Register a new user'''
    # user = await ctx.obj.db.register_user(email=email, password=password, first_name=first_name, last_name=last_name)
    # print(user)
    query = """
    mutation
    {{
      registerUser(input: {{firstName: "{first_name}", lastName: "{last_name}", email: "{email}", password: "{password}"}})
      {{
        user
        {{
          id,
          firstName,
          lastName,
          createdAt,
          updatedAt
        }}
      }}
    }}""".format(**kwargs)
    if kwargs['email'] == user.DEFAULT_EMAIL:
        print('Default email: {}'.format(user.DEFAULT_EMAIL))
    if kwargs['password'] == user.DEFAULT_PASSWORD:
        print('Default password: {}'.format(user.DEFAULT_PASSWORD))
    request = requests.post(graphql, json={'query': query})
    if request.status_code != 200:
        print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
        return
    print(request.json())


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(user.token_argument + user.graphql_option)
async def remove(ctx, graphql, token):
    '''Remove a user'''
    # deleted = await ctx.obj.db.remove_user(email=email)
    # print('User deleted?', deleted)
    headers = {"Authorization": "Bearer {}".format(token)}
    query = """
    mutation
    {
        removeUser(input: {})
        {
            clientMutationId
        }
    }"""
    request = requests.post(graphql, json={'query': query}, headers=headers)
    if request.status_code != 200:
        print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
        return
    # query = """
    # {
    #     currentMusicbot
    #     {
    #         id
    #     }
    # }"""
    # request = requests.post(graphql, json={'query': query}, headers=headers)
    # if request.status_code != 200:
    #     print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    #     return

    # if request.json()['data']['currentMusicbot'] is None:
    #     print("User does not exist anymore")
    #     return
    # user_id = request.json()['data']['currentMusicbot']['id']
    # query = """
    # mutation {{
    #    deleteUserById(input: {{id: {user_id}}})
    #    {{
    #        clientMutationId
    #    }}
    # }}""".format(user_id=user_id)
    # request = requests.post(graphql, json={'query': query}, headers=headers)
    # if request.status_code != 200:
    #     print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    #     return
    # print(request.json())


@cli.command()
@click.pass_context
@helpers.add_options(user.email_argument + user.password_argument + user.graphql_option)
def login(ctx, graphql, **kwargs):
    '''Authenticate user'''
    query = """
    mutation
    {{
        authenticate(input: {{email: "{email}", password: "{password}"}})
        {{
            jwtToken
        }}
    }}""".format(**kwargs)
    request = requests.post(graphql, json={'query': query})
    if request.status_code != 200:
        print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
        return
    print(request.json())
