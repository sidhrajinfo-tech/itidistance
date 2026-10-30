"""Pure Python distance helpers. All distances are great-circle, not driving."""
from math import radians, sin, cos, asin, sqrt, isfinite


def valid_point(lat, lon):
    try:
        return isfinite(float(lat)) and isfinite(float(lon)) and -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (TypeError, ValueError):
        return False


def haversine_km(lat1, lon1, lat2, lon2):
    if not (valid_point(lat1, lon1) and valid_point(lat2, lon2)):
        raise ValueError('Invalid latitude/longitude')
    a, b, c, d = map(radians, map(float, [lat1, lon1, lat2, lon2]))
    h = sin((c-a)/2)**2 + cos(a)*cos(c)*sin((d-b)/2)**2
    return 6371.0088 * 2 * asin(sqrt(min(1.0, max(0.0, h))))


def eligible(record):
    return bool(record.get('distanceEligible')) and valid_point(record.get('lat'), record.get('lon'))
