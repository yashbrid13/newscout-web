from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView, UserView, Logoutview
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('login/',LoginView.as_view(),name="login"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/',UserView.as_view(),name="user"),
    path('logout/',Logoutview.as_view()),
    path('v1/',include('api.v1.urls')),
]
