from rest_framework import serializers
from .models import CustomUser
from .models import UploadImage


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImage
        # fields = "__all__",
        exclude = ('id',)


# user signup model serialzer
class CustomUserRegistrationModelSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        # password = attrs.get('password')
        # password2 = attrs.get('password2')

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password does not match")
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


# login user serializer
class CustomUserLoginModelSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

