from django.shortcuts import render
from django.http import HttpResponse
from .renderers import MyCustomRenderer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import CustomUserLoginModelSerializer, CustomUserRegistrationModelSerializer, ImageSerializer


# generate custom token from simple jwt third party package 
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class CustomUserRegistrationView(APIView):
    renderer_classes = [MyCustomRenderer]
    def post(self, requset, format=None):
        serializer = CustomUserRegistrationModelSerializer(data=requset.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'user': 'Registration successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserLoginView(APIView):
    def post(self, request, format=None):
        serializer = CustomUserLoginModelSerializer(data=request.data)

        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)

        # if serializer not valid raise_exception occurs
        if serializer.is_valid(raise_exception=True): 
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token': token, 'msg': 'login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': {'non_field_error': ['username or password field may be inncorrect']}},
                        status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_image(request, pk=None):

    if request.method == 'POST':
        serializer = ImageSerializer(data=request.data) # convert json object into python data
        if serializer.is_valid():
            serializer.save()
            return Response({
                'thumbnail': serializer.data['thumbnail'].split("/")[-1],
                'midium': serializer.data['medium'].split("/")[-1],
                'large': serializer.data['large'].split("/")[-1],
                'grayScale': serializer.data['grayscale'].split("/")[-1]
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)