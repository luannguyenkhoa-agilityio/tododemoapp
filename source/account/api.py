from __future__ import absolute_import
from django.contrib.sites.models import Site
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.db import transaction
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.http import HttpUnauthorized
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey
from tastypie import fields
from .signals import *
from .authentication import ApiKeyAuthenticationExt
from .validation import UserProfileValidation
from ..commons.custom_exception import CustomBadRequest
from ..commons.multipart_resource import MultipartResource

current_site = Site.objects.get_current()

class InternalUserResource(ModelResource):
    class Meta(object):
        queryset = User.objects.all()
        excludes = ['password', 'is_superuser']
        resource_name = 'auth/users'
        authenticate = ApiKeyAuthenticationExt()
        authorization = Authorization()

class UserResource(ModelResource):

    class Meta(object):
        queryset = User.objects.all()
        fields = ['username', 'first_name', 'last_name']
        excludes = ['email', 'password', 'is_superuser']
        resource_name = 'auth/users'
        authentication = ApiKeyAuthenticationExt()
        authorization = Authorization()

class UserImageResource(ModelResource):
    original = fields.CharField(attribute='get_origin_url')
    medium = fields.CharField(attribute='get_medium_url')
    small = fields.CharField(attribute='get_small_url')

    class Meta(object):
        queryset = UserImage.objects.all()
        fields = ['id', 'original', 'medium', 'small']
        resource_name = 'userimage'
        authorization = Authorization()
        authentication = ApiKeyAuthenticationExt()
        always_return_data = True

class InternalUserProfileResource(ModelResource):
    # image = fields.ForeignKey(UserImageResource, 'image', full=True, null=True, readonly=True)
    first_name = fields.CharField(attribute='user__first_name', null=True)
    last_name = fields.CharField(attribute='user__last_name', null=True)

    class Meta(object):
        queryset = UserProfile.objects.all() \
            .prefetch_related('user')
        fields = ['id']
        resource_name = 'auth/user'
        authentication = ApiKeyAuthenticationExt()
        authorization = Authorization()
        filtering = {
            "id": 'exact'
        }

class UserProfileResource(ModelResource):

    user = fields.ToOneField(InternalUserResource, attribute='user', null=True)
    # image = fields.ForeignKey(UserImageResource, 'image', full=True, null=True)
    first_name = fields.CharField(attribute='user__first_name', null=True)
    last_name = fields.CharField(attribute='user__last_name', null=True)
    email = fields.CharField(attribute='user__email', null=True)

    class Meta(object):
        queryset = UserProfile.objects \
            .prefetch_related('user')
            # .prefetch_related('image')
        resource_name = 'userprofile'
        always_return_data = True
        authentication = ApiKeyAuthenticationExt()
        authorization = Authorization()
        validation = UserProfileValidation()

    def hydrate(self, bundle):

        bundle.data['user'] = {}
        bundle.data['user']['id'] = bundle.request.user.id
        if 'email' in bundle.data:
            bundle.data['user']['email'] = bundle.data['email']
        if 'first_name' in bundle.data:
            bundle.data['user']['first_name'] = bundle.data['first_name']
            bundle.data['user']['last_name'] = bundle.data['last_name']

        return super(UserProfileResource, self).hydrate(bundle)

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/profile-image%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('upload_profile_image'), name="api_upload_profile_image"),
        ]

    def upload_profile_image(self, request, **kwargs):
    
        self.is_authenticated(request)
        self.method_check(request, allowed=['post'])
        self.throttle_check(request)
    
        # Create new image
        userimage = UserImage(original=request.FILES['original'])
        userimage.save()
    
        # Tie image to user profile
        updated = UserProfile.objects.filter(user__id=request.user.id).update(image=userimage)
    
        api_uri = os.path.split(os.path.split(self.get_resource_uri())[0])[0]
    
        resource_uri = '/'.join((api_uri, UserImageResource.Meta.resource_name, str(userimage.id), ''))
    
        self.log_throttled_access(request)
        return self.create_upload_response(request, resource_uri, userimage, updated)

    def create_upload_response(self, request, resource_uri, image_model, success):
        """
        Return uploaded image response
        """
        if success:
            return self.create_response(request, {"success": True,
                                                  "resource_uri": resource_uri,
                                                  "origin": image_model.get_original_url(),
                                                  "small": image_model.get_small_url(),
                                                  "medium": image_model.get_medium_url()})
        else:
            raise CustomBadRequest(error_type='UNKNOWNERROR', error_message="Can't update user profile image")        


class AuthenticationResource(ModelResource):
    class Meta(object):
        allowed_methods = ['get', 'post']
        always_return_data = True
        authentication = Authentication()
        authorization = Authorization()
        queryset = User.objects.all()
        resource_name = 'authentication'
        fields = ['username', 'email', 'password']

    def prepend_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/sign_in%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sign_in'), name="api_sign_in"),
            url(r"^(?P<resource_name>%s)/sign_out%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sign_out'), name="api_sign_out"),
        ]

    def sign_in(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/join'))

        retype_password = data.get('retype_password', None)
        if retype_password is not None:
            return self.sign_up_by_email(request, **kwargs)
        elif 'email' in data and 'password' in data:
            return self.sign_in_by_email(request, **kwargs)
        else:
            raise CustomBadRequest(error_type='UNAUTHORIZED')

    def sign_in_by_email(self, request, **kwargs):
        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/join'))

        email = data.get('email', '')
        password = data.get('password', '')
        user = User.objects.filter(email=email).first()

        if user:
            if user.check_password(password):
                user = authenticate(username=email, password=password)
                login(request, user)
                apikey = ApiKey.objects.filter(user=user).first()
                return self.create_auth_response(request=request, user=user, api_key=apikey.key, is_new=True)
            else:
                raise CustomBadRequest(error_type='UNAUTHORIZED', error_message='Your password is not correct')
        else:
            raise CustomBadRequest(error_type='UNAUTHORIZED',
                                   error_message='Your email address is not registered. Please register')

    def sign_up_by_email(self, request, **kwargs):

        data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/join'))

        email = data.get('email', '')
        password = data.get('password', '')
        first_name = data.get('first_name', 'abc')
        last_name = data.get('last_name', 'cbd')

        if last_name:
            last_name = last_name.strip()
        if first_name:
            first_name = first_name.strip()

        if User.objects.filter(email__iexact=email).exists():
            raise CustomBadRequest(error_type='DUPLICATE_VALUE', field='email', obj='email')
        else:
            try:
                with transaction.atomic():

                    User.objects.create_user(username=email, email=email, password=password,
                                                    first_name=first_name, last_name=last_name)
                    user = authenticate(username=email, password=password)

                    login(request, user)

                    if user is not None:
                        self.create_userprofile(user.id)
                        apiKey = ApiKey.objects.filter(user=user).first()
                        return self.create_auth_response(request=request, user=user, api_key=apiKey.key, is_new=True)
                    else:
                        raise CustomBadRequest(error_type='UNKNOWN_ERROR', error_message='Cannot sign up by this email.')
            except ValueError as e:
                raise CustomBadRequest(error_type='UNKNOWN_ERROR', error_message=str(e))

    def sign_out(self, request, **kwargs):
        self.is_authenticated(request)
        self.method_check(request, allowed=['post', 'get'])

        if request.user and request.user.is_authenticated():
            logout(request)

            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False}, HttpUnauthorized)

    def create_auth_response(self, request, user, api_key, is_new=False):
        """
        Genetate response data for authentication process
        """
        userprofile = UserProfile.objects.get(id=user.userprofile.id)

        resource_instance = UserProfileResource()
        bundle = resource_instance.full_hydrate(resource_instance.build_bundle(obj=userprofile, request=request))
        bundle.data['api_key'] = api_key
        bundle.data['is_new'] = is_new
        # api_uri = os.path.split(os.path.split(self.get_resource_uri())[0])[0]
        # if 'image' in bundle.data and bundle.data['image']:
        #     image_uri = bundle.data['image'].data.get('resource_uri', '')
        #     if not image_uri:
        #         resource_uri = '/'.join(
        #             (api_uri, UserImageResource.Meta.resource_name, str(bundle.data['image'].data['id'])))
        #         bundle.data['image'].data['resource_uri'] = resource_uri

        return self.create_response(request, bundle)
    def create_userprofile(self, user_id, **kwargs):
        """
        Create blank user profile base on user_id
        """

        # Add the user_id to kwargs
        kwargs['user_id'] = user_id

        # register_type = kwargs.get('register_type', None)
        # is_facebook = register_type == 1

        # Create user profile
        userprofile, _ = UserProfile.objects.get_or_create(user__id=user_id, defaults=kwargs)

        if userprofile is None:
            raise CustomBadRequest(error_type='UNKNOWNERROR', error_message="Can't create userprofile and address")
