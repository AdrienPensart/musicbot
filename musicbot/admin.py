from typing import Any
import requests
from click_option_group import optgroup  # type: ignore
from .config import config
from .graphql import GraphQL
from .helpers import config_string


DEFAULT_GRAPHQL_ADMIN = 'http://127.0.0.1:5001/graphql'
graphql_admin_option = [
    optgroup.option(
        '--graphql-admin',
        help='GraphQL endpoint',
        default=DEFAULT_GRAPHQL_ADMIN,
        callback=config_string,
        show_default=True
    )
]


DEFAULT_GRAPHQL_ADMIN_USER = None
graphql_admin_user_option = [
    optgroup.option(
        '--graphql-admin-user',
        help='GraphQL admin user (basic auth)',
        default=DEFAULT_GRAPHQL_ADMIN_USER,
        callback=config_string,
    )
]


DEFAULT_GRAPHQL_ADMIN_PASSWORD = None
graphql_admin_password_option = [
    optgroup.option(
        '--graphql-admin-password',
        help='GraphQL admin password (basic auth)',
        default=DEFAULT_GRAPHQL_ADMIN_PASSWORD,
        callback=config_string,
    )
]

admin_options =\
    [optgroup.group('Admin options')] +\
    graphql_admin_option +\
    graphql_admin_user_option +\
    graphql_admin_password_option


class Admin(GraphQL):
    @config.timeit
    def __init__(self, graphql: str, graphql_admin_user: str, graphql_admin_password: str) -> None:
        self.user = graphql_admin_user
        self.password = graphql_admin_password
        GraphQL.__init__(
            self,
            graphql=graphql,
            authorization=requests.auth._basic_auth_str(self.user, self.password)
        )

    @config.timeit
    def users(self) -> Any:
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
        return self.post(query)['data']['accountsList']
