import logging
import json
import requests
from musicbot.exceptions import FailedRequest, FailedAuthentication

logger = logging.getLogger(__name__)


class GraphQL:
    def __init__(self, graphql, headers=None, user=None, password=None):
        self.headers = headers if headers is not None else {}
        self.graphql = graphql
        if user and password:
            self.headers = {
                'Authorization': requests.auth._basic_auth_str(user, password)
            }

    def post(self, query):
        logger.debug(self.graphql)
        logger.debug(self.headers)
        logger.debug(query)
        response = requests.post(
            self.graphql,
            headers=self.headers,
            json={'query': query},
        )
        logger.debug(response)
        if response.status_code == 401:
            raise FailedAuthentication(f"Authentication failed: {response.text} | {self.headers}")

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise FailedRequest(f"Query failed : {query} | {self.headers}") from e

        logger.debug(json_response)
        if 'errors' in json_response and json_response['errors']:
            errors = [e['message'] for e in json_response['errors']]
            raise FailedRequest(f"Query failed: {query} | {errors} | {self.headers}")
        return json_response
