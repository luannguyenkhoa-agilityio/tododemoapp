"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from __future__ import absolute_import
from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from tastypie.api import Api

from source.task.api import TaskResource
from source.account.api import AuthenticationResource, UserProfileResource, UserResource

# define api
v1_api = Api(api_name='v1')
v1_api.register(UserProfileResource())
v1_api.register(AuthenticationResource())
v1_api.register(UserResource())
v1_api.register(TaskResource())

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include(v1_api.urls)),
                       url(r'^account/', include('allauth.urls')),
                       )
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('', url(r'^__debug__', include(debug_toolbar.urls)))
