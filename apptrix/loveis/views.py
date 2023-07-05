from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ClientFilter
from .models import Client, Like
from .serializers import (ClientRegistrationSerialazer, ClientSerializer,
                          LikeSerializer)


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
        password = request.data.get("password")
        try:
            user = Client.objects.get(email=email)

        except BaseException:
            return Response({"ошибка": "Пользователь не найден!"}, status=400)
        token = Token.objects.get_or_create(user=user)[0].key

        if check_password(password, user.password):
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


class ClientMatchView(APIView):
    """Оценивание участников"""

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        sender = request.user
        receiver_id = id
        receiver = get_object_or_404(Client, id=receiver_id)
        if sender.id == receiver_id:
            return Response("Нельзя оценить самого себя")

        if Like.objects.filter(sender=sender, receiver=receiver).exists():
            return Response("Вы уже голосовали за этого участника")

        like_data = {
            "sender": sender.id,
            "receiver": receiver.id}

        serializer = LikeSerializer(data=like_data)

        if serializer.is_valid():
            serializer.save()
            # Проверка на взаимную симпатию
            if Like.objects.filter(sender=receiver, receiver=sender).exists():
                # Отправка сообщений на почту обоим участникам
                send_mail(
                    "Взаимная симпатия",
                    f"Вы понравились {receiver.first_name}! Почта участника: {receiver.email}",
                    "djangorest@yandex.ru",
                    [sender.email],
                    fail_silently=False
                )
                send_mail(
                    "Взаимная симпатия",
                    f"Вы понравились {sender.first_name}! Почта участника: {sender.email}",
                    "djangorest@yandex.ru",
                    [receiver.email],
                    fail_silently=False
                )
                return Response(f"Поздравляем, симпатия взаимна! Вот email партнера: {receiver.email}")
            return Response(f"Вы проявили симпатию к {receiver.first_name}")
        return Response("Ошибка", status=400)


class ClientListView(ListAPIView):

    permission_classes = [IsAuthenticated]

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ClientFilter
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["first_name", "last_name"]
