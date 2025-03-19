import math
import logging
from datetime import datetime, timezone
from django.utils.http import http_date, parse_http_date_safe
from django.http import HttpResponseNotModified
from rest_framework.response import Response

class ETagIfModifiedSinceMiddleware:
    """
    Middleware to globally handle ETag and If-Modified-Since filtering for all API responses.
    Works for Django REST Framework & standard Django views.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        print("✅ ETagIfModifiedSinceMiddleware is loaded and active!")  # Confirms middleware is initialized

    def __call__(self, request):
        print("\n")
        print(f"🔄 Middleware triggered for: {request.path}")

        # Extract If-Modified-Since header
        request.if_modified_since_dt = self.extract_if_modified_since(request)

        # Get response
        response = self.get_response(request)

        # Check if response is valid for ETag processing
        if not isinstance(response, Response):
            print(f"⏭️ Skipping middleware for {request.path} (Not a DRF Response)")
            return response  

        if response.status_code not in [200, 201]:
            print(f"⏭️ Skipping middleware for {request.path} (Response status: {response.status_code})")
            return response  

        # Apply ETag & Last-Modified headers
        print(f"✅ Applying ETag & Last-Modified for: {request.path}")
        return self.apply_etag_and_last_modified(request, response)

    def extract_if_modified_since(self, request):
        """Extract If-Modified-Since header and convert to datetime."""
        if_modified_since = request.headers.get("If-Modified-Since")
        if if_modified_since:
            timestamp = parse_http_date_safe(if_modified_since)
            if timestamp:
                print(f"📅 Parsed If-Modified-Since: {if_modified_since}")
                return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
            else:
                print(f"⚠️ Failed to parse If-Modified-Since: {if_modified_since}")
        return None

    def apply_etag_and_last_modified(self, request, response):
        """Adds ETag and Last-Modified headers to API responses."""
        last_updated = self.get_last_updated(response)

        if not last_updated:
            print(f"⚠️ No 'last_updated' found in response for {request.path}, skipping ETag.")
            return response

        # Check If-Modified-Since
        if request.if_modified_since_dt and last_updated <= request.if_modified_since_dt:
            print(f"304 Not Modified: {request.path}")
            return HttpResponseNotModified()

        # Generate ETag (millisecond timestamp)
        etag_value = f'"{int(last_updated.timestamp() * 1000)}"'
        client_etag = request.headers.get("If-None-Match")

        if client_etag == etag_value:
            print(f"304 Not Modified (ETag match) for {request.path}")
            return HttpResponseNotModified()

        # ✅ Set response headers
        response["Last-Modified"] = http_date(last_updated.timestamp())
        response["ETag"] = etag_value
        print(f"✅ ETag set: {etag_value} | Last-Modified: {response['Last-Modified']} for {request.path}")

        return response
    print("\n")

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
                if last_updated_list:
                    last_updated = max(last_updated_list)
                    print(f"📅 Extracted last_updated from list: {last_updated}")
                    return last_updated

            elif isinstance(data, dict) and "last_updated" in data:
                last_updated = datetime.fromisoformat(data["last_updated"]).replace(tzinfo=timezone.utc)
                print(f"📅 Extracted last_updated from dict: {last_updated}")
                return last_updated

        except Exception as e:
            print(f"❌ Error extracting last_updated: {e}")
        return None
