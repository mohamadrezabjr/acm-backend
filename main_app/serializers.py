from rest_framework import serializers
from auth_app.models import Person
from main_app.models import Event, Tag, Course, TimePlan
from auth_app.serializers import PersonSerializer, PersonGetOrCreateSerializer


class EventSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field= 'name'
    )
    speakers = PersonGetOrCreateSerializer(many=True, required=False)
    
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.url

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
        event.tags.set(tags)
        for speaker in speakers:
            user = speaker.get('user')
            if not user:
                person = Person.objects.create(position = speaker.get('position'), description = speaker.get('description'))
            else :
                person = Person.objects.filter(user = user).first()
            event.speakers.add(person)
        return event
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

    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.url

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