from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from core.serializers import UserSerializer
from core.models import User
import jwt, datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serialzer = UserSerializer(data=request.data)
        serialzer.is_valid(raise_exception=True)
        serialzer.save()
        return Response(serialzer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email'] 
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')
        
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        response = Response()

        response.set_cookie(key='access_token', value=str(access_token), httponly=True)
        response.set_cookie(key='access_token', value=str(refresh_token), httponly=True)
        response.data = {
            'access_token' : str(access_token),
            'refresh_token': str(refresh_token)
        }
        
        return response  

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        
        if not token:
            raise AuthenticationFailed('UnAuthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('UnAuthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class Logoutview(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response 