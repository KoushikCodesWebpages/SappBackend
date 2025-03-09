# File: sapp/general/apps.py

from django.apps import AppConfig

class GeneralConfig(AppConfig):
    name = 'general'  # Using the direct app name without sapp prefix

    def ready(self):
        # Import the signal handler to register signals
        from general.utils.query_filter import filter_queryset_based_on_if_modified_since 
