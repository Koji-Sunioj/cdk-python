from decimal import Decimal

def serialize_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)