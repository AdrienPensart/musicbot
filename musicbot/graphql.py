import logging
import requests
from musicbot.exceptions import FailedRequest

logger = logging.getLogger(__name__)


class GraphQL:
    def __init__(self, graphql, headers=None):
        self.graphql = graphql
        self.headers = headers

    def _post(self, query, failure=None):
        logger.debug(query)
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        json_response = response.json()
        logger.debug(json_response)
        if response.status_code != 200:
            failure = failure if failure is not None else FailedRequest(f"Query failed: {json_response}")
            raise failure
        if 'errors' in json_response and json_response['errors']:
            errors = [e['message'] for e in json_response['errors']]
            failure = failure if failure is not None else FailedRequest(f"Query failed: {errors}")
            raise failure
        return json_response
