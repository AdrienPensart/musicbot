import logging
import json
from typing import Optional, List, Any
import requests
import attr
from musicbot.exceptions import FailedRequest, FailedBatchRequest, FailedAuthentication

logger = logging.getLogger(__name__)

DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'


@attr.s(auto_attribs=True, repr=False)
class GraphQL:
    graphql: str
    authorization: Optional[str] = None
    session: requests.Session = requests.Session()

    def __repr__(self):
        return self.graphql

    def batch(self, operations: List[Any]) -> Any:
        json_response = self._post(operations)
        for response_object in json_response:
            if 'errors' in response_object and response_object['errors']:
                raise FailedBatchRequest(operations=operations, response=json_response)
        return json_response

    def post(self, query: Any) -> Any:
        json_response = self._post({'query': query})
        if 'errors' in json_response and json_response['errors']:
            logger.debug(json_response)
            raise FailedRequest(operation=query, response=json_response)
        return json_response

    def _post(self, operation: Any) -> Any:
        headers = {'Authorization': self.authorization} if self.authorization else {}
        response = self.session.post(
            self.graphql,
            headers=headers,
            json=operation,
        )
        logger.debug(response)
        if response.status_code == 401:
            raise FailedAuthentication(f"Authentication failed: {response.text} | {headers}")

        response.raise_for_status()

        try:
            json_response = response.json()
        except json.JSONDecodeError as e:
            raise FailedRequest(operation=operation, response=response) from e
        return json_response
