from datetime import datetime

def serialize_datetime(obj):
    """Custom serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj