from django.db import models


class Client(models.Model):
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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
