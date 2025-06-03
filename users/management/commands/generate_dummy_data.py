from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker
from courses.models import Course, Module, Lesson
from exams.models import Exam, Question, Choice, ExamAttempt, Answer
from progress.models import CourseProgress, LessonProgress, ExamProgress

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generates dummy data for all models'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating dummy data...')
        
        # Create users
        self.create_users()
        
        # Create courses and related data
        self.create_courses()
        
        # Create exams and related data
        self.create_exams()
        
        # Create progress data
        self.create_progress_data()
        
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))

    def create_users(self):
        # Create admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )

        # Create teachers
        teachers = []
        for i in range(5):
            username = f'teacher{i+1}'
            if not User.objects.filter(username=username).exists():
                teacher = User.objects.create_user(
                    username=username,
                    email=f'teacher{i+1}@example.com',
                    password='teacher123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='teacher',
                    bio=fake.text(),
                    phone_number=fake.phone_number(),
                    address=fake.address()
                )
                teachers.append(teacher)
            else:
                teachers.append(User.objects.get(username=username))

        # Create students
        students = []
        for i in range(10):
            username = f'student{i+1}'
            if not User.objects.filter(username=username).exists():
                student = User.objects.create_user(
                    username=username,
                    email=f'student{i+1}@example.com',
                    password='student123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='student',
                    bio=fake.text(),
                    phone_number=fake.phone_number(),
                    address=fake.address()
                )
                students.append(student)
            else:
                students.append(User.objects.get(username=username))

        return teachers, students

    def create_courses(self):
        teachers = User.objects.filter(user_type='teacher')
        students = User.objects.filter(user_type='student')

        # Create courses
        courses = []
        for i in range(5):
            course = Course.objects.create(
                title=f'Course {i+1}: {fake.catch_phrase()}',
                description=fake.text(),
                instructor=random.choice(teachers),
                price=random.randint(0, 100),
                is_published=True
            )
            courses.append(course)

            # Add some students to each course
            course.students.add(*random.sample(list(students), k=random.randint(3, 8)))

            # Create modules for each course
            for j in range(random.randint(3, 5)):
                module = Module.objects.create(
                    course=course,
                    title=f'Module {j+1}: {fake.catch_phrase()}',
                    description=fake.text(),
                    order=j+1
                )

                # Create lessons for each module
                for k in range(random.randint(3, 5)):
                    Lesson.objects.create(
                        module=module,
                        title=f'Lesson {k+1}: {fake.catch_phrase()}',
                        content=fake.text(),
                        video_url=f'https://example.com/video/{fake.uuid4()}',
                        duration=timedelta(minutes=random.randint(5, 60)),
                        order=k+1
                    )

        return courses

    def create_exams(self):
        courses = Course.objects.all()
        students = User.objects.filter(user_type='student')

        # Create exams
        for course in courses:
            for i in range(2):  # 2 exams per course
                exam = Exam.objects.create(
                    course=course,
                    title=f'Exam {i+1} for {course.title}',
                    description=fake.text(),
                    duration=timedelta(minutes=random.randint(30, 120)),
                    total_marks=100,
                    passing_marks=40,
                    start_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                    end_time=timezone.now() + timedelta(days=random.randint(31, 60)),
                    is_published=True
                )

                # Create questions for each exam
                for j in range(10):  # 10 questions per exam
                    question = Question.objects.create(
                        exam=exam,
                        question_text=fake.sentence(),
                        question_type='multiple_choice',
                        marks=10,
                        order=j+1
                    )

                    # Create choices for each question
                    correct_choice = random.randint(0, 3)
                    for k in range(4):
                        Choice.objects.create(
                            question=question,
                            choice_text=fake.sentence(),
                            is_correct=(k == correct_choice)
                        )

                # Create exam attempts for some students
                for student in random.sample(list(students), k=random.randint(3, 8)):
                    attempt = ExamAttempt.objects.create(
                        exam=exam,
                        student=student,
                        start_time=timezone.now() - timedelta(hours=random.randint(1, 24)),
                        end_time=timezone.now(),
                        score=random.randint(0, 100),
                        is_completed=True
                    )

                    # Create answers for each attempt
                    for question in exam.questions.all():
                        Answer.objects.create(
                            attempt=attempt,
                            question=question,
                            answer_text=random.choice(question.choices.all()).choice_text,
                            marks_obtained=random.randint(0, question.marks)
                        )

    def create_progress_data(self):
        courses = Course.objects.all()
        students = User.objects.filter(user_type='student')

        for course in courses:
            for student in course.students.all():
                # Create course progress
                course_progress, created = CourseProgress.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={
                        'progress_percentage': random.randint(0, 100),
                        'is_completed': random.choice([True, False])
                    }
                )

                # Create lesson progress for each lesson in the course
                for module in course.modules.all():
                    for lesson in module.lessons.all():
                        LessonProgress.objects.create(
                            student=student,
                            lesson=lesson,
                            is_completed=random.choice([True, False]),
                            time_spent=timedelta(minutes=random.randint(0, lesson.duration.total_seconds() // 60)),
                            last_position=random.randint(0, 100)
                        )

                # Create exam progress for each exam in the course
                for exam in course.exams.all():
                    # Get the latest ExamAttempt for this student and exam, if any
                    last_attempt = ExamAttempt.objects.filter(student=student, exam=exam).order_by('-end_time').first()
                    ExamProgress.objects.create(
                        student=student,
                        exam=exam,
                        best_score=random.randint(0, 100),
                        last_attempt=last_attempt
                    ) 