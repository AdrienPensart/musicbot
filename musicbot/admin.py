from typing import Any, Optional
import requests
from musicbot import defaults
from musicbot.config import config
from musicbot.graphql import GraphQL


class Admin(GraphQL):
    @config.timeit
    def __init__(
        self,
        graphql: str = defaults.DEFAULT_GRAPHQL_ADMIN,
        graphql_admin_user: Optional[str] = defaults.DEFAULT_GRAPHQL_ADMIN_USER,
        graphql_admin_password: Optional[str] = defaults.DEFAULT_GRAPHQL_ADMIN_PASSWORD
    ) -> None:
        self.user = graphql_admin_user
        self.password = graphql_admin_password
        authorization = None
        if self.user and self.password:
            authorization = requests.auth._basic_auth_str(self.user, self.password)

        GraphQL.__init__(
            self,
            graphql=graphql,
            authorization=authorization
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
