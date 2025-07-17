from errno import EUSERS

from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthonticated
from rest_framework.response import Response
from rest_framework_simpljwt.tokens import RefreshToken
from rest_framework_simpljwt.exceptions import TokenError
from django.contrib.auth import authonticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decotator
from .models import User,SellerRegistration
from .serializers import (UserSerializer,UserRegistrationSerializer,LoginSerializer,UserUpdateSerializer,SellerRegistrationSerializer,TokenVerifySerializer,TokenRefreshSerializer)


@api_view(['POST'])
def register(request):
    """Yangi foydalanuvchi ro'yxatdan o'tish"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Prepare response data
        user_data = UserSerializer(user).data
        user_data['created_at'] = user.created_at.isoformat()

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):

    serializer = LoginSerializer(dataclasses=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'access_token':access_token,
            'refresh_token':refresh_token,
            'user':{
                'id':user.id,
                'full_name':user.full_name,
                'phone_number':user.phone_number

            }
        })
    return Response(
        {'detail':'Invalid phone number or password'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['PUT'])
@permission_classes([IsAuthonticated])
def update_profile(request):
    serializer = UserUpdateSerializer(request.user, data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        response_data = UserSerializer(user).data
        return Response(response_data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_profile(request):
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        response_data = UserSerializer(user).data
        return Response(response_data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def seller_registration(request):
    serializer = SellerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        seller_reg = serializer.save()

        return Response({
            'id': seller_reg.id,
            'full_name': seller_reg.full_name,
            'project_name': seller_reg.project_name,
            'category_id': seller_reg.category.id,
            'phone_number': seller_reg.phone_number,
            'address': seller_reg.address,
            'status': seller_reg.status
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def token_refresh(request):
    serializer = TokenRefreshSerializer(data=request.data)
    if serializer.is_valid():
        try:
            refresh_token = RefreshToken(serializer.validated_data['refresh_token'])
            access_token = str(refresh_token.access_token)

            return Response({
                'access_token': access_token
            })
        except TokenError:
            return Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def token_verify(request):
    serializer = TokenVerifySerializer(data=request.data)
    if serializer.is_valid():
        try:
            token = serializer.validated_data['token']
            return Response({
                'valid': True,
                'user_id': 123
            })
        except Exception:
            return Response(
                {'detail': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)