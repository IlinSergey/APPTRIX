from rest_framework import serializers
from .models import Client, Like
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


class ClientRegistrationSerialazer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data):

        password = validated_data.pop("password")
        avatar = validated_data.pop("avatar", None)

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

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "gender", "email", "password", "avatar"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "first_name", "last_name", "avatar", "gender", "email"]