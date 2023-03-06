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
router.register(r"clubs", views.ListClubView)

router.register(
    r"user-register", ac_views.ACIDRegister, basename="user-register"
)
router.register(
    r"user-directory", ac_views.ACIDDirectory, basename="user-directory"
)
router.register(r"ticket-products", ac_views.TicketProductViewSet)
router.register(r"orders", ac_views.OrderViewSet)
router.register(r"tickets", ac_views.TicketViewSet)
router.register(r"payment-records", ac_views.PaymentRecordViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r"accounts/", include("rest_framework.urls", namespace="admin")),
    path(r"csrf-token/", ac_views.csrf_token),
    path(r"user-login/", ac_views.user_login),
    path("google/auth/", ac_views.google_auth_rdr),
    path("google/callback/", ac_views.google_auth_cb),
    path(
        "payment-records/neweb-pay-notify/",
        ac_views.PaymentRecordViewSet.neweb_pay_notify,
    ),
    path(
        "payment-records/neweb-pay-return/",
        ac_views.PaymentRecordViewSet.neweb_pay_return,
    ),
    path("graphql/", AsyncGraphQLView.as_view(schema=schema)),
    path("", include(router.urls)),
]
