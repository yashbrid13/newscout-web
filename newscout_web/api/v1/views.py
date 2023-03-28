from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import (CategorySerializer,)
from core.models import Category
from rest_framework.response import Response
from collections import OrderedDict
from django.http import Http404

def create_error_response(response_data):
    """
    method used to create response data in given format
    """
    return OrderedDict({
        "header": {
            "status": "0"
        },
        "errors": response_data
    }
    )

def create_response(response_data):
    """
    method used to create response data in given format
    """
    response = OrderedDict()
    response["header"] = {"status": "1"}
    response["body"] = response_data
    return response


class CategoryListAPIView(APIView):
    # TODO: User auth pending
    permission_classes = (AllowAny,)


    def post(self, request, format=None):
        """
        Save new category to database
        """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(create_response(serializer.data))
        return Response(create_error_response(serializer.errors), status=400)


    def get(self, request, format=None, *args, **kwargs):
        """
        List all news categories
        """
        categories = CategorySerializer(Category.objects.all(), many=True)
        return Response(create_response({"categories": categories.data}))


    def put(self, request, format=None):
        """
        update category in database
        """
        _cat = request.data.get("category")
        category = Category.objects.get(name=_cat)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(create_response(serializer.data))
        return Response(create_error_response(serializer.errors), status=400)
        

    def delete(self, request, format=None):
        """
        Delete category in database
        """
        _cat = request.data.get("category")
        category = Category.objects.get(name=_cat)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            category.delete()
            return Response(create_response({"categories": serializer.data}))
        return Response(create_error_response(serializer.errors), status=400)
        