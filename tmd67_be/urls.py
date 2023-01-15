"""tmd67_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from strawberry.django.views import AsyncGraphQLView

from tmd67_be.ac import views as ac_views
from tmd67_be.api import views
from tmd67_be.api.schema import schema

router = routers.DefaultRouter()
router.register(r"paths", views.ListPathView)
router.register(r"projects", views.ListProjectView)
router.register(
    r"user-register", ac_views.ACIDRegister, basename="user-register"
)
router.register(
    r"user-directory", ac_views.ACIDDirectory, basename="user-directory"
)
router.register(r"tickets", ac_views.TicketViewSet)
router.register(r"orders", ac_views.OrderViewSet)
router.register(r"badges", ac_views.BadgeViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r"accounts/", include("rest_framework.urls", namespace="admin")),
    path("graphql/", AsyncGraphQLView.as_view(schema=schema)),
    path("", include(router.urls)),
]
