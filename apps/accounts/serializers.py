from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Address
from store.models import Category

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["name", "lat", "long"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "phone_number",
            "profile_photo",
            "address",
            "created_time",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["full_name", "phone_number", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password, role="customer", status="approved", **validated_data
        )

        return user


class SellerRegistrationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "project_name",
            "category",
            "phone_number",
            "address",
            "status",
        ]
        extra_kwargs = {"status": {"read_only": True}}

    def create(self, validated_data):
        address_data = validated_data.pop("address")

        user = User.objects.create(
            role="seller", status="pending", is_active=False, **validated_data
        )
        Address.objects.create(user=user, **address_data)

        return user

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "full_name": instance.full_name,
            "project_name": instance.project_name,
            "category_id": instance.category.id if instance.category else None,
            "phone_number": instance.phone_number,
            "address": instance.address.name if hasattr(instance, 'address') and instance.address else None,
            "status": instance.status,
        }
        return data


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        if phone_number and password:
            user = authenticate(
                request=self.context.get("request"),
                username=phone_number,
                password=password,
            )

            if not user:
                raise serializers.ValidationError("Invalid phone number or password.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            attrs["user"] = user
            return attrs

        raise serializers.ValidationError("Must include phone number and password.")

    def to_representation(self, instance):
        user = instance["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
            }
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "phone_number", "profile_photo"]
        extra_kwargs = {"phone_number": {"required": False}}

    def update(self, instance, validated_data):
        phone_number = validated_data.get("phone_number")
        if phone_number and phone_number != instance.phone_number:
            if (
                    User.objects.filter(phone_number=phone_number)
                            .exclude(id=instance.id)
                            .exists()
            ):
                raise serializers.ValidationError(
                    {"phone_number": "This phone number is already in use."}
                )

        return super().update(instance, validated_data)


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh_token")

        try:
            token = RefreshToken(refresh_token)
            attrs["access_token"] = str(token.access_token)
            return attrs
        except Exception:
            raise serializers.ValidationError("Invalid refresh token.")


class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get("token")

        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            attrs["user_id"] = access_token.payload.get("user_id")
            attrs["valid"] = True
            return attrs
        except Exception:
            attrs["valid"] = False
            return attrs