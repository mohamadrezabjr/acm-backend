from rest_framework import serializers
from auth_app.models import Person
from main_app.models import Event, Tag, Course, TimePlan
from auth_app.serializers import PersonSerializer, PersonGetOrCreateSerializer

class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()

    def create(self, validated_data):
        name = validated_data.get("name")
        tag = Tag.objects.filter(name=name).first()
        if not tag:
            tag = Tag.objects.create(name=name)
        return tag
class EventCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListSerializer(child=TagSerializer(), required=False)
    speakers = PersonGetOrCreateSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Event
        fields = [
            'title',
            'slug',
            'description',
            'tags',
            'start_date',
            'end_date',
            'registration_start_at',
            'registration_deadline',
            'capacity',
            'registered',
            'location',
            'price',
            'organizer',
            'image',
            'speakers'
        ]
    def create(self, validated_data):
        speakers = validated_data.pop('speakers')
        tags = validated_data.pop("tags")
        event = Event.objects.create(**validated_data)
        for tag in tags :
            tag_serializer = TagSerializer(data=tag)
            tag_serializer.is_valid(raise_exception=True)
            tag = tag_serializer.save()
            event.tags.add(tag)
        for speaker in speakers:
            person_serializer = PersonGetOrCreateSerializer(data=speaker)
            person_serializer.is_valid(raise_exception=True)
            person = person_serializer.save()
            event.speakers.add(person)
        return event

class EventListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        required=False,
        slug_field='name',
        many=True,
        queryset=Tag.objects.all(),
    )
    speakers = PersonGetOrCreateSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Event
        fields = [
            'title',
            'slug',
            'description',
            'tags',
            'start_date',
            'end_date',
            'registration_start_at',
            'registration_deadline',
            'capacity',
            'registered',
            'location',
            'price',
            'organizer',
            'image',
            'speakers'
        ]

class TimePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimePlan
        fields = [
            'weekday',
            'time_start',
            'time_end',
        ]
class CourseSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field= 'name'
    )
    instructors = PersonGetOrCreateSerializer(many=True, required=False)
    time_plans = TimePlanSerializer(many=True, required=False)

    image = serializers.SerializerMethodField(required = False)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    class Meta:
        model = Course
        fields = [
            'title',
            'slug',
            'description',
            'tags',
            'start_date',
            'end_date',
            'registration_start_at',
            'registration_deadline',
            'capacity',
            'registered',
            'location',
            'price',
            'organizer',
            'image',
            'instructors',
            'time_plans'
        ]
    def create(self, validated_data):
        time_plans = validated_data.pop('time_plans')
        course = Course.objcts.create(**validated_data)
        if time_plans:
            serializer = TimePlanSerializer(data = time_plans, many=True)
            if serializer.is_valid():
                serializer.save()
                course.time_plans.set(serializer.data)
            else:
                raise serializers.ValidationError(serializer.errors)
        return course