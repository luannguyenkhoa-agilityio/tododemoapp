import os
import math
import shutil

from django.core.files.storage import default_storage, FileSystemStorage
from django.conf import settings

def delete_obsolete_img(img_obj):
  
  if default_storage.get_available_name.im_class is FileSystemStorage:
    
    default_storage.delete(img_obj.original.name)

    cached_folder = os.path.dirname(img_obj.medium.path)
    if os.path.exists(cached_folder):
      shutil.rmtree(cached_folder)

  else:
    default_storage.delete(img_obj.original.name)
    default_storage.delete(img_obj.medium.name)
    default_storage.delete(img_obj.small.name)

def null_or_number(input):
    """
    Check an input is not null or a number
    """
    return not input or isnumeric(input)

def isnumeric(inp):
    """
    Check a string is numeric
    """
    try:
        float(inp)
        return True
    except ValueError:
        return False

def get_pk_from_uri(uri):
    pk = filter(None, uri.split('/'))[-1]
    return pk if isnumeric(pk) else None

def center_geo_coordinate(geo_coordinates):
    """
    Calculate the center geographic coordinate of 2 lat/long
    @geo_coordinates: Array of lat/long object: [{lat: "", lng: ""}]
    """    
    x = 0
    y = 0
    z = 0

    for geo_coordinate in geo_coordinates:
        latitude = geo_coordinate["lat"] * math.pi / 180
        longtitude = geo_coordinate["lng"] * math.pi / 180
        x += math.cos(latitude) * math.cos(longtitude)
        y += math.cos(latitude) * math.sin(longtitude)
        z += math.sin(latitude)

    total = len(geo_coordinates)

    x /= total
    y /= total
    z /= total

    central_longtitude = math.atan2(y, x)
    central_squareroot = math.sqrt(x * x + y * x)
    central_latitude = math.atan2(z, central_squareroot)

    return {
        'lat': central_latitude * 180 / math.pi,
        'lng': central_longtitude * 180 / math.pi
    }

def get_client_timezone(request):
    return settings.DEFAULT_TIMEZONE