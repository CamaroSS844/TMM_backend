from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, LoginSerializer
from rest_framework.permissions import AllowAny

class SignupView(APIView):
    permission_classes = [AllowAny]   # Override default permission
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        print("serializer is",serializer)
        if serializer.is_valid():
            user = serializer.save()
            print("user is",type(user))
            token, created = Token.objects.get_or_create(user = user)
            print("generated token is", token)
            return Response({"token":token.key, "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Override default permission
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid():
            user = authenticate(
                username = serializer.validated_data["username"],
                password = serializer.validated_data["password"]
            )
            if user:
                token, created = Token.objects.get_or_create(user = user)
                return Response({"token": token.key, "user": UserSerializer(user).data}, status = status.HTTP_200_OK)
            return Response({'error': "invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        try:
            request.auth.delete()
            return Response({"message": "Logged out successfully"}, status = status.HTTP_200_OK)
        except AttributeError:
            return Response({"error": "token not found"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    permission_classes = [AllowAny]  # Override default permission
    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)