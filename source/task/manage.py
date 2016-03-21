from ..commons.utils import null_or_number
from django.db import models


def validate_restaurant_filters(limit, offset):
    """
    Validate filter data
    :param limit: this arg is define how many items per page
    :param offset: the value of page
    """
    if not null_or_number(limit) or not null_or_number(offset):
        return False

    return True