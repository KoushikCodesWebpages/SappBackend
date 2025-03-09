# File: sapp/general/utils/query_filter.py

from django.db.models.signals import pre_init
from django.dispatch import receiver
from django.db.models import QuerySet
from datetime import datetime, timezone

@receiver(pre_init)
def filter_queryset_based_on_if_modified_since(sender, args, kwargs, **extras):
    print("🔴 Signal triggered!")  # Debug print to confirm signal is fired

    request = kwargs.get("request", None)
    if request and hasattr(request, "if_modified_since_dt") and request.if_modified_since_dt:
        if hasattr(sender, "last_updated") and isinstance(sender.objects, QuerySet):
            print(f"🔍 Applying global filter: last_updated > {request.if_modified_since_dt}")
            kwargs["queryset"] = sender.objects.filter(last_updated__gt=request.if_modified_since_dt)
