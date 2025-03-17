import math
from datetime import datetime, timezone
from django.utils.http import http_date, parse_http_date_safe
from django.http import HttpResponseNotModified
from rest_framework.response import Response
from django.db import models
from django.apps import apps

class ETagIfModifiedSinceMiddleware:
    """
    Middleware to globally handle ETag and If-Modified-Since filtering for all API responses.
    Filters querysets based on If-Modified-Since header globally, and sends full data for new users.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract If-Modified-Since header
        if_modified_since = request.headers.get("If-Modified-Since")
        if if_modified_since:
            timestamp = parse_http_date_safe(if_modified_since)
            if timestamp:
                request.if_modified_since_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
            else:
                request.if_modified_since_dt = None
        else:
            # If If-Modified-Since header is missing, this implies it's a new request or the first-time user
            request.if_modified_since_dt = None

        # Filter querysets based on the If-Modified-Since header globally (if present)
        self.filter_queryset_based_on_if_modified_since(request)

        # Get response
        response = self.get_response(request)

        # Ensure response is an API response
        if not isinstance(response, Response) or response.status_code != 200:
            return response  

        # Extract last_updated timestamp from the response data
        last_updated = self.get_last_updated(response)
        if not last_updated:
            return response

        # Process If-Modified-Since: If data is not modified, return 304
        if request.if_modified_since_dt and last_updated <= request.if_modified_since_dt:
            return HttpResponseNotModified()

        # Process ETag
        etag_value = f'"{int(last_updated.timestamp() * 1000)}"'
        client_etag = request.headers.get("If-None-Match")

        if client_etag == etag_value:
            return HttpResponseNotModified()

        # Add headers
        response["Last-Modified"] = http_date(last_updated.timestamp())
        response["ETag"] = etag_value

        # Set flag that ETag processing has been applied
        request.etag_middleware_triggered = True

        return response

    def get_last_updated(self, response):
        """
        Extracts the last_updated timestamp from response data.
        Handles list, dict, and paginated responses.
        """
        try:
            data = response.data
            if isinstance(data, dict) and "results" in data:  # Handle paginated response
                data = data["results"]

            if isinstance(data, list) and data:
                last_updated = max(
                    datetime.fromisoformat(obj["last_updated"]).replace(tzinfo=timezone.utc)
                    for obj in data if "last_updated" in obj
                )
                return last_updated
            elif isinstance(data, dict) and "last_updated" in data:
                return datetime.fromisoformat(data["last_updated"]).replace(tzinfo=timezone.utc)
        except Exception:
            return None

        return None

    def filter_queryset_based_on_if_modified_since(self, request):
        """
        This function will globally filter querysets for views based on the If-Modified-Since header.
        It checks if the `request.if_modified_since_dt` exists, then applies it to any queryset.
        """
        if hasattr(request, 'if_modified_since_dt') and request.if_modified_since_dt:
            # Filter querysets for views based on the `last_updated` field globally
            for model in apps.get_models():
                if hasattr(model, 'last_updated'):  # Check if the model has the last_updated field
                    model.objects = model.objects.filter(last_updated__gt=request.if_modified_since_dt)