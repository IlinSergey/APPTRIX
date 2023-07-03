from rest_framework import serializers
from .models import Client


class ClientRegistrationSerialazer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "avatar", "gender", "email", "password"]

        def create(self, validated_data):
            password = validated_data.pop("password")
            client = Client.objects.create_user(
                password=password,
                **validated_data
            )
            client.set_password(password)
            client.save()
            return client
