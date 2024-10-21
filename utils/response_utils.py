from rest_framework.response import Response
from rest_framework import status
from typing import Optional, Type


class ResponseManager:

    @classmethod
    def handle_success_response(cls, message: str, data: dict = dict, status_code: int = 200) -> Response:
        """handles success response"""
        return Response({
            "data": data,
            "message": message
        }, status=status_code)
    
    @classmethod
    def handle_error_response(cls, message: Optional[str] = "", status_code: int = 400) -> Response:
        """handles error response"""
        return Response({
            "data": None,
            "message": message
        }, status=status_code)
