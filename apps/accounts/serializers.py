from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User,Address,SellerRegistration,Category

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['name','lat','long']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name','phone_number','password','password_confirm','address']


class  UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    address = AddressSerializer(required=False)

    class Meta:
        model = User
        fields = ['full_name','phone_number','password','password_confirm','address']

    def validate(self,attrs):
        if attrs ['password']  == attrs ['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self,validated_data):
        address_data = validated_data.pop('address,None')
        validated_data.pop('password_confirm')

        if address_data:
            address = Address.objects.create(**address_data)
            validated_data['address'] = address

        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number and password:
            user = authenticate(username=phone_number, password=password)
            if not user:
                raise serializers.ValidationError("Invalid phone number or password")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Must include phone number and password")

        return attrs
class UserUpdateSerializer(serializers.ModelSerializer):
    address = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ['full_name','phone_number','address']

    def update(self, instance, validated_data):
        address_id = validated_data.pop('address', None)

        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                instance.address = address
            except Address.DoesNotExist:
                pass

        return super().update(instance, validated_data)

class SellerRegistrationSerializer(serializers.ModelSerializer):
    address = serializers.JSONField()

    class Meta:
        model = SellerRegistration
        fields = ['full_name','project_name','category','phone_number','address']

    def create(self,validated_data):
        address_data = validated_data.pop('address')
        address_str = address_data.get('name','')
        validated_data['address'] = address_str

        return super().create(validated_data)

class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

