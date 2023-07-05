import os
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from rest_framework import serializers
from geopy.geocoders import Nominatim

from .models import Client, Like


class ClientRegistrationSerialazer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "gender", "email", "password", "avatar", "address", "latitude", "longitude"]

        read_only_fields = ["latitude", "longitude"]

    def create(self, validated_data):
        address = validated_data.pop("address", None)
        password = validated_data.pop("password")
        avatar = validated_data.pop("avatar", None)

        geolocator = Nominatim(user_agent="apptrix")
        location = geolocator.geocode(address)  # Получаем координаты по адресу

        if location:
            validated_data["latitude"] = round(location.latitude, 6)
            validated_data["longitude"] = round(location.longitude, 6)
        validated_data["address"] = address
        client = Client.objects.create_user(
            password=password,
            **validated_data
        )

        if avatar:
            avatar_with_watermark = self.watermark(avatar)
            client.avatar = avatar_with_watermark
            client.save()
        return client

    def watermark(self, photo):
        """Добавление водяного знака на аватар"""

        image = Image.open(photo).convert("RGBA")

        watermark_path = os.path.join(os.path.dirname(__file__), "..", "utils/watermark.png")
        watermark = Image.open(watermark_path).convert("RGBA")

        watermark_size = (image.width // 4, image.height // 4)
        watermark = watermark.resize(watermark_size)

        watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        watermark_position = (image.width - watermark.width, image.height - watermark.height)

        watermark_layer.paste(watermark, watermark_position, mask=watermark)
        processed_avatar = Image.alpha_composite(image.convert("RGBA"), watermark_layer)

        output = BytesIO()
        processed_avatar.save(output, format='PNG')
        output.seek(0)

        processed_avatar = InMemoryUploadedFile(
            output,
            None,
            photo.name,
            'image/png',
            output.getbuffer().nbytes,
            None
        )

        return processed_avatar


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "first_name", "last_name", "avatar", "gender"]


class LikeSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    sender_details = ClientSerializer(source="sender", read_only=True)
    receiver_details = ClientSerializer(source="receiver", read_only=True)

    class Meta:
        model = Like
        fields = "__all__"
