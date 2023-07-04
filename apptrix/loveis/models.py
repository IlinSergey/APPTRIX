from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class ClientManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email должен быть обязательно введен!")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)


class Client(AbstractBaseUser, PermissionsMixin):
    """Участники"""
    gender_choices = (
        ("male", "мужской"),
        ("female", "женский")
    )

    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    gender = models.CharField("Пол", max_length=6, choices=gender_choices)
    email = models.EmailField("E-mail", unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = ClientManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Like(models.Model):
    """Оценки пользователей"""

    sender = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="Оценивающий")
    receiver = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="Оцениваемый")

    class Meta:
        unique_together = ("sender", "receiver")
