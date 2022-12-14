
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from mantra import views


router = DefaultRouter()
router.register('mantras', views.MantraViewSet)
router.register('tags', views.TagViewSet)

app_name = 'mantra'

urlpatterns = [
    path('', include(router.urls)),
]