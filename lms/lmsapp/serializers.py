from rest_framework import serializers
from .models import *
from authapp.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseCategory.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'instructor',
            'category',
            'category_id',
            'is_published',
            'created_at'
        ]

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'is_published']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['instructor'] = request.user
        return super().create(validated_data)
    
class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['course']

    def validate(self, data):
        request = self.context['request']
        if Enrollment.objects.filter(student=request.user, course=data['course']).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        return data

    def create(self, validated_data):
        request = self.context['request']
        return Enrollment.objects.create(
            student=request.user,
            course=validated_data['course']
        )
    
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'content', 'video_url', 'order']