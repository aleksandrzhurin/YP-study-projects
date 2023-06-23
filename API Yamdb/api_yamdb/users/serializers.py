from rest_framework import serializers

from users.models import User
from api_yamdb.settings import (MAX_LENGTH_EMAIL,
                                MAX_LENGTH_USERNAME,
                                MAX_LENGTH_CODE)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError(
                'Email занят'
            )
        return data


class UserSignUpSerilizer(serializers.ModelSerializer):

    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True,
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError('me нельзя')

        if (User.objects.filter(email=data.get('email')).exists()
           and not User.objects.filter(
           username=data.get('username')).exists()):
            raise serializers.ValidationError(
                f'Email: {data.get("email")} занят'
            )
        if User.objects.filter(username=data.get('username')).exists():
            user = User.objects.get(username=data.get('username'))
            if user.email != data.get('email'):
                raise serializers.ValidationError(
                    f'Email:{data.get("email")}указан неверно'
                )

        return data


class UserTokenSerializer(serializers.Serializer):

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=MAX_LENGTH_CODE,
        required=True
    )
