import logging

logger = logging.getLogger(__name__)


class MusicbotError(Exception):
    pass


class FilterNotFound(Exception):
    pass


class MusicbotConfigError(MusicbotError):
    pass


class FailedRegistration(MusicbotError):
    pass


class FailedAuthentication(MusicbotError):
    pass


class QuerySyntaxError(MusicbotError):
    pass


class FailedRequest(MusicbotError):
    def __init__(self, message=None, operation=None, response=None):
        if not message:
            message = "Failed request"
        super().__init__(message)

        self.operation = operation if operation is not None else []
        self.errors = []
        if isinstance(response, dict) and response.get('errors', []):
            self.errors = [error['message'] for error in response['errors']]


class FailedBatchRequest(MusicbotError):
    def __init__(self, message=None, operations=None, response=None):
        if not message:
            message = "Failed batch request"
        super().__init__(message)

        self.operations = operations if operations is not None else []
        self.errors = set()

        if not isinstance(response, list):
            logger.error(f"{self} : response is not a list : {type(response)}")
            return

        for response_object in response:
            if not isinstance(response_object, dict):
                logger.error(f"{self} : response object is not a dict : {type(response_object)}")
                continue
            errors = response_object.get('errors', [])
            self.errors.update([error['message'] for error in errors])
