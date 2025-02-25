from rest_framework.exceptions import APIException


class CustomException(APIException):
    status_code = 400
    default_detail = "An error occurred"
    default_code = "error"

    def __init__(self, message: str, status_code: int = 400):
        self.status_code = status_code
        self.detail = message
        super().__init__(message)
