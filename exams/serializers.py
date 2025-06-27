from rest_framework import serializers

from courses.subjects.serializers import SubjectSerializer
from .models import Exam, Question, Choice, ExamAttempt, Answer
from courses.serializers import CourseSerializer

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'is_correct')

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'marks', 'order', 'choices')

class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    
    class Meta:
        model = Question
        fields = ('question_text', 'question_type', 'marks', 'order', 'choices')
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question

class ExamSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = '__all__'

class ExamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('title', 'description', 'duration', 'total_marks', 'passing_marks', 'examination_type', 'year',
                 'start_time', 'end_time', 'is_published', 'subject')

class StaffExamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ('title', 'description', 'duration', 'total_marks', 'passing_marks', 'examination_type', 'year',
                 'start_time', 'end_time', 'is_published')

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('question', 'answer_text')

class ExamAttemptSerializer(serializers.ModelSerializer):
    exam = serializers.PrimaryKeyRelatedField(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExamAttempt
        fields = ('id', 'exam', 'student', 'start_time', 'end_time', 'score',
                 'is_completed', 'answers')
        read_only_fields = ('student', 'score', 'is_completed')

class ExamSubmissionSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)
    
    def validate(self, data):
        attempt = self.context['attempt']
        exam = attempt.exam
        
        # Validate that all questions are answered
        answered_questions = set(answer['question'].id for answer in data['answers'])
        exam_questions = set(question.id for question in exam.questions.all())
        
        if answered_questions != exam_questions:
            raise serializers.ValidationError("All questions must be answered.")
        
        return data