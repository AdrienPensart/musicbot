from typing import Any, Optional
import attr
import requests
from musicbot.timing import timeit
from musicbot.graphql import GraphQL

DEFAULT_GRAPHQL_ADMIN = 'http://127.0.0.1:5001/graphql'
DEFAULT_GRAPHQL_ADMIN_USER: Optional[str] = None
DEFAULT_GRAPHQL_ADMIN_PASSWORD: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class Admin:
    api: GraphQL

    @classmethod
    @timeit
    def from_auth(
        cls,
        graphql: str = DEFAULT_GRAPHQL_ADMIN,
        graphql_admin_user: Optional[str] = DEFAULT_GRAPHQL_ADMIN_USER,
        graphql_admin_password: Optional[str] = DEFAULT_GRAPHQL_ADMIN_PASSWORD,
    ) -> "Admin":
        if graphql_admin_user and graphql_admin_password:
            authorization = requests.auth._basic_auth_str(graphql_admin_user, graphql_admin_password)
            api = GraphQL(graphql=graphql, authorization=authorization)
        else:
            api = GraphQL(graphql=graphql)
        return cls(api=api)

    @timeit
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
