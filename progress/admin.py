from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import CourseProgress, LessonProgress, ExamProgress

class CourseProgressResource(resources.ModelResource):
    class Meta:
        model = CourseProgress
        fields = ('id', 'student', 'course', 'completed_lessons', 'last_accessed_lesson',
                 'progress_percentage', 'is_completed', 'completed_at', 'created_at',
                 'updated_at')
        export_order = fields

class LessonProgressResource(resources.ModelResource):
    class Meta:
        model = LessonProgress
        fields = ('id', 'student', 'lesson', 'is_completed', 'completed_at',
                 'time_spent', 'last_position', 'created_at', 'updated_at')
        export_order = fields

class ExamProgressResource(resources.ModelResource):
    class Meta:
        model = ExamProgress
        fields = ('id', 'student', 'exam', 'best_score', 'last_attempt',
                 'created_at', 'updated_at')
        export_order = fields

@admin.register(CourseProgress)
class CourseProgressAdmin(ImportExportModelAdmin):
    resource_class = CourseProgressResource
    list_display = ('student', 'course', 'progress_percentage', 'is_completed')
    list_filter = ('is_completed', 'course')
    search_fields = ('student__username', 'course__title')
    ordering = ('-updated_at',)
    raw_id_fields = ('student', 'course', 'last_accessed_lesson')

@admin.register(LessonProgress)
class LessonProgressAdmin(ImportExportModelAdmin):
    resource_class = LessonProgressResource
    list_display = ('student', 'lesson', 'is_completed', 'time_spent')
    list_filter = ('is_completed', 'lesson__module__course')
    search_fields = ('student__username', 'lesson__title')
    ordering = ('-updated_at',)
    raw_id_fields = ('student', 'lesson')

@admin.register(ExamProgress)
class ExamProgressAdmin(ImportExportModelAdmin):
    resource_class = ExamProgressResource
    list_display = ('student', 'exam', 'best_score', 'last_attempt')
    list_filter = ('exam__subject',)
    search_fields = ('student__username', 'exam__title')
    ordering = ('-updated_at',)
    raw_id_fields = ('student', 'exam')
