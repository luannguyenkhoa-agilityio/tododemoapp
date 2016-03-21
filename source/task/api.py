from __future__ import absolute_import
from django.conf.urls import url
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from ..account.authentication import ApiKeyAuthenticationExt
from ..account.models import UserProfile
from ..commons.custom_exception import CustomBadRequest
from ..authorization.custom_authorization import UserObjectsOnlyAuthorization
from .models import Task
from ..commons.datetime_utils import *
from ..commons.paginator import PageNumberPaginator


class InternalUserProfileResource(ModelResource):
    """
    Shortcut for UserProfileResource, remove unnessesary data
    """

    class Meta(object):
        queryset = UserProfile.objects \
            .all()
        authentication = ApiKeyAuthenticationExt()
        authorization = Authorization()
        resource_name = 'userprofile'
        always_return_data = True
        fields = ['id']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_internal_profile__list'):
        resource_uri = super(InternalUserProfileResource, self).get_resource_uri(bundle_or_obj, url_name)
        return resource_uri


class TaskResource(ModelResource):
    # people = fields.ToManyField(InternalUserProfileResource, 'people', full=True, null=True)
    user = fields.ForeignKey(InternalUserProfileResource, 'user', full=True, null=False)
    total_records = fields.CharField(attribute='total_records', default=0, readonly=True)

    class Meta(object):
        queryset = Task.objects \
            .all() \
            .select_related() \
            .prefetch_related('user')
        resource_name = 'tasks'
        filtering = {
            'title': ALL,
            'id': ALL
        }
        authentication = ApiKeyAuthenticationExt()
        authorization = UserObjectsOnlyAuthorization()
        always_return_data = True
        paginator_class = PageNumberPaginator
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/listing%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_tasks'), name="api_get_tasks")
        ]

    def validation(self, bundle):
        if bundle.request.method == 'POST':
            if bundle.data.get('title', '') == '' \
                    or bundle.data.get('select_date', '') == '' \
                    or bundle.data.get('select_time', '') == '':
                raise CustomBadRequest(error_type='INVALID_OPERATOR', error_message="Cant create the task")

    def validate_duplicate(self, bundle):
        title = bundle.data['title']
        date = bundle.data['select_date']
        time = bundle.data['select_time']
        if title and date and time:
            if Task.objects.filter(title__iexact=title, select_time__iexact=time, select_date__iexact=date).exists():
                raise CustomBadRequest(error_type='DUPLICATE_TASK', error_message="A same task is already in your list")

    def hydrate(self, bundle):
        # Always tie task to the current user profile
        if bundle.request.method == 'POST':
            bundle.data["user"] = bundle.request.user.userprofile
        rq_date = bundle.data["select_date"]
        bundle.data["task_date"] = convert_to_date(rq_date)
        return super(TaskResource, self).hydrate(bundle)

    def dehydrate(self, bundle):
        if "user" in bundle.data:
            bundle.data.pop("user", None)
        if "total_records" in bundle.data:
            bundle.data.pop('total_records', None)
        if 'task_date' in bundle.data:
            bundle.data.pop('task_date', None)
        return super(TaskResource, self).dehydrate(bundle)

    def build_filters(self, filters=None):

        if filters is None:
            filters = {}
        q = None
        if 'q' in filters:
            q = filters.pop('q')
        orm_filters = super(TaskResource, self).build_filters(filters)
        if q:
            orm_filters['q'] = q

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'q' in applicable_filters:
            q = applicable_filters.pop('q')
        else:
            q = None
        semi_filtered = super(TaskResource, self).apply_filters(request, applicable_filters)

        # Always get task belong to an user
        semi_filtered = semi_filtered.filter(user_id=request.user.userprofile.id, is_deleted=False)
        # Just only get tasks that has date is greater than the current dates
        q_date = request.GET.get('date', None)
        if q_date is None:
            current_date = get_current_date()
        else:
            current_date = convert_to_date(q_date)
        semi_filtered = semi_filtered.filter(task_date=current_date)
        if q:
            semi_filtered = semi_filtered.search(q[0], raw=True, fields=('title',))
        return semi_filtered

    def obj_get(self, bundle, **kwargs):
        return super(TaskResource, self).obj_get(bundle, **kwargs)

    def obj_create(self, bundle, **kwargs):
        self.validation(bundle)
        # self.validate_duplicate(bundle)
        try:
            return super(TaskResource, self).obj_create(bundle, **kwargs)
        except Exception as e:
            raise CustomBadRequest(error_type='UNKNOWNERROR', error_message=str(e))

    # def save_m2m(self, bundle):
    #     people = bundle.data['people']
    #     for user in people:
    #         user.data['user'] = bundle.obj
    #
    #     return super(TaskResource, self).save_m2m(bundle)

    def get_tasks(self, request, **kwargs):

        self.is_authenticated(request)
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        self.log_throttled_access(request)
        return self.get_list(request)
