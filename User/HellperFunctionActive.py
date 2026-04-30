from .models import *

def log_activity(user, action, object_id=None, metadata=None):
    UserActivity.objects.create(
        user=user,
        action=action,
        object_id=object_id,
        metadata=metadata or {}
    )