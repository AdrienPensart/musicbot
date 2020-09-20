import logging
import json
from typing import Any, Optional
import requests
from musicbot.exceptions import FailedRequest, FailedAuthentication

logger = logging.getLogger(__name__)


class GraphQL:
    def __init__(self, graphql: str, authorization: Optional[str] = None) -> None:
        self.graphql = graphql
        self._headers = {'Authorization': authorization} if authorization else {}

    def post(self, query: str) -> Any:
        response = requests.post(
            self.graphql,
            headers=self._headers,
            json={'query': query},
        )
        logger.debug(response)
        if response.status_code == 401:
            raise FailedAuthentication(f"Authentication failed: {response.text} | {self._headers}")

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise FailedRequest(f"Query failed : {query} | {self._headers}") from e

        logger.debug(json_response)
        if 'errors' in json_response and json_response['errors']:
            errors = [e['message'] for e in json_response['errors']]
            raise FailedRequest(f"Query failed: {query} | {errors} | {self._headers}")
        return json_response
