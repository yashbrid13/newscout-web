from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, LoginView, UserView, Logoutview

urlpatterns = [
    path('register',RegisterView.as_view()),
    path('login',LoginView.as_view()),
    path('user',UserView.as_view()),
    path('logout',Logoutview.as_view()),
]
