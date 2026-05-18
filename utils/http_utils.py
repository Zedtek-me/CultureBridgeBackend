from rest_framework.response import Response
from rest_framework import status
from typing import Optional, Type, Any

import requests
import json

from utils.helpers import get_logger

from django.conf import settings


logger = get_logger()
class ResponseManager:

    @classmethod
    def handle_success_response(cls, message: str, data: dict = dict, status_code: int = 200) -> Response:
        """handles success response"""
        return Response({
            "data": data,
            "message": message,
            "status": "success"
        }, status=status_code)

    @classmethod
    def handle_error_response(cls, message: Optional[str] | Any | dict = "", status_code: int = 400) -> Response:
        """handles error response"""
        return Response({
            "data": None,
            "message": message,
            "status": "error"
        }, status=status_code)

    @classmethod
    def handle_paginated_response(
        cls, message: str = "Data successfully retrieved",
        data: Optional[dict] = None, status_code: int = 200,
    ):
        """returns an already paginated data response"""
        return Response(data={"message": message, **(data or {})}, status=status_code)


class HttpClient:
    """
    handles http requests and responses
    for external services
    """

    def __init__(self, base_url: str, endpoint: Optional[str] = None, *args, **kwargs):
        self.base_url = base_url
        self.endpoint = endpoint or ""
        self.headers = kwargs.get("headers", {"Content-Type": "application/json"})

    def _parse_response(
        self, response: requests.Response
    ) -> dict:
        try:
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(e)
            return {
                "status": "error",
                "message": f"{e.args[0]}"
            }
        except json.JSONDecodeError as e:
            logger.exception(f"error occurred when parsing response: {e}")
            return {
                "status": "error",
                "message": f"Unable to parse response: {e.args[0]}"
            }

    def get(
        self, endpoint: Optional[str] = None, params: Optional[dict] = None,
        extra_headers: Optional[dict] = None
    ) -> dict:
        """handles get request"""
        url = self._get_url(endpoint)
        headers = {**self.headers, **(extra_headers or {})}
        response = requests.request(
            "GET", url, params=params, headers=headers,
            timeout=settings.DEFAULT_REQUEST_TIMEOUT
        )
        return self._parse_response(response)

    def post(
        self, endpoint: Optional[str] = None, data: Optional[dict] = None,
        extra_headers: Optional[dict] = None, payload: Optional[dict] = None
    ) -> dict:
        """handles post request"""
        url = self._get_url(endpoint)
        headers = {**self.headers, **(extra_headers or {})}
        timeout = settings.DEFAULT_REQUEST_TIMEOUT or 5000
        response = requests.request(
            "POST", url, json=payload, headers=headers,
            timeout=int(timeout), data=data
        )
        return self._parse_response(response)

    def _get_url(
        self, endpoint: Optional[str] = None
    ) -> str:
        if not endpoint:
            return f"{self.base_url}{'/' if '/' not in self.base_url else ''}{self.endpoint or ''}"
        return f"{self.base_url}{'/' if '/' not in endpoint else ''}{endpoint}"
