from django.urls import path
from django.conf.urls import include
from rest_framework.authtoken.views import obtain_auth_token
from api.admin import custom_admin

urlpatterns = [
    path('admin/', custom_admin.urls),
    path('api/', include('api.urls')),
    path('auth/', obtain_auth_token),
]
