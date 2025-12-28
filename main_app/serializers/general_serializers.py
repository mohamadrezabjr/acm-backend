from rest_framework import serializers
from main_app.models import Tag

class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        name = validated_data.get("name")
        tag = Tag.objects.filter(name=name).first()
        if not tag:
            tag = Tag.objects.create(name=name)
        return tag

