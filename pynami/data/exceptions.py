class NamiResponseTypeException(Exception):
    """
    This is raised when the response type from the |NAMI| is not in list of
    allowed values or more specifically when the |NAMI| returns an error, a
    warning or an exception.
    """
    def __init__(self, response_type):
        super.__init__("Invalid response type {response_type} received!")


class NamiResponseSuccessException(Exception):
    """
    This is being raised when the response 'success' field is not :data:`True`.
    """
    def __init__(self):
        super.__init__("Received success=False from NaMi-endpoint.")


class NamiHTTPException(Exception):
    """Raised when the HTTP status code was not as expected!"""
    def __init__(self, status_code):
        super.__init__("Invalid HTTP status code {status_code}.")