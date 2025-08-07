from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="user_register"),
    path("login/", views.UserLoginView.as_view(), name="user_login"),
    path("me/", views.UserProfileView.as_view(), name="user_profile"),
    path("edit/", views.UserProfileView.as_view(), name="user_edit"),
    path(
        "seller/registration/",
        views.SellerRegistrationView.as_view(),
        name="seller_registration",
    ),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", views.TokenVerifyView.as_view(), name="token_verify"),
]
