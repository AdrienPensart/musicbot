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


class FailedRequest(MusicbotError):
    def __init__(self, message=None, headers=None, operation=None, response=None):
        if not message:
            message = "Failed request | "
        self.operation = operation if operation is not None else []
        if response and 'errors' in response and response['errors']:
            messages = [error['message'] for error in response['errors']]
            message += f" error : {messages}"

        if headers:
            message += f" | headers : {headers}"
        super().__init__(message)
