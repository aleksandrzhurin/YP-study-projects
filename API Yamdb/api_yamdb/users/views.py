from random import randint

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, action
from rest_framework import status, viewsets, permissions, filters

from users.models import User
from users.serializers import (
    UserTokenSerializer,
    UserSerializer,
    UserSignUpSerilizer,
)

from api.permissions import (AdminOrSuperUser,)


@api_view(['POST'])
def get_token(request):
    serializer = UserTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)

    if confirmation_code != str(user.confirmation_code):
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    token = RefreshToken.for_user(user)
    return Response({'token': str(token.access_token)},
                    status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOrSuperUser,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)

    http_method_names = ('get', 'post', 'delete', 'patch')

    @action(detail=False,
            url_path='me',
            methods=('GET', 'PATCH',),
            permission_classes=(permissions.IsAuthenticated, ))
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                role=user.role
            )
            return Response(serializer.data)

        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserSignUp(APIView):
    def post(self, request):
        serializer = UserSignUpSerilizer(data=request.data)
        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            return Response(request.data)

        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user, _ = User.objects.get_or_create(
            username=username,
            email=email
        )
        confirmation_code = randint(1000, 9999)
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            'Subject here',
            f'Твой код подтверждения: {confirmation_code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        return Response({'email': serializer.validated_data['email'],
                         'username': serializer.validated_data['username']},
                        status=status.HTTP_200_OK)
