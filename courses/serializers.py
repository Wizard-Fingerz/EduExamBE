from rest_framework import serializers
from .models import Course, CourseEnrollment, CourseRating, Module, Lesson, Assignment, AssignmentQuestion, AssignmentChoice, AssignmentSubmission, AssignmentAnswer
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
    enrollment_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('instructor', 'students')
    
    def get_enrollment_count(self, obj):
        return obj.students.count()
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return sum(rating.rating for rating in ratings) / len(ratings)
        return 0

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description', 'price', 'category', 'level', 'duration', 'thumbnail', 'is_published', 'passing_score')
    
    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = '__all__'

class CourseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRating
        fields = '__all__'

class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('title', 'description', 'order')

class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('title', 'content', 'video_url', 'duration', 'order')

# Assignment Serializers
class AssignmentChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentChoice
        fields = ('id', 'choice_text', 'is_correct')

class AssignmentQuestionSerializer(serializers.ModelSerializer):
    choices = AssignmentChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = AssignmentQuestion
        fields = ('id', 'question_text', 'question_type', 'points', 'order', 'choices')

class AssignmentQuestionCreateSerializer(serializers.ModelSerializer):
    choices = AssignmentChoiceSerializer(many=True, required=False)
    
    class Meta:
        model = AssignmentQuestion
        fields = ('question_text', 'question_type', 'points', 'order', 'choices')
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = AssignmentQuestion.objects.create(**validated_data)
        
        for choice_data in choices_data:
            AssignmentChoice.objects.create(question=question, **choice_data)
        
        return question
    
    def update(self, instance, validated_data):
        choices_data = validated_data.pop('choices', [])
        
        # Update question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update choices
        instance.choices.all().delete()
        for choice_data in choices_data:
            AssignmentChoice.objects.create(question=instance, **choice_data)
        
        return instance

class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    questions = AssignmentQuestionSerializer(many=True, read_only=True)
    submission_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = '__all__'
    
    def get_submission_count(self, obj):
        return obj.submissions.count()
    
    def get_average_score(self, obj):
        graded_submissions = obj.submissions.filter(is_graded=True)
        if graded_submissions:
            return sum(sub.score for sub in graded_submissions) / len(graded_submissions)
        return 0

class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'due_date', 'total_points', 'is_published')

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'

class AssignmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentAnswer
        fields = '__all__'

# Staff-specific serializers
class StaffAssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    questions = AssignmentQuestionSerializer(many=True, read_only=True)
    submission_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = '__all__'
    
    def get_submission_count(self, obj):
        return obj.submissions.count()
    
    def get_average_score(self, obj):
        graded_submissions = obj.submissions.filter(is_graded=True)
        if graded_submissions:
            return sum(sub.score for sub in graded_submissions) / len(graded_submissions)
        return 0

class StaffAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'due_date', 'total_points', 'is_published') 