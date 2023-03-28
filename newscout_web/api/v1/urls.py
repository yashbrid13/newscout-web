from django.contrib import admin
from django.urls import path, include
from .views import CategoryListAPIView

urlpatterns = [
    path('cl',CategoryListAPIView.as_view(),name="category list"),
]
