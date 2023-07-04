from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClientRegistrationSerialazer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import Client
from django.contrib.auth import logout


class ClientRegistrationView(APIView):
    """Регистрация пользователя"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientRegistrationSerialazer(data=request.data)
        if serializer.is_valid():
            client = serializer.create(serializer.validated_data)
            token = Token.objects.get_or_create(user=client)[0].key
            return Response({"message": "Вы успешно зарегестрированы",
                             "Ваш токен": token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientLoginView(APIView):
    """Логин пользователя и получения токена"""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = str(request.data.get("password"))
        try:
            user = Client.object.get(email=email)
        except BaseException:
            return Response({"ошибка": "Пользователь не найден!"}, status=400)
        token = Token.objects.get_or_create(user=user)[0].key

        if user.password == password:
            return Response({"Ваш токен": token})
        return Response({"ошибка": "неверные логин или пароль!"}, status=401)


class ClientLogoutView(APIView):
    """Логаут пользователя и удаление токена из базы"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
        try:
            Token.objects.get(key=token).delete()
        except Token.DoesNotExist:
            pass
        logout(request)
        return Response("Вы разлогинились!")
