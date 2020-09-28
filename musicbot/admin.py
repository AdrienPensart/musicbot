from typing import Any, Optional
import attr
import requests
from musicbot import defaults
from musicbot.config import config
from musicbot.graphql import GraphQL


@attr.s(auto_attribs=True, frozen=True)
class Admin:
    api: GraphQL

    @classmethod
    @config.timeit
    def from_auth(
        cls,
        graphql: str = defaults.DEFAULT_GRAPHQL_ADMIN,
        graphql_admin_user: Optional[str] = defaults.DEFAULT_GRAPHQL_ADMIN_USER,
        graphql_admin_password: Optional[str] = defaults.DEFAULT_GRAPHQL_ADMIN_PASSWORD,
    ):
        if graphql_admin_user and graphql_admin_password:
            authorization = requests.auth._basic_auth_str(graphql_admin_user, graphql_admin_password)
            api = GraphQL(graphql=graphql, authorization=authorization)
        else:
            api = GraphQL(graphql=graphql)
        return cls(api=api)

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
        return self.api.post(query)['data']['accountsList']
