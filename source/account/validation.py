from django.db.models import Q
from django.contrib.auth.models import User
from ..commons.custom_exception import CustomBadRequest
from tastypie.validation import Validation

class UserProfileValidation(Validation):
    def  is_valid(self, bundle, request=None):
        errors = {}
        email = bundle.data.get('email', '')
        if email:
            is_exist = User.objects.filter(email=email).filter(~Q(userprofile=bundle.obj.id)).exists()
            if is_exist:
                raise CustomBadRequest(error_type='UNKNOWNERROR', error_message='This email already has been registered by another account')
        return errors