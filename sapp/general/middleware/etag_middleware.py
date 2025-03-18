import math
import logging
from datetime import datetime, timezone
from django.utils.http import http_date, parse_http_date_safe
from django.http import HttpResponseNotModified
from rest_framework.response import Response
from django.db.models import QuerySet
from django.apps import apps

logger = logging.getLogger(__name__)

class ETagIfModifiedSinceMiddleware:
    """
    Middleware to globally handle ETag and If-Modified-Since filtering for all API responses.
    Works for Django REST Framework & standard Django views.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Middleware triggered for {request.path}")

        # Extract If-Modified-Since header
        request.if_modified_since_dt = self.extract_if_modified_since(request)

        # Get response
        response = self.get_response(request)

        # ✅ Ensure it's an API response (Django REST Framework or JSON response)
        if not isinstance(response, Response) or response.status_code not in [200, 201]:
            return response  

        # ✅ Apply ETag & Last-Modified headers
        return self.apply_etag_and_last_modified(request, response)

    def extract_if_modified_since(self, request):
        """Extract If-Modified-Since header and convert to datetime."""
        if_modified_since = request.headers.get("If-Modified-Since")
        if if_modified_since:
            timestamp = parse_http_date_safe(if_modified_since)
            return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc) if timestamp else None
        return None

    def apply_etag_and_last_modified(self, request, response):
        """Adds ETag and Last-Modified headers to API responses."""
        last_updated = self.get_last_updated(response)

        if not last_updated:
            return response

        # Check If-Modified-Since
        if request.if_modified_since_dt and last_updated <= request.if_modified_since_dt:
            return HttpResponseNotModified()

        # Generate ETag (millisecond timestamp)
        etag_value = f'"{int(last_updated.timestamp() * 1000)}"'
        client_etag = request.headers.get("If-None-Match")

        if client_etag == etag_value:
            return HttpResponseNotModified()

        # ✅ Set response headers
        response["Last-Modified"] = http_date(last_updated.timestamp())
        response["ETag"] = etag_value

        return response

    def get_last_updated(self, response):
        """
        Extracts the last_updated timestamp from API response data.
        Works for list, dict, and paginated responses.
        """
        try:
            data = response.data

            if isinstance(data, dict) and "results" in data:  # Handle paginated response
                data = data["results"]

            if isinstance(data, list) and data:
                last_updated_list = [
                    datetime.fromisoformat(obj["last_updated"]).replace(tzinfo=timezone.utc)
                    for obj in data if "last_updated" in obj
                ]
                return max(last_updated_list) if last_updated_list else None

            elif isinstance(data, dict) and "last_updated" in data:
                return datetime.fromisoformat(data["last_updated"]).replace(tzinfo=timezone.utc)

        except Exception as e:
            logger.error(f"Error extracting last_updated: {e}")

        return None
