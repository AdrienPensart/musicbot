import click
from . import helpers
from .graphql import GraphQL
from .helpers import config_string


DEFAULT_GRAPHQL_ADMIN = 'http://127.0.0.1:5001/graphql'
graphql_admin_option = [click.option('--graphql-admin', help='GraphQL endpoint', default=DEFAULT_GRAPHQL_ADMIN, callback=config_string, show_default=True)]


class Admin(GraphQL):
    @helpers.timeit
    def __init__(self, graphql=None):
        graphql = graphql if graphql is not None else DEFAULT_GRAPHQL_ADMIN
        GraphQL.__init__(self, graphql=graphql)

    @helpers.timeit
    def users(self):
        query = """{
            accountsList {
                user {
                  lastName
                  createdAt
                  updatedAt
                  firstName
                }
                email
            }
        }"""
        return self._post(query)['data']['accountsList']
