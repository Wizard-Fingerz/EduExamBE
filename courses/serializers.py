from rest_framework import serializers
from .models import Course, Module, Lesson
from users.serializers import UserProfileSerializer

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserProfileSerializer(read_only=True)
    students = UserProfileSerializer(many=True, read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('instructor', 'students')

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description', 'thumbnail', 'price', 'is_published')
    
    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('title', 'description', 'order')

class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('title', 'content', 'video_url', 'duration', 'order') 