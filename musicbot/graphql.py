import logging
import json
from typing import Optional, Any
import requests
import attr
from musicbot.exceptions import FailedRequest, FailedAuthentication

logger = logging.getLogger(__name__)

DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'


@attr.s(auto_attribs=True, frozen=True)
class GraphQL:
    graphql: str
    authorization: Optional[str] = None

    def post(self, query: str) -> Any:
        headers = {'Authorization': self.authorization} if self.authorization else {}
        response = requests.post(
            self.graphql,
            headers=headers,
            json={'query': query},
        )
        logger.debug(response)
        if response.status_code == 401:
            raise FailedAuthentication(f"Authentication failed: {response.text} | {headers}")

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise FailedRequest(f"Query failed : {query} | {headers}") from e

        logger.debug(json_response)
        if 'errors' in json_response and json_response['errors']:
            errors = [e['message'] for e in json_response['errors']]
            raise FailedRequest(f"Query failed: {query} | {errors} | {headers}")
        return json_response
